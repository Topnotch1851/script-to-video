"""Shared helpers for the script-to-video toolkit: formats, fonts, colours, shot list loading, audio I/O."""
import json, os, re, shutil, subprocess
import numpy as np

KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = os.path.join(KIT, "fonts")
SR = 48000

# Screen layouts. Every y value is in output pixels.
#   headline: band for big on-screen words (text card), centred in this band
#   subject:  where the main person/object should sit in every picture (head to feet)
#   caption:  caption pill band; captions are kept narrower than cap_max_w
FORMATS = {
    "vertical": {  # 9:16 Shorts / Reels / TikTok. Proven in production.
        "W": 1080, "H": 1920, "aspect": "9:16",
        "headline": (425, 765), "subject": (830, 1350), "caption": (1368, 1478),
        "cap_max_w": 620, "headline_max_w": 900,
        "ui_safe": {"top": 270, "bottom": 1500, "right_rail_x": 850},
    },
    "landscape": {  # 16:9 YouTube long-form.
        "W": 1920, "H": 1080, "aspect": "16:9",
        "headline": (60, 280), "subject": (300, 900), "caption": (918, 1014),
        "cap_max_w": 1500, "headline_max_w": 1500,
        "ui_safe": {"top": 54, "bottom": 1026, "right_rail_x": 1824},
    },
    "square": {  # 1:1 feed posts.
        "W": 1080, "H": 1080, "aspect": "1:1",
        "headline": (60, 300), "subject": (320, 900), "caption": (930, 1030),
        "cap_max_w": 900, "headline_max_w": 940,
        "ui_safe": {"top": 54, "bottom": 1040, "right_rail_x": 1026},
    },
}

TEXT_STYLES = {
    # kids: early-reader font (single-storey a and g) + friendly handwriting captions
    "kids": {"headline_font": "Andika-Bold.ttf", "caption_font": "PatrickHand-Regular.ttf", "caption_size": 64},
    # clean: modern explainer / business / documentary look
    "clean": {"headline_font": "Poppins-Bold.ttf", "caption_font": "Poppins-SemiBold.ttf", "caption_size": 46},
}

NAMED = {"ink": "#1F1F1F", "accent": "#D46F12", "card": "#FFFDF8", "white": "#FFFFFF", "black": "#000000"}


def font_path(name):
    p = name if os.path.isabs(name) else os.path.join(FONTS, name)
    if not os.path.exists(p):
        raise FileNotFoundError(f"font not found: {p}")
    return p


def rgb(c, colors=None):
    """'#RRGGBB', a named colour, or a key of the shot list's colours -> (r,g,b)."""
    if isinstance(c, (list, tuple)):
        return tuple(int(v) for v in c[:3])
    if colors and c in colors:
        c = colors[c]
    c = NAMED.get(c, c)
    c = c.lstrip("#")
    return tuple(int(c[i:i + 2], 16) for i in (0, 2, 4))


def load_shotlist(path):
    """Load a shot list and fill defaults. Relative media paths resolve against the shot list's folder."""
    S = json.load(open(path))
    root = os.path.dirname(os.path.abspath(path))
    S.setdefault("format", "vertical")
    if S["format"] not in FORMATS:
        raise ValueError(f"format must be one of {list(FORMATS)}")
    S["_fmt"] = FORMATS[S["format"]]
    S["_root"] = root
    S.setdefault("fps", 30)
    S.setdefault("text_style", "clean")
    ts = S["text_style"]
    S["_text"] = dict(TEXT_STYLES[ts]) if isinstance(ts, str) else {**TEXT_STYLES["clean"], **ts}
    S.setdefault("colors", {})
    S["colors"] = {**NAMED, **S["colors"]}
    S.setdefault("loudness", -16.0)
    S.setdefault("music_db", -10.0)      # music level relative to the voice, before ducking (preferred in real use)
    S.setdefault("duck_db", 4.0)         # extra dip while someone speaks
    S.setdefault("sfx_db", -6.0)
    S.setdefault("ambience_db", -36.0)
    S.setdefault("auto_sfx", True)
    S.setdefault("default_move", "zoom-in")
    t = 0.0
    for i, b in enumerate(S["beats"]):
        b.setdefault("id", i + 1)
        b.setdefault("seconds", 5.0)
        frames = round(b["seconds"] * S["fps"])
        b["seconds"] = frames / S["fps"]          # every beat is a whole number of frames, so nothing drifts
        b["_frames"] = frames
        b["_start"] = t
        t += b["seconds"]
        b.setdefault("voice_at", 0.0)
        b.setdefault("move", S["default_move"])
        for k in ("picture", "clip", "voice"):
            if b.get(k) and not b[k].startswith("http") and not os.path.isabs(b[k]):
                b[k] = os.path.join(root, b[k])
        for ln in b.get("lines") or []:                # dialogue: several voice files per beat
            if ln.get("file") and not os.path.isabs(ln["file"]):
                ln["file"] = os.path.join(root, ln["file"])
    S["_total"] = t
    for m in S.get("music", []) or []:
        if not os.path.isabs(m["file"]):
            m["file"] = os.path.join(root, m["file"])
    # one presenter ("character") is a cast of one
    if not S.get("cast") and S.get("character"):
        c = dict(S["character"]); c.setdefault("id", "presenter"); S["cast"] = [c]
    S.setdefault("cast", [])
    S.setdefault("locations", [])
    return S


def span_seconds(S, i):
    """Seconds a beat's voice may use: the beat itself plus any following beats marked "continues": true
    (a long line spread over two or more pictures, e.g. scene 3a + 3b)."""
    beats = S["beats"]
    total = beats[i]["seconds"]
    j = i + 1
    while j < len(beats) and beats[j].get("continues"):
        total += beats[j]["seconds"]; j += 1
    return total


def voice_plan(b, gap=0.25):
    """Where every spoken line of a beat sits: [(file, start_in_beat, onset, end, speaker, text)].
    A single "voice" file, or "lines" (dialogue). Lines without "at" follow the previous line after `gap` seconds."""
    items = b.get("lines") or ([{"file": b["voice"], "at": b.get("voice_at", 0.0), "text": b.get("line"),
                                 "speaker": b.get("speaker")}] if b.get("voice") else [])
    out, cursor = [], b.get("voice_at", 0.0)
    for ln in items:
        if not ln.get("file") or not os.path.exists(ln["file"]):
            continue
        x = decode_audio(ln["file"])
        on, end = speech_bounds(x)
        if on is None:
            continue
        start = ln["at"] if ln.get("at") is not None else max(0.0, cursor - on)
        out.append((ln["file"], start, start + on, start + end, ln.get("speaker"), ln.get("text")))
        cursor = start + end + gap
    return out


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, **kw)


def _find_ffmpeg():
    """System ffmpeg if installed, else the binary bundled with `pip install imageio-ffmpeg`."""
    p = shutil.which("ffmpeg")
    if p:
        return p
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        raise SystemExit("ffmpeg not found. Install it (https://ffmpeg.org) or run: pip install imageio-ffmpeg")


FFMPEG = _find_ffmpeg()
FFPROBE = shutil.which("ffprobe")


def probe_duration(path, stream=None):
    """Duration in seconds of the file, or of one stream ('v:0', 'a:0'). Works without ffprobe."""
    if FFPROBE:
        args = [FFPROBE, "-v", "error"]
        if stream:
            args += ["-select_streams", stream, "-show_entries", "stream=duration"]
        else:
            args += ["-show_entries", "format=duration"]
        out = subprocess.run(args + ["-of", "csv=p=0", path], capture_output=True, text=True).stdout.strip().splitlines()
        if out and out[0] not in ("", "N/A"):
            return float(out[0])
    # fallback: decode the stream and measure it
    sel = ["-map", f"0:{stream}"] if stream else []
    r = subprocess.run([FFMPEG, "-hide_banner", "-i", path, *sel, "-f", "null", "-"], capture_output=True, text=True).stderr
    times = re.findall(r"time=(\d+):(\d+):([\d.]+)", r)
    if times:
        h, m, s = times[-1]
        return int(h) * 3600 + int(m) * 60 + float(s)
    d = re.search(r"Duration: (\d+):(\d+):([\d.]+)", r)
    return int(d.group(1)) * 3600 + int(d.group(2)) * 60 + float(d.group(3)) if d else None


def has_audio(path):
    r = subprocess.run([FFMPEG, "-hide_banner", "-i", path], capture_output=True, text=True).stderr
    return bool(re.search(r"Stream #\S+.*Audio:", r))


def decode_audio(path, sr=SR, channels=2):
    """Any audio/video file -> float32 array (n, channels)."""
    pcm = subprocess.run([FFMPEG, "-v", "error", "-i", path, "-vn", "-ac", str(channels), "-ar", str(sr),
                          "-f", "f32le", "-"], capture_output=True, check=True).stdout
    return np.frombuffer(pcm, np.float32).reshape(-1, channels).copy()


def write_wav(path, x, sr=SR):
    import wave
    x = np.clip(x, -1, 1)
    pcm = (x * 32767).astype("<i2")
    with wave.open(path, "wb") as w:
        w.setnchannels(x.shape[1]); w.setsampwidth(2); w.setframerate(sr); w.writeframes(pcm.tobytes())


def speech_bounds(x, sr=SR, thr_db=-40.0, win=0.02):
    """(onset, end) of sound in 20 ms windows, or (None, None) when silent.
    The threshold is -40 dBFS or 30 dB under the loudest window, whichever is lower, so quiet home recordings still work."""
    mono = x.mean(1) if x.ndim == 2 else x
    n = int(win * sr)
    if len(mono) < n:
        return None, None
    fr = mono[:len(mono) // n * n].reshape(-1, n)
    db = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9)
    if db.max() < -70:
        return None, None
    on = np.nonzero(db > min(thr_db, db.max() - 30))[0]
    if not len(on):
        return None, None
    return on[0] * win, (on[-1] + 1) * win


def rms_db(x):
    return 20 * np.log10(np.sqrt((x ** 2).mean()) + 1e-12)
