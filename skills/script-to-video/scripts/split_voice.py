"""Split one long narration recording into one file per beat, cutting at the longest pauses (free).

Record the script in one go with a clear pause (about a second) between beat lines; this cuts at the N-1 longest
pauses, trims silence, and writes voice/01.wav, 02.wav ... Listen to the result: if a cut is wrong, re-record with
longer pauses or pass --min-pause lower/higher.

usage: split_voice.py RECORDING --beats N --out voice/ [--min-pause 0.35]
"""
import os, sys, argparse
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import decode_audio, write_wav, SR


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("recording"); ap.add_argument("--beats", type=int, required=True); ap.add_argument("--out", default="voice")
    ap.add_argument("--min-pause", type=float, default=0.35)
    A = ap.parse_args()
    x = decode_audio(A.recording)
    hop = int(0.02 * SR)
    fr = x.mean(1)[:len(x) // hop * hop].reshape(-1, hop)
    db = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9)
    thr = min(-40.0, db.max() - 30)
    loud = db > thr
    runs, i = [], 0
    while i < len(loud):
        if not loud[i]:
            j = i
            while j < len(loud) and not loud[j]:
                j += 1
            if i > 0 and j < len(loud) and (j - i) * 0.02 >= A.min_pause:
                runs.append(((j - i) * 0.02, i, j))
            i = j
        else:
            i += 1
    if len(runs) < A.beats - 1:
        sys.exit(f"found only {len(runs) + 1} parts; need {A.beats}. Re-record with longer pauses or lower --min-pause.")
    cuts = sorted(runs, reverse=True)[:A.beats - 1]
    bounds = [0] + sorted((i + j) // 2 for _, i, j in cuts) + [len(loud)]
    os.makedirs(A.out, exist_ok=True)
    for k in range(A.beats):
        a, b = bounds[k], bounds[k + 1]
        seg = np.nonzero(loud[a:b])[0]
        s = max(a + seg[0] - 3, a) * hop; e = min(a + seg[-1] + 6, b) * hop      # keep 60 ms before, 120 ms after
        p = os.path.join(A.out, f"{k + 1:02d}.wav")
        write_wav(p, x[s:e])
        print(f"{p}: {(e - s) / SR:.2f}s")


if __name__ == "__main__":
    main()
