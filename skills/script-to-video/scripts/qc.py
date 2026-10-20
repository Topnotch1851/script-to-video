"""Final check of an assembled video against its shot list (free). Run after assemble.py.

Checks: video and audio length match the plan; every beat's speech starts on time and ends inside the beat
(beats with "answer_gap" keep that much silence at the end); integrated loudness near target; true peak.
Writes qc/contact.png: one frame from the middle of every beat plus a frame after every text change,
so spelling and colours can be checked letter by letter.

usage: qc.py SHOTLIST.json VIDEO.mp4
"""
import os, sys, json, subprocess
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_shotlist, probe_duration, FFMPEG
from overlay import change_times


def loudness(path):
    r = subprocess.run([FFMPEG, "-hide_banner", "-i", path, "-af", "loudnorm=print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True).stderr
    m = json.loads(r[r.rfind("{"):r.rfind("}") + 1])
    return float(m["input_i"]), float(m["input_tp"])


def main():
    S = load_shotlist(sys.argv[1]); video = sys.argv[2]
    tl = json.load(open(os.path.join(S["_root"], "_work", "timeline.json")))
    problems = []
    dv, da = probe_duration(video, "v:0"), probe_duration(video, "a:0")
    print(f"planned {S['_total']:.2f}s | video {dv:.2f}s | audio {da:.2f}s")
    if abs(dv - S["_total"]) > 0.1 or abs(da - S["_total"]) > 0.1:
        problems.append("length mismatch")
    for b, rec in zip(S["beats"], tl["beats"]):
        if not b.get("voice"):
            continue
        if not rec["voice"]:
            problems.append(f"beat {b['id']}: voice file is silent"); continue
        on, end = rec["voice"]
        gap = b.get("answer_gap", 0.4)
        ok_on = on - b["voice_at"] <= 0.3
        ok_end = end <= b["seconds"] - gap
        flag = "" if ok_on and ok_end else "  <-- " + ("late start " if not ok_on else "") + ("too long " if not ok_end else "")
        print(f"beat {b['id']:3d}: speech {on:.2f}-{end:.2f}s of {b['seconds']:.2f}s (needs end <= {b['seconds'] - gap:.2f}){flag}")
        if flag:
            problems.append(f"beat {b['id']}:{flag.strip(' <-')}")
    I, TP = loudness(video)
    print(f"loudness {I:.1f} LUFS (target {S['loudness']}), true peak {TP:.1f} dBTP")
    if abs(I - S["loudness"]) > 1.0:
        problems.append(f"loudness {I:.1f} LUFS")
    if TP > -0.5:
        problems.append(f"true peak {TP:.1f} dBTP")
    # contact sheet
    qc = os.path.join(S["_root"], "qc"); os.makedirs(qc, exist_ok=True)
    shots = []
    for b in S["beats"]:
        ts = sorted({b["seconds"] / 2} | {t + 0.15 for t in change_times(b) if t > 0})
        for t in ts:
            shots.append((b["id"], round(b["_start"] + t, 2)))
    W, H = S["_fmt"]["W"], S["_fmt"]["H"]
    tw = 180 if H > W else 300; th = round(tw * H / W)
    tiles = []
    for bid, t in shots:
        p = os.path.join(qc, f"f_{t:.2f}.png")
        subprocess.run([FFMPEG, "-v", "error", "-y", "-ss", str(t), "-i", video, "-frames:v", "1", p], check=True)
        im = Image.open(p).resize((tw, th)); ImageDraw.Draw(im).text((4, 4), f"b{bid} {t:.2f}s", fill=(255, 40, 40))
        tiles.append(im)
    cols = 8 if H > W else 5
    sheet = Image.new("RGB", (cols * tw, ((len(tiles) + cols - 1) // cols) * th), (0, 0, 0))
    for i, im in enumerate(tiles):
        sheet.paste(im, ((i % cols) * tw, (i // cols) * th))
    sheet.save(os.path.join(qc, "contact.png"))
    print(f"contact sheet: {os.path.join(qc, 'contact.png')} ({len(tiles)} frames)")
    print("PASS" if not problems else "PROBLEMS: " + "; ".join(problems))
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
