"""Render the picture track of one beat (no audio): background + timed text overlays.

Background, in order of preference:
  clip     an animated clip (AI or your own footage): scaled to cover the frame, held on its last frame if short
  picture  a still: slow camera move rendered here for free ("move": zoom-in|zoom-out|pan-left|pan-right|pan-up|pan-down|none)
  color    a flat colour for text-only beats
usage: build_beat.py SHOTLIST.json BEAT_ID OUT.mp4
"""
import sys, os, math, subprocess
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_shotlist, rgb, FFMPEG
from overlay import Renderer


def ease(k):
    return k * k * (3 - 2 * k)


def still_frames(pic, W, H, frames, move, amount):
    """Yield RGB frames of a slow, sub-pixel-smooth camera move over a still picture."""
    src = Image.open(pic).convert("RGB")
    s0 = max(W / src.width, H / src.height)
    pre = min(1.0, s0 * (1 + amount) * 1.15)          # shrink very large sources first (speed); keep detail
    if pre < 1.0:
        src = src.resize((round(src.width * pre), round(src.height * pre)), Image.LANCZOS)
        s0 = s0 / pre
    iw, ih = src.size
    for i in range(frames):
        k = ease(i / max(1, frames - 1))
        if move == "zoom-in":
            z, px, py = 1 + amount * k, 0.5, 0.5
        elif move == "zoom-out":
            z, px, py = 1 + amount * (1 - k), 0.5, 0.5
        elif move in ("pan-left", "pan-right", "pan-up", "pan-down"):
            z = 1 + amount
            d = (k - 0.5) if move in ("pan-left", "pan-up") else (0.5 - k)
            px = 0.5 - d * amount / z if "left" in move or "right" in move else 0.5
            py = 0.5 - d * amount / z if "up" in move or "down" in move else 0.5
        else:
            z, px, py = 1.0, 0.5, 0.5
        sc = s0 * z
        a = 1 / sc
        cx, cy = iw * px, ih * py
        # keep the crop inside the picture
        hw, hh = W / 2 * a, H / 2 * a
        cx = min(max(cx, hw), iw - hw); cy = min(max(cy, hh), ih - hh)
        data = (a, 0, cx - W / 2 * a, 0, a, cy - H / 2 * a)
        yield src.transform((W, H), Image.AFFINE, data, resample=Image.BICUBIC).tobytes()


def build(S, bid, out):
    beat = next(b for b in S["beats"] if str(b["id"]) == str(bid))
    W, H, fps, N, D = S["_fmt"]["W"], S["_fmt"]["H"], S["fps"], beat["_frames"], beat["seconds"]
    work = os.path.join(S["_root"], "_work", "overlays")
    segs = Renderer(S).timeline(beat, work)
    pipe_frames = None
    if beat.get("clip"):
        # loop: generated clips start and end on the same picture, so they repeat seamlessly; hold: freeze last frame (own footage)
        fit = beat.get("clip_fit", "loop")
        vin = (["-stream_loop", "-1"] if fit == "loop" else []) + ["-i", beat["clip"]]
        hold = f"tpad=stop_mode=clone:stop_duration={D}," if fit != "loop" else ""
        start = beat.get("clip_start", 0)
        bg = (f"[0:v]trim=start={start},setpts=PTS-STARTPTS,fps={fps},scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos,"
              f"crop={W}:{H},setsar=1,{hold}trim=end_frame={N},setpts=PTS-STARTPTS[bg]")
    elif beat.get("picture"):
        vin = ["-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-"]
        bg = "[0:v]setsar=1[bg]"
        pipe_frames = still_frames(beat["picture"], W, H, N, beat.get("move", "zoom-in"), beat.get("move_amount", 0.08))
    else:
        c = "%02x%02x%02x" % rgb(beat.get("color", S["colors"].get("card")), S["colors"])
        vin = ["-f", "lavfi", "-i", f"color=c=0x{c}:s={W}x{H}:r={fps}:d={D}"]
        bg = "[0:v]setsar=1[bg]"
    ins, fc, prev = [], [bg], "bg"
    for i, (a, b, png) in enumerate(segs):
        ins += ["-loop", "1", "-framerate", str(fps), "-t", f"{D}", "-i", png]
        nxt = f"v{i}"
        fc.append(f"[{prev}][{i + 1}:v]overlay=0:0:format=auto:enable='between(t,{a:.4f},{b - 1e-4:.4f})'[{nxt}]")
        prev = nxt
    fc.append(f"[{prev}]format=yuv420p[v]")
    cmd = [FFMPEG, "-v", "error", "-y", *vin, *ins, "-filter_complex", ";".join(fc), "-map", "[v]", "-an",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-r", str(fps), "-frames:v", str(N), out]
    if pipe_frames is None:
        subprocess.run(cmd, check=True)
    else:
        p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for fr in pipe_frames:
            p.stdin.write(fr)
        p.stdin.close()
        if p.wait() != 0:
            raise RuntimeError(f"ffmpeg failed on beat {bid}")
    return out


if __name__ == "__main__":
    S = load_shotlist(sys.argv[1])
    print(build(S, sys.argv[2], sys.argv[3]))
