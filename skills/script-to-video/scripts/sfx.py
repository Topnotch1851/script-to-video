"""Free, synthesised sound effects (no downloads, no licences). Each function returns mono float32 at 48 kHz.
Names usable in a beat's "sfx": [{"at": 0.4, "sound": "pop", "db": -4, "note": 1.5}]
  pop, plink, sparkle, boing, whoosh, soft_down, click, chime, swoosh_up, tick, ding, thud
"""
import numpy as np
SR = 48000
G = 523.25                          # C5
PENTA = [1, 1.125, 1.25, 1.5, 1.6875, 2]


def _env(n, a=0.004, d=0.25):
    t = np.arange(n) / SR
    return np.minimum(1, t / a) * np.exp(-t / d)


def plink(note=1.0, d=0.35):
    f = G * note; n = int(d * 1.6 * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 4 * t) * np.exp(-t / 0.05)
    return s * _env(n, 0.003, d * 0.5)


def pop(**_):
    n = int(0.09 * SR); t = np.arange(n) / SR; f = 520 * np.exp(-t / 0.03) + 180
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.002, 0.03)


def sparkle(note=2.52, **_):
    out = np.zeros(int(0.9 * SR))
    for i, r in enumerate([1, 1.26, 1.5, 2.0, 2.52]):
        p = plink(note / 2.52 * r, 0.22) * 0.7; s = int(i * 0.06 * SR); out[s:s + len(p)] += p[:len(out) - s]
    return out


def boing(**_):
    n = int(0.4 * SR); t = np.arange(n) / SR
    f = 220 + 160 * np.sin(2 * np.pi * 9 * t) * np.exp(-t / 0.15) + 140 * np.exp(-t / 0.05)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.003, 0.12)


def whoosh(**_):
    n = int(0.45 * SR); t = np.arange(n) / SR; rng = np.random.default_rng(3)
    noise = rng.normal(0, 1, n)
    # band-limited noise with a rising-then-falling envelope
    k = np.exp(-((t - 0.22) / 0.12) ** 2)
    sm = np.convolve(noise, np.ones(24) / 24, "same")
    return (noise - sm) * k * 0.6


def swoosh_up(**_):
    n = int(0.3 * SR); t = np.arange(n) / SR; f = 300 + 2400 * (t / t[-1]) ** 2
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * t / t[-1]) * 0.5


def soft_down(**_):
    n = int(0.45 * SR); t = np.arange(n) / SR; f = 880 * np.exp(-t / 0.35)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.01, 0.18) * 0.6


def click(**_):
    n = int(0.03 * SR); rng = np.random.default_rng(1)
    return rng.normal(0, 1, n) * _env(n, 0.0005, 0.004)


def tick(**_):
    n = int(0.05 * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * 2200 * t) * _env(n, 0.0005, 0.008)


def chime(note=1.0, **_):
    out = np.zeros(int(1.4 * SR))
    for r, g in ((1, 1), (2.76, 0.4), (5.4, 0.2)):
        n = len(out); t = np.arange(n) / SR
        out += g * np.sin(2 * np.pi * G * 2 * note * r * t) * _env(n, 0.002, 0.45 / r)
    return out


def ding(note=1.0, **_):
    return chime(note * 1.5)[: int(0.8 * SR)]


def thud(**_):
    n = int(0.25 * SR); t = np.arange(n) / SR; f = 120 * np.exp(-t / 0.08) + 45
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * _env(n, 0.002, 0.07)


LIB = {"pop": pop, "plink": plink, "sparkle": sparkle, "boing": boing, "whoosh": whoosh, "swoosh_up": swoosh_up,
       "soft_down": soft_down, "click": click, "tick": tick, "chime": chime, "ding": ding, "thud": thud}


def make(name, note=None):
    fn = LIB[name]
    s = fn(note) if (note is not None and name in ("plink", "chime", "ding", "sparkle")) else fn()
    s = np.asarray(s, np.float32)
    return s / (np.max(np.abs(s)) + 1e-9)


def auto_cues(beat):
    """Gentle default cues from the overlay plan: pop when text appears, rising plinks on reveals/marks/list items."""
    cues = []
    hl = beat.get("headline")
    if hl:
        cues.append({"at": hl.get("from", 0) + 0.02, "sound": "pop", "db": -4})
        ev = sorted({e["at"] for e in hl.get("reveal", []) + hl.get("marks", []) if e.get("at", 0) > 0.05})
        for i, a in enumerate(ev):
            cues.append({"at": a, "sound": "plink", "note": PENTA[i % len(PENTA)] * 1.5, "db": -6})
    lst = beat.get("list")
    if lst:
        for i, a in enumerate(lst.get("at", [])):
            cues.append({"at": a, "sound": "plink", "note": PENTA[i % len(PENTA)], "db": -5})
    if beat.get("transition") == "whoosh":
        cues.append({"at": 0.0, "sound": "whoosh", "db": -9})
    return cues
