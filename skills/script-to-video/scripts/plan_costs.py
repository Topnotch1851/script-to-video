"""Quote what a video will cost BEFORE anything is generated (free).

usage examples
  plan_costs.py --seconds 30 --motion animated --menu          # the quality menu: every model level side by side
  plan_costs.py --seconds 30 --motion animated --picture-model pro --motion-model pro
  plan_costs.py --seconds 300 --format landscape --motion still --pictures own --music none
  plan_costs.py --seconds 60 --compare                          # still / mixed / animated x made here / your own
options
  --picture-model standard (Nano Banana 2, 1K) | pro (Nano Banana Pro, 2K)
  --motion-model  standard (MiniMax H3)        | pro (Kling 2.6 Pro; clips bill 5 or 10 s)
  --motion    still | animated | mixed (--animated-share 0.3 = 30% of scenes animated)
  --pictures  generate (made on fal) | own (you make them elsewhere: $0 here)
  --clips     generate | own  (own = your own filmed footage / clips: $0 here)
  --music     new | own | none        --tracks N (default: 1 per 2 minutes)
  --voice     ai | own | none (own = you record the narration: $0 here)
  --beat      seconds per scene (default 5 vertical, 6 landscape)
  --chars     narration characters if known (default estimated from --pace)
  --pace      kids (~9 chars/s) | normal (~14 chars/s)
  --references N  cast sheet + location pictures to make      --presenter  same as --references 1
  --reserve   share kept for retries (default 0.15)
"""
import os, json, math, argparse
KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = json.load(open(os.path.join(KIT, "prices.json")))


def anim_seconds(seconds, n, share, model):
    """Seconds billed for animation. Kling only makes 5 s or 10 s clips, so each scene rounds up."""
    scenes = n * share
    if model == "pro":
        per = seconds / n
        return scenes * (5 if per <= 7 else 10) if per <= 10 else scenes * math.ceil(per / 5) * 5
    return seconds * share * P["animation"][model]["billed_overrun"]


def quote(seconds, fmt="vertical", motion="still", share=0.5, pictures="generate", clips="generate", music="new",
          tracks=None, voice="ai", beat=None, chars=None, pace="normal", presenter=False, reserve=0.15, references=0,
          picture_model="standard", motion_model="standard"):
    beat = beat or (5.0 if fmt in ("vertical", "square") else 6.0)
    n = math.ceil(seconds / beat - 1e-9)
    pm, mm = P["picture"][picture_model], P["animation"][motion_model]
    rows = []
    if pictures == "generate":
        rows.append((f"Pictures — {pm['label']}", f"{n} x ${pm['price']:.2f}", n * pm["price"]))
        refs = references + (1 if presenter else 0)
        if refs:
            rows.append(("Reference pictures (cast sheet, locations)", f"{refs} x ${pm['price']:.2f}", refs * pm["price"]))
    else:
        rows.append(("Pictures", f"{n} made by you elsewhere", 0.0))
    if motion in ("animated", "mixed") and clips == "generate":
        sh = 1.0 if motion == "animated" else share
        s = anim_seconds(seconds, n, sh, motion_model)
        rows.append((f"Animation — {mm['label']}", f"{s:.0f} s x ${mm['price']}/s", s * mm["price"]))
    elif motion in ("animated", "mixed"):
        rows.append(("Animation", "your own clips", 0.0))
    else:
        rows.append(("Camera moves on stills", "made locally", 0.0))
    if voice == "ai":
        c = chars or round(seconds * (9 if pace == "kids" else 14))
        rows.append(("Voice", f"~{c} characters", c / 1000 * P["voice"]["price"]))
    else:
        rows.append(("Voice", "your own recording" if voice == "own" else "none", 0.0))
    if music == "new":
        t = tracks or max(1, math.ceil(seconds / 120))
        rows.append(("Music (new)", f"{t} track(s)", t * P["music"]["price"]))
    else:
        rows.append(("Music", "your own track" if music == "own" else "none", 0.0))
    rows.append(("Sound effects, text, captions, editing, mixing", "made locally", 0.0))
    sub = sum(r[2] for r in rows)
    return rows, sub, sub * reserve, n


def money(x):
    return f"${x:,.2f}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, required=True)
    ap.add_argument("--format", default="vertical")
    ap.add_argument("--motion", default="still", choices=["still", "animated", "mixed"])
    ap.add_argument("--animated-share", type=float, default=0.5)
    ap.add_argument("--pictures", default="generate", choices=["generate", "own"])
    ap.add_argument("--clips", default="generate", choices=["generate", "own"])
    ap.add_argument("--music", default="new", choices=["new", "own", "none"])
    ap.add_argument("--tracks", type=int)
    ap.add_argument("--voice", default="ai", choices=["ai", "own", "none"])
    ap.add_argument("--beat", type=float)
    ap.add_argument("--chars", type=int)
    ap.add_argument("--pace", default="normal", choices=["kids", "normal"])
    ap.add_argument("--presenter", action="store_true")
    ap.add_argument("--references", type=int, default=0)
    ap.add_argument("--picture-model", default="standard", choices=list(P["picture"]))
    ap.add_argument("--motion-model", default="standard", choices=list(P["animation"]))
    ap.add_argument("--reserve", type=float, default=0.15)
    ap.add_argument("--compare", action="store_true")
    ap.add_argument("--menu", action="store_true")
    A = ap.parse_args()
    kw = dict(fmt=A.format, share=A.animated_share, clips=A.clips, music=A.music, tracks=A.tracks, voice=A.voice,
              beat=A.beat, chars=A.chars, pace=A.pace, presenter=A.presenter, reserve=A.reserve, references=A.references)
    if A.menu:
        motion = A.motion if A.motion != "still" else "animated"
        print(f"### Quality menu: {A.seconds:.0f}-second {A.format} video, {motion}\n")
        print("| Level | Pictures | Animation | Pictures made here | Your own pictures |\n|---|---|---|---|---|")
        for name, pmod, mmod in (("Budget", "standard", "standard"), ("Sharper pictures", "pro", "standard"),
                                 ("Better motion", "standard", "pro"), ("Premium", "pro", "pro")):
            _, a, ra, _ = quote(A.seconds, motion=motion, pictures="generate", picture_model=pmod, motion_model=mmod, **kw)
            _, b, rb, _ = quote(A.seconds, motion=motion, pictures="own", picture_model=pmod, motion_model=mmod, **kw)
            own = f"{money(b)} (cap {money(b + rb)})"     # your own pictures: the picture model does not matter
            print(f"| **{name}** | {P['picture'][pmod]['label']} | {P['animation'][mmod]['label']} | "
                  f"{money(a)} (cap {money(a + ra)}) | {own} |")
        _, s1, _, _ = quote(A.seconds, motion="still", pictures="generate", **kw)
        _, s2, _, _ = quote(A.seconds, motion="still", pictures="generate", picture_model="pro", **kw)
        _, s3, _, _ = quote(A.seconds, motion="still", pictures="own", **kw)
        print(f"| Still (no animation) | Nano Banana 2 / Pro | free camera moves | {money(s1)} / {money(s2)} | {money(s3)} |")
        print("\nMusic: new music adds $0.08 per track; your own track or none adds $0. "
              "Sound effects, text, captions, editing and mixing are always free.")
        return
    if A.compare:
        print(f"### Options for a {A.seconds:.0f}-second {A.format} video "
              f"({P['picture'][A.picture_model]['label']}, {P['animation'][A.motion_model]['label']})\n")
        print("| | Pictures made here | Your own pictures |\n|---|---|---|")
        for m in ("still", "mixed", "animated"):
            cells = []
            for p in ("generate", "own"):
                _, sub, res, _ = quote(A.seconds, motion=m, pictures=p, picture_model=A.picture_model,
                                       motion_model=A.motion_model, **kw)
                cells.append(f"{money(sub)} (up to {money(sub + res)})")
            label = {"still": "Still (free camera moves)", "mixed": f"Mixed ({A.animated_share:.0%} animated)",
                     "animated": "Animated"}[m]
            print(f"| **{label}** | {cells[0]} | {cells[1]} |")
        print("\nSecond figure includes the retry reserve. Sound effects, text, editing and mixing are always free.")
        return
    rows, sub, res, n = quote(A.seconds, motion=A.motion, pictures=A.pictures, picture_model=A.picture_model,
                              motion_model=A.motion_model, **kw)
    print(f"### Quote: {A.seconds:.0f} s {A.format}, {A.motion}, pictures: {A.pictures}, music: {A.music}\n")
    print(f"{n} scenes of about {A.seconds / n:.1f} s\n")
    print("| Item | Quantity | Cost |\n|---|---|---|")
    for name, q, c in rows:
        print(f"| {name} | {q} | {money(c)} |")
    print(f"| **Expected total** | | **{money(sub)}** |")
    print(f"| Retry reserve ({A.reserve:.0%}) | only spent if a take fails | {money(res)} |")
    print(f"| **Spending cap** | | **{money(sub + res)}** |")
    print(f"\nPer minute: {money(sub / (A.seconds / 60))}. Prices from prices.json; re-check live before approving.")


if __name__ == "__main__":
    main()
