"""On-screen text for one beat, rendered as a timeline of transparent PNG states.

A beat can carry:
  headline: {"text": "tape", "size": "auto"|int, "from": 0, "until": null,
             "reveal": [{"at": 1.2, "chars": [3], "fade": 0.35}], "ghost": 0.0,
             "marks": [{"at": 1.5, "until": 3.0, "regex": "a", "color": "accent", "alpha": 1.0, "fade": 0}]}
  list:     {"items": ["cake", "gate"], "at": [0.2, 0.9], "size": 110, "marks": [...same selectors...]}
  caption:  "short a: tap"  or  {"text": "...", "from": 0, "until": null}
Selectors inside reveal/marks: "chars": [indices] | "word": n | "match": "ph" (first) | "regex": "e$" (all) | "all": true.
Indices count every character of the text, spaces included.
"""
import re, hashlib, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from common import font_path, rgb

INF = 1e9


def select(text, sel):
    if sel.get("all"):
        return set(range(len(text)))
    if "chars" in sel:
        return set(sel["chars"])
    if "word" in sel:
        spans = [m.span() for m in re.finditer(r"\S+", text)]
        a, b = spans[sel["word"]]
        return set(range(a, b))
    if "match" in sel:
        i = text.find(sel["match"])
        return set(range(i, i + len(sel["match"]))) if i >= 0 else set()
    if "regex" in sel:
        out = set()
        for m in re.finditer(sel["regex"], text):
            out |= set(range(*m.span()))
        return out
    return set()


def char_state(text, spec, t, colors):
    """Per-character (colour, alpha) at time t. alpha 0 = hidden."""
    ink = rgb(spec.get("color", "ink"), colors)
    st = [[ink, 1.0] for _ in text]
    ghost = spec.get("ghost", 0.0)
    waiting = set()                      # characters not yet revealed: plain ink at ghost alpha, marks ignored
    fading = {}
    for r in spec.get("reveal", []):
        for i in select(text, r):
            if t < r["at"]:
                waiting.add(i)
            elif r.get("fade") and t < r["at"] + r["fade"]:
                fading[i] = (t - r["at"]) / r["fade"]
    for m in spec.get("marks", []):
        if not (m.get("at", 0) <= t < m.get("until", INF)):
            continue
        k = 1.0
        if m.get("fade"):
            k = min(1.0, (t - m.get("at", 0)) / m["fade"])
        for i in select(text, m) - waiting:
            if "color" in m:
                c0, c1 = st[i][0], rgb(m["color"], colors)
                st[i][0] = tuple(round(a + (b - a) * k) for a, b in zip(c0, c1))
            if "alpha" in m:
                st[i][1] = st[i][1] + (m["alpha"] - st[i][1]) * k
    for i in waiting:
        st[i][1] = ghost
    for i, k in fading.items():
        st[i][1] = ghost + (st[i][1] - ghost) * k
    return st


def change_times(beat):
    ts = {0.0}
    def add_spec(s):
        if not s:
            return
        for k in ("from", "until"):
            if s.get(k) is not None:
                ts.add(s[k])
        for e in s.get("reveal", []) + s.get("marks", []):
            for k in ("at", "until"):
                if e.get(k) is not None:
                    ts.add(e[k])
            if e.get("fade"):
                for j in range(1, 6):
                    ts.add(e["at"] + e["fade"] * j / 6)
    add_spec(beat.get("headline"))
    lst = beat.get("list")
    if lst:
        for a in lst.get("at", []):
            ts.add(a)
        add_spec({"marks": lst.get("marks", [])})
    cap = beat.get("caption")
    if isinstance(cap, dict):
        add_spec(cap)
    return sorted(t for t in ts if 0 <= t < beat["seconds"])


def wrap(font, text, maxw):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if font.getlength(trial) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur); cur = w
    lines.append(cur)
    return lines


def ink_band(font):
    return font.getbbox("bdhklt", anchor="ls")[1], font.getbbox("gpqy", anchor="ls")[3]


class Renderer:
    def __init__(self, S):
        self.S, self.F = S, S["_fmt"]
        self.W, self.H = self.F["W"], self.F["H"]
        self.hfont = font_path(S["_text"]["headline_font"])
        self.cfont = font_path(S["_text"]["caption_font"])
        self.box = S.get("headline_box", "card")     # card | outline | none
        self.capbox = S.get("caption_box", "pill")   # pill | outline | none
        self.colors = S["colors"]

    def base_color(self):
        """Ink on a card; white (with a dark outline) when text sits straight on the picture."""
        return "ink" if self.box == "card" else self.colors.get("text_on_picture", "#FFFFFF")

    # ---------- drawing helpers ----------
    def card(self, layer, box, radius):
        sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([box[0], box[1] + 10, box[2], box[3] + 10], radius, fill=(40, 40, 60, 70))
        layer.alpha_composite(sh.filter(ImageFilter.GaussianBlur(16)))
        c = rgb(self.colors["card"]) + (236,)
        cl = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        ImageDraw.Draw(cl).rounded_rectangle(box, radius, fill=c)
        layer.alpha_composite(cl)

    def chars(self, layer, font, text, x0, baseline, states, outline):
        x = x0
        for ch, (col, a) in zip(text, states):
            if a > 0.004 and ch != " ":
                cl = Image.new("RGBA", layer.size, (0, 0, 0, 0))
                d = ImageDraw.Draw(cl)
                if outline:
                    sw = max(2, round(font.size * 0.06))
                    d.text((x, baseline), ch, font=font, fill=col + (255,), anchor="ls", stroke_width=sw, stroke_fill=(20, 20, 20, 255))
                else:
                    d.text((x, baseline), ch, font=font, fill=col + (255,), anchor="ls")
                if a < 1:
                    cl.putalpha(cl.getchannel("A").point(lambda v: round(v * a)))
                layer.alpha_composite(cl)
            x += font.getlength(ch)

    # ---------- layout ----------
    def headline_layout(self, text, size):
        band, maxw = self.F["headline"], self.F["headline_max_w"]
        pad_x = 80 if self.box == "card" else 0
        if size == "auto" or size is None:
            size = 240 if self.S["format"] == "vertical" else 150
            while size > 40:
                f = ImageFont.truetype(self.hfont, size)
                lines = wrap(f, text, maxw - 2 * pad_x)
                top, bot = ink_band(f)
                block = (bot - top) * len(lines) + int(size * 0.18) * (len(lines) - 1)
                if len(lines) <= 3 and block <= (band[1] - band[0]) - 60 and max(f.getlength(l) for l in lines) <= maxw - 2 * pad_x:
                    break
                size -= 8
        f = ImageFont.truetype(self.hfont, int(size))
        lines = wrap(f, text, maxw - 2 * pad_x)
        top, bot = ink_band(f)
        lh = (bot - top) + int(f.size * 0.18)
        block = (bot - top) * len(lines) + int(f.size * 0.18) * (len(lines) - 1)
        y0 = (band[0] + band[1]) / 2 - block / 2 - top
        out, idx = [], 0
        for li, line in enumerate(lines):
            x0 = self.W / 2 - f.getlength(line) / 2
            out.append((line, idx, x0, y0 + li * lh))
            idx += len(line) + 1
        width = max(f.getlength(l) for l in lines)
        return f, out, width

    def render(self, beat, t):
        layer = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        hl = beat.get("headline")
        if hl and hl.get("from", 0) <= t < (hl.get("until") or INF):
            f, lines, width = self.headline_layout(hl["text"], hl.get("size", "auto"))
            if self.box == "card":
                band = self.F["headline"]
                self.card(layer, [self.W / 2 - width / 2 - 80, band[0], self.W / 2 + width / 2 + 80, band[1]], 56)
            st = char_state(hl["text"], {"color": self.base_color(), **hl}, t, self.colors)
            for line, start, x0, base in lines:
                self.chars(layer, f, line, x0, base, st[start:start + len(line)], self.box != "card")
        lst = beat.get("list")
        if lst:
            self.render_list(layer, lst, t)
        cap = beat.get("caption")
        if cap:
            c = cap if isinstance(cap, dict) else {"text": cap}
            if c.get("from", 0) <= t < (c.get("until") or INF):
                self.render_caption(layer, c["text"])
        return layer

    def render_list(self, layer, lst, t):
        items, ats = lst["items"], lst.get("at", [0] * len(lst["items"]))
        size = lst.get("size", 110 if self.S["format"] == "vertical" else 80)
        f = ImageFont.truetype(self.hfont, size)
        top, bot = ink_band(f)
        rows = lst.get("rows") or (3 if len(items) > 3 else len(items))
        cols = [items[i:i + rows] for i in range(0, len(items), rows)]
        gap, colgap = 22, 90
        pitch = (bot - top) + gap
        block = pitch * rows - gap
        band = self.F["headline"]
        first = (band[0] + band[1]) / 2 - block / 2
        widths = [max(f.getlength(w) for w in c) for c in cols]
        total = sum(widths) + colgap * (len(cols) - 1)
        if self.box == "card":
            self.card(layer, [self.W / 2 - total / 2 - 70, first - 50, self.W / 2 + total / 2 + 70, first + block + 50], 56)
        left = self.W / 2 - total / 2
        k = 0
        for ci, col in enumerate(cols):
            cx = left + sum(widths[:ci]) + colgap * ci + widths[ci] / 2
            for ri, w in enumerate(col):
                if t >= ats[k]:
                    st = char_state(w, {"color": self.base_color(), "marks": lst.get("marks", [])}, t, self.colors)
                    self.chars(layer, f, w, cx - f.getlength(w) / 2, first - top + ri * pitch, st, self.box != "card")
                k += 1

    def render_caption(self, layer, text):
        band, maxw = self.F["caption"], self.F["cap_max_w"]
        size = self.S["_text"]["caption_size"]
        if self.capbox != "pill":
            size = round(size * 1.15)       # outlined subtitles need a little more size to read over busy pictures
        f = ImageFont.truetype(self.cfont, size)
        lines = wrap(f, text, maxw)
        if len(lines) > 2:
            raise ValueError(f"caption too long for 2 lines: {text!r} (shorten it or split the beat)")
        if len(lines) == 2:                      # balance the two lines (no lonely last word)
            words = text.split(" ")
            best = min(range(1, len(words)), key=lambda k: max(f.getlength(" ".join(words[:k])), f.getlength(" ".join(words[k:]))))
            lines = [" ".join(words[:best]), " ".join(words[best:])]
        bb = f.getbbox("Thgy", anchor="ls")
        lh = (bb[3] - bb[1]) + 12
        width = max(f.getlength(l) for l in lines)
        extra = lh * (len(lines) - 1)
        up = max(0, band[1] + extra - self.F["ui_safe"]["bottom"])   # never push a second line out of the safe area
        cy0 = (band[0] + band[1]) / 2 - up      # first line sits where a one-line caption sits; a second line goes below
        if self.capbox == "pill":
            self.card(layer, [self.W / 2 - width / 2 - 44, band[0] - up, self.W / 2 + width / 2 + 44, band[1] + extra - up], 55)
        d = ImageDraw.Draw(layer)
        for i, line in enumerate(lines):
            base = cy0 + i * lh - (bb[1] + bb[3]) / 2
            if self.capbox == "pill":
                d.text((self.W / 2, base), line, font=f, fill=rgb(self.colors["ink"]) + (255,), anchor="ms")
            elif self.capbox == "tv":           # bold yellow TV-subtitle look, thick black outline
                d.text((self.W / 2, base), line, font=f, fill=rgb(self.colors.get("tv_caption", "#FFD23F")) + (255,),
                       anchor="ms", stroke_width=max(3, size // 9), stroke_fill=(0, 0, 0, 255))
            else:
                d.text((self.W / 2, base), line, font=f, fill=(255, 255, 255, 255), anchor="ms",
                       stroke_width=max(2, size // 14), stroke_fill=(0, 0, 0, 255))

    def timeline(self, beat, outdir):
        """Write one PNG per distinct overlay state. Returns [(t0, t1, png)]."""
        os.makedirs(outdir, exist_ok=True)
        ts = change_times(beat) + [beat["seconds"]]
        segs, last = [], None
        for a, b in zip(ts[:-1], ts[1:]):
            img = self.render(beat, a + 1e-4)
            h = hashlib.md5(img.tobytes()).hexdigest()[:12]
            p = os.path.join(outdir, f"b{beat['id']:03d}_{h}.png")
            if not os.path.exists(p):
                img.save(p)
            if last and last[2] == p:
                segs[-1] = (last[0], b, p)
            else:
                segs.append((a, b, p))
            last = segs[-1]
        return segs
