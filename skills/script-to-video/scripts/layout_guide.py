"""Make a LAYOUT GUIDE picture: a plain grey stand-in at the exact size and place the main subject must take.
Send it to the image model as an extra reference ("copy only the SIZE and POSITION of the figure in this image").
This is what fixed framing in production: asking a model for "empty space at the top" gave hard pale bands instead.

usage: layout_guide.py --format vertical|landscape|square --subject person|object|group [--out guide.png]
"""
import os, sys, argparse
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import FORMATS

SKY, GROUND, GREY, LINE = (205, 225, 240), (190, 220, 175), (150, 150, 155), (90, 90, 95)


def person(d, cx, top, feet, k=1.0):
    h = (feet - top)
    hr = h * 0.105
    d.ellipse([cx - hr, top, cx + hr, top + 2 * hr], fill=GREY, outline=LINE, width=3)
    neck = top + 2 * hr
    sh = neck + h * 0.03
    hip = top + h * 0.56
    bw = h * 0.16
    d.rounded_rectangle([cx - bw, sh, cx + bw, hip], radius=bw * 0.5, fill=GREY, outline=LINE, width=3)
    lw = h * 0.055
    for s in (-1, 1):
        d.line([(cx + s * bw * 0.95, sh + lw), (cx + s * bw * 1.55, hip - h * 0.04)], fill=GREY, width=int(lw * 1.6))
        d.rounded_rectangle([cx + s * bw * 0.5 - lw, hip - lw, cx + s * bw * 0.5 + lw, feet], radius=lw, fill=GREY, outline=LINE, width=3)


def make(fmt, subject, out, scale=0.5):
    F = FORMATS[fmt]
    W, H = round(F["W"] * scale), round(F["H"] * scale)
    top, feet = F["subject"][0] * scale, F["subject"][1] * scale
    im = Image.new("RGB", (W, H), SKY)
    d = ImageDraw.Draw(im)
    d.rectangle([0, feet, W, H], fill=GROUND)
    cx = W / 2
    if subject == "person":
        person(d, cx, top, feet)
    elif subject == "group":
        hgt = feet - top
        for dx, k in ((-0.22, 0.92), (0, 1.0), (0.22, 0.95)):
            person(d, cx + dx * W * (0.6 if fmt == "vertical" else 0.35), feet - hgt * k, feet)
    else:
        w = (feet - top) * 0.9
        d.rounded_rectangle([cx - w / 2, top + (feet - top) * 0.15, cx + w / 2, feet], radius=w * 0.12, fill=GREY, outline=LINE, width=3)
    im.save(out)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--format", default="vertical", choices=list(FORMATS))
    ap.add_argument("--subject", default="person", choices=["person", "object", "group"])
    ap.add_argument("--out", default=None)
    A = ap.parse_args()
    print(make(A.format, A.subject, A.out or f"layout-guide-{A.format}-{A.subject}.png"))
