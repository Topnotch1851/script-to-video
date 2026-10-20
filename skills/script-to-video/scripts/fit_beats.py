"""Time every beat to its narration (free). Run after the voice lines exist, before pictures/clips are made.

For each beat with a voice file: seconds = voice_at + measured speech end + tail (+ answer_gap if set),
never shorter than --min, rounded up to --step. Beats without voice keep their length.
Also reports total length and lines that are too long for a single picture (consider splitting them).

usage: fit_beats.py SHOTLIST.json [--min 5] [--max 12] [--tail 0.6] [--step 0.5] [--dry-run]
"""
import os, sys, json, math, argparse
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_shotlist, decode_audio, speech_bounds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shotlist"); ap.add_argument("--min", type=float, default=5.0); ap.add_argument("--max", type=float, default=12.0)
    ap.add_argument("--tail", type=float, default=0.6); ap.add_argument("--step", type=float, default=0.5)
    ap.add_argument("--dry-run", action="store_true")
    A = ap.parse_args()
    S = load_shotlist(A.shotlist)
    raw = json.load(open(A.shotlist))
    total = 0.0
    for b, r in zip(S["beats"], raw["beats"]):
        if b.get("voice") and os.path.exists(b["voice"]):
            on, end = speech_bounds(decode_audio(b["voice"]))
            if end is None:
                print(f"beat {b['id']}: voice is silent"); total += b["seconds"]; continue
            need = b["voice_at"] + end + max(A.tail, b.get("answer_gap", 0))
            sec = max(A.min, math.ceil(need / A.step) * A.step)
            flag = "  <-- long line: split it across two pictures" if sec > A.max else ""
            print(f"beat {b['id']:3d}: speech ends {end:.2f}s -> {sec:.1f}s{flag}")
            r["seconds"] = sec
        total += r.get("seconds", b["seconds"])
    print(f"total {total:.1f}s ({total / 60:.1f} min), {len(S['beats'])} beats")
    if not A.dry_run:
        json.dump(raw, open(A.shotlist, "w"), indent=1)
        print(f"updated {A.shotlist}")


if __name__ == "__main__":
    main()
