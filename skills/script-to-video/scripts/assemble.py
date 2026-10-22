"""Assemble the finished video from a shot list (free, local).

1. Builds every beat's picture track (build_beat.py), joins them losslessly.
2. Builds ONE audio track in memory, sample-exact (no per-beat AAC drift):
     voice lines at beat start + voice_at
     clip ambience (from animated clips that carry sound), levelled to ambience_db
     sound effects (explicit + automatic), at sfx_db
     music, looped/cross-faded to length, ducked under the voice by duck_db
3. Normalises to the target loudness (two-pass EBU R128) and muxes with a single AAC encode.
4. Writes captions.srt from each beat's "line" and the measured speech.

usage: assemble.py SHOTLIST.json OUT.mp4 [--preview] [--jobs 3] [--reuse]
  --preview  animatic check: no music (unless --music-anyway), same picture and text track
  --reuse    keep beat files already built (only rebuild missing ones)
"""
import sys, os, json, argparse, subprocess, concurrent.futures as cf
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_shotlist, decode_audio, write_wav, speech_bounds, rms_db, has_audio, SR, FFMPEG, voice_plan, span_seconds
import build_beat, sfx as SFX


def place(track, x, at):
    i = int(round(at * SR))
    if i >= len(track):
        return
    n = min(len(x), len(track) - i)
    track[i:i + n] += x[:n]


def music_bed(S, total):
    tracks = [decode_audio(m["file"]) for m in S.get("music") or []]
    if not tracks:
        return None
    xf = int(2.0 * SR)
    out = np.zeros((0, 2), np.float32)
    k = 0
    while len(out) < total * SR + xf:
        t = tracks[k % len(tracks)].copy(); k += 1
        if len(out) == 0:
            out = t
        else:
            ramp = np.linspace(0, 1, xf, dtype=np.float32)[:, None]
            head = out[:-xf]; tail = out[-xf:] * (1 - ramp) + t[:xf] * ramp
            out = np.concatenate([head, tail, t[xf:]])
    n = int(round(total * SR))
    out = out[:n]
    fi, fo = int(0.5 * SR), int(min(2.5, total / 4) * SR)
    out[:fi] *= np.linspace(0, 1, fi)[:, None]
    out[-fo:] *= np.linspace(1, 0, fo)[:, None]
    return out


def duck_gain(voice, duck_db, thr=0.015):
    """Smooth gain curve: music drops by duck_db wherever the voice is present (attack 20 ms, release 400 ms)."""
    hop = int(0.01 * SR)
    mono = np.abs(voice.mean(1))
    fr = mono[:len(mono) // hop * hop].reshape(-1, hop).max(1)
    env = np.zeros_like(fr); e = 0.0
    a_att, a_rel = np.exp(-1 / 2.0), np.exp(-1 / 40.0)
    for i, v in enumerate(fr):
        e = a_att * e + (1 - a_att) * v if v > e else a_rel * e + (1 - a_rel) * v
        env[i] = e
    amt = np.clip(env / thr, 0, 1)
    g = 10 ** (-duck_db * amt / 20)
    g = np.repeat(g, hop)
    return np.pad(g, (0, len(voice) - len(g)), mode="edge")[:, None].astype(np.float32)


def loudnorm(inp, out, target, tp=-1.5):
    r = subprocess.run([FFMPEG, "-hide_banner", "-i", inp, "-af", f"loudnorm=I={target}:TP={tp}:LRA=11:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True).stderr
    m = json.loads(r[r.rfind("{"):r.rfind("}") + 1])
    af = (f"loudnorm=I={target}:TP={tp}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", inp, "-af", af + ",aresample=48000", "-c:a", "pcm_s16le", out], check=True)


def srt_time(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shotlist"); ap.add_argument("out")
    ap.add_argument("--preview", action="store_true"); ap.add_argument("--music-anyway", action="store_true")
    ap.add_argument("--jobs", type=int, default=3); ap.add_argument("--reuse", action="store_true")
    A = ap.parse_args()
    S = load_shotlist(A.shotlist)
    work = os.path.join(S["_root"], "_work"); bdir = os.path.join(work, "beats"); os.makedirs(bdir, exist_ok=True)
    total = S["_total"]

    # 1. picture track
    def one(b):
        p = os.path.join(bdir, f"beat{b['id']:03d}.mp4")
        if not (A.reuse and os.path.exists(p)):
            build_beat.build(S, b["id"], p)
        return p
    with cf.ThreadPoolExecutor(max_workers=A.jobs) as ex:
        paths = list(ex.map(one, S["beats"]))
    lst = os.path.join(work, "beats.txt")
    open(lst, "w").write("\n".join(f"file '{p}'" for p in paths))
    video = os.path.join(work, "video.mp4")
    subprocess.run([FFMPEG, "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", video], check=True)

    # 2. audio track
    n = int(round(total * SR))
    voice, amb, fx = (np.zeros((n, 2), np.float32) for _ in range(3))
    timeline = []
    for bi, b in enumerate(S["beats"]):
        rec = {"id": b["id"], "start": b["_start"], "seconds": b["seconds"], "voice": None, "lines": []}
        plan = voice_plan(b)                      # one narrator file, or several dialogue lines in turn
        span = span_seconds(S, bi)                # the line may run on into following "continues" pictures
        for f, start, on, end, speaker, text in plan:
            v = decode_audio(f)
            room = span - start
            if len(v) > room * SR:
                print(f"WARNING beat {b['id']}: a line runs past the end of the beat ({start + len(v)/SR:.2f}s > {span:.2f}s); it will be cut")
                v = v[:int(room * SR)]
            place(voice, v, b["_start"] + start)
            rec["lines"].append({"speaker": speaker, "text": text, "on": round(on, 3), "end": round(end, 3)})
        if plan:
            rec["voice"] = [round(plan[0][2], 3), round(plan[-1][3], 3)]
        # clip_audio: "ambience" (default: levelled to ambience_db under everything), "full" (own footage with
        # real sound/dialogue, kept at its own level and treated like voice for ducking), "off"
        mode = b.get("clip_audio", "ambience")
        if b.get("clip") and mode != "off" and has_audio(b["clip"]):
            a = decode_audio(b["clip"])
            a = a[int(b.get("clip_start", 0) * SR):][:int(b["seconds"] * SR)]
            if mode == "full":
                place(voice, a, b["_start"])
            elif rms_db(a) > -70:
                a *= 10 ** ((S["ambience_db"] - rms_db(a)) / 20)
                f = int(0.06 * SR)
                a[:f] *= np.linspace(0, 1, f)[:, None]; a[-f:] *= np.linspace(1, 0, f)[:, None]
                place(amb, a, b["_start"])
        cues = list(b.get("sfx", []))
        if S["auto_sfx"] and not b.get("no_auto_sfx"):
            cues += SFX.auto_cues(b)
        for c in cues:
            s = SFX.make(c["sound"], c.get("note")) * 10 ** (c.get("db", 0) / 20)
            place(fx, np.repeat(s[:, None], 2, 1), b["_start"] + c["at"])
        timeline.append(rec)
    if np.abs(fx).max() > 0:
        fx = fx / np.abs(fx).max() * 10 ** ((-12 + S["sfx_db"]) / 20)      # effects peak 12 dB + sfx_db below full scale
    mix = voice + amb + fx
    use_music = (not A.preview) or A.music_anyway
    bed = music_bed(S, total) if use_music else None
    if bed is not None:
        # music_db is relative to the voice: -14 means the bed sits 14 dB under the speech, then ducks duck_db more
        loud = np.abs(voice.mean(1)) > 0.01
        v_db = rms_db(voice[loud]) if loud.any() else -20.0
        bed = bed * 10 ** ((v_db + S["music_db"] - rms_db(bed)) / 20)
        bed = bed * duck_gain(voice, S["duck_db"])
        mix += bed
    if not A.preview:                             # separate tracks for editing in CapCut / Premiere / DaVinci
        sd = os.path.join(S["_root"], "stems"); os.makedirs(sd, exist_ok=True)
        for name, x in (("voice", voice), ("effects", fx), ("room-sound", amb), ("music", bed)):
            if x is not None and np.abs(x).max() > 0:
                write_wav(os.path.join(sd, f"{name}.wav"), x)
    raw = os.path.join(work, "mix.wav"); norm = os.path.join(work, "mix-norm.wav")
    peak = np.abs(mix).max()
    write_wav(raw, mix / peak * 0.9 if peak > 0.9 else mix)
    loudnorm(raw, norm, S["loudness"])

    # 3. mux
    subprocess.run([FFMPEG, "-v", "error", "-y", "-i", video, "-i", norm, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", "-t", f"{total:.3f}", A.out], check=True)

    # 4. captions + timeline
    srt = []
    names = {c.get("id"): c.get("name", c.get("id")) for c in S.get("cast", [])}
    multi = len({ln["speaker"] for r in timeline for ln in r["lines"] if ln["speaker"]}) > 1
    for b, rec in zip(S["beats"], timeline):
        for ln in rec["lines"]:
            if not ln["text"]:
                continue
            who = f"{names.get(ln['speaker'], ln['speaker'])}: " if multi and ln["speaker"] else ""
            srt.append([b['_start'] + ln['on'], b['_start'] + ln['end'] + 0.3, f"{who}{ln['text']}"])
    for a, z in zip(srt, srt[1:]):            # never let a subtitle overlap the next one
        a[1] = min(a[1], z[0] - 0.02)
    srt = [f"{i}\n{srt_time(a)} --> {srt_time(z)}\n{t}\n" for i, (a, z, t) in enumerate(srt, 1)]
    base = os.path.splitext(A.out)[0]
    if srt:
        open(base + ".srt", "w").write("\n".join(srt))
    json.dump({"total": total, "beats": timeline}, open(os.path.join(work, "timeline.json"), "w"), indent=1)
    chapters = [(b["_start"], b["chapter"]) for b in S["beats"] if b.get("chapter")]
    if chapters:
        if chapters[0][0] > 0:
            chapters.insert(0, (0.0, "Intro"))
        txt = "\n".join(f"{int(t // 60):02d}:{int(t % 60):02d} {name}" for t, name in chapters)
        open(os.path.join(work, "chapters.txt"), "w").write(txt + "\n")
        print("chapters:\n" + txt)
    print(f"{A.out}  {total:.2f}s  {'preview (no music)' if A.preview and not A.music_anyway else 'final mix'}")


if __name__ == "__main__":
    main()
