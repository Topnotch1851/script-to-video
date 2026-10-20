"""Make a thumbnail / cover from one of the video's pictures (free).

usage: thumbnail.py PICTURE "Big short title" OUT.png [--size youtube|vertical|square] [--font Poppins-Bold.ttf]
       [--color "#FFD23F"] [--position top|bottom]
youtube = 1280x720 (YouTube long-form thumbnail), vertical = 1080x1920 (Shorts/Reels cover), square = 1080x1080.
Big, high-contrast text with a dark outline and soft shadow so it reads at phone size. Keep titles to 2-5 words.
"""
import os, sys, argparse
from PIL import Image, ImageDraw, ImageFont, ImageFilter
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import font_path, rgb
from overlay import wrap

SIZES = {"youtube": (1280, 720), "vertical": (1080, 1920), "square": (1080, 1080)}


def make(pic, text, out, size="youtube", font="Poppins-Bold.ttf", color="#FFD23F", position="top"):
    W, H = SIZES[size]
    im = Image.open(pic).convert("RGB")
    s = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    im = im.crop(((im.width - W) // 2, (im.height - H) // 2, (im.width - W) // 2 + W, (im.height - H) // 2 + H)).convert("RGBA")
    maxw = W * 0.88
    fs = int(H * (0.2 if size == "youtube" else 0.11))
    while fs > 20:
        f = ImageFont.truetype(font_path(font), fs)
        lines = wrap(f, text.upper() if size == "youtube" else text, maxw)
        if len(lines) <= 2 and max(f.getlength(l) for l in lines) <= maxw:
            break
        fs -= 4
    lh = int(fs * 1.08)
    block = lh * len(lines)
    y0 = H * 0.07 if position == "top" else H * 0.93 - block
    if size == "vertical":
        y0 = H * 0.16 if position == "top" else H * 0.72 - block
    sw = max(4, fs // 11)
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(sh)
    for i, l in enumerate(lines):
        d.text((W / 2 + fs * 0.04, y0 + i * lh + fs * 0.06), l, font=f, fill=(0, 0, 0, 160), anchor="ma", stroke_width=sw, stroke_fill=(0, 0, 0, 160))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(fs * 0.05)))
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        d.text((W / 2, y0 + i * lh), l, font=f, fill=rgb(color) + (255,), anchor="ma", stroke_width=sw, stroke_fill=(15, 15, 25, 255))
    im.convert("RGB").save(out, quality=92)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("picture"); ap.add_argument("text"); ap.add_argument("out")
    ap.add_argument("--size", default="youtube", choices=list(SIZES)); ap.add_argument("--font", default="Poppins-Bold.ttf")
    ap.add_argument("--color", default="#FFD23F"); ap.add_argument("--position", default="top", choices=["top", "bottom"])
    A = ap.parse_args()
    print(make(A.picture, A.text, A.out, A.size, A.font, A.color, A.position))
