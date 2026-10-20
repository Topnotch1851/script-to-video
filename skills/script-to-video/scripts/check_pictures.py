"""Check pictures before any money is spent animating them (free). Works for generated AND bring-your-own pictures.

Per picture: readable, big enough, aspect close to the format (warns how much the cover-crop will cut),
no hard horizontal band (the classic "empty strip" failure), no flat empty strip at the top or bottom.
Writes a contact sheet so all pictures can be reviewed in one look.

usage: check_pictures.py --format vertical PICTURE_DIR_OR_FILES... [--sheet contact.png]
Exit code 1 if any picture FAILS (warnings do not fail).
"""
import os, sys, glob, argparse
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import FORMATS

EXT = (".png", ".jpg", ".jpeg", ".webp")


def check(path, fmt):
    F = FORMATS[fmt]; want = F["W"] / F["H"]
    res = {"file": os.path.basename(path), "fail": [], "warn": []}
    try:
        im = Image.open(path).convert("RGB")
    except Exception as e:
        res["fail"].append(f"unreadable ({e})"); return res, None
    w, h = im.size
    if min(w, h) < 640:
        res["fail"].append(f"too small {w}x{h} (short side under 640 px)")
    elif min(w, h) < 720:
        res["warn"].append(f"small {w}x{h}; will be upscaled")
    asp = w / h
    cut = 1 - min(asp, want) / max(asp, want)
    if cut > 0.25:
        res["fail"].append(f"wrong shape: {w}x{h}; {cut:.0%} of the picture would be cropped away for {F['aspect']}")
    elif cut > 0.04:
        res["warn"].append(f"aspect {asp:.3f} vs {want:.3f}: about {cut:.0%} cropped")
    g = np.asarray(im.convert("L").resize((64, 256 if h >= w else 144)), np.float32)
    rows = g.mean(1)
    jump = np.abs(np.diff(rows))
    # a band = a hard horizontal edge with a flat, empty area on one side (a horizon has detail on both sides)
    k = max(4, len(rows) // 10)
    for i in np.argsort(jump)[::-1][:3]:
        if jump[i] <= 38:
            break
        above, below = g[max(0, i - k):i + 1], g[i + 1:i + 1 + k]
        if min(above.std(), below.std()) < 3.5 or max(above.mean(), below.mean()) >= 215:   # flat, or washed-out pale
            res["warn"].append(f"possible band/panel at {i / len(rows):.0%} height (hard edge next to an empty flat area)")
            break
    n = len(rows) // 5
    for name, part in (("top", g[:n]), ("bottom", g[-n:])):
        if part.std() < 4:
            res["warn"].append(f"flat empty strip at the {name} (no detail)")
    return res, im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--format", default="vertical", choices=list(FORMATS))
    ap.add_argument("paths", nargs="+"); ap.add_argument("--sheet", default="contact-sheet.png")
    A = ap.parse_args()
    files = []
    for p in A.paths:
        files += sorted(f for f in glob.glob(os.path.join(p, "*")) if f.lower().endswith(EXT)) if os.path.isdir(p) else [p]
    if not files:
        print("no pictures found"); sys.exit(1)
    thumbs, bad = [], 0
    F = FORMATS[A.format]; tw = 216; th = round(tw * F["H"] / F["W"])
    for f in files:
        r, im = check(f, A.format)
        state = "FAIL" if r["fail"] else ("warn" if r["warn"] else "ok")
        bad += state == "FAIL"
        print(f"{state:4s}  {r['file']}  " + "; ".join(r["fail"] + r["warn"]))
        t = Image.new("RGB", (tw, th + 22), (60, 60, 60))
        if im:
            s = max(tw / im.width, th / im.height)
            r_im = im.resize((round(im.width * s), round(im.height * s)))
            t.paste(r_im.crop(((r_im.width - tw) // 2, (r_im.height - th) // 2, (r_im.width - tw) // 2 + tw, (r_im.height - th) // 2 + th)), (0, 22))
        ImageDraw.Draw(t).text((4, 4), f"{r['file']} {state}", fill=(255, 90, 90) if state == "FAIL" else (255, 255, 255))
        thumbs.append(t)
    cols = 6 if A.format == "vertical" else 4
    sheet = Image.new("RGB", (cols * (tw + 6), ((len(thumbs) + cols - 1) // cols) * (th + 28)), (30, 30, 30))
    for i, t in enumerate(thumbs):
        sheet.paste(t, ((i % cols) * (tw + 6), (i // cols) * (th + 28)))
    sheet.save(A.sheet)
    print(f"{len(files)} pictures, {bad} failing. Contact sheet: {A.sheet}")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
