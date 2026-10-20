"""Quote what a video will cost BEFORE anything is generated (free).

usage examples
  plan_costs.py --seconds 60 --motion animated --pictures generate
  plan_costs.py --seconds 300 --format landscape --motion still --pictures own --music none
  plan_costs.py --seconds 60 --compare            # every option side by side
options
  --motion    still | animated | mixed (--animated-share 0.3 = 30% of beats animated)
  --pictures  generate (made on fal) | own (you make them elsewhere: $0 here)
  --clips     generate | own  (own = your own filmed footage / clips: $0 here)
  --music     new | own | none        --tracks N (default: 1 per 2 minutes)
  --voice     ai | own (own = you record the narration: $0 here)
  --beat      seconds per picture (default 5 vertical, 6 landscape)
  --chars     narration characters if known (default estimated from --pace)
  --pace      kids (~9 chars/s, slow with pauses) | normal (~14 chars/s)
  --presenter add one character-sheet picture
  --references N  cast sheet + location pictures to make (each one picture)
  --reserve   share kept for retries (default 0.15)
"""
import os, sys, json, math, argparse
KIT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = json.load(open(os.path.join(KIT, "prices.json")))


def quote(seconds, fmt="vertical", motion="still", share=0.5, pictures="generate", clips="generate", music="new",
          tracks=None, voice="ai", beat=None, chars=None, pace="normal", presenter=False, reserve=0.15, references=0):
    beat = beat or (5.0 if fmt in ("vertical", "square") else 6.0)
    n = math.ceil(seconds / beat)
    rows = []
    if pictures == "generate":
        rows.append(("Pictures", f"{n} x ${P['picture']['price']:.2f}", n * P["picture"]["price"]))
        refs = references + (1 if presenter else 0)
        if refs:
            rows.append(("Reference pictures (cast sheet, locations)", f"{refs} x ${P['picture']['price']:.2f}",
                         refs * P["picture"]["price"]))
    else:
        rows.append(("Pictures", f"{n} made by you elsewhere", 0.0))
    if motion in ("animated", "mixed") and clips == "generate":
        anim_s = seconds * (1.0 if motion == "animated" else share)
        cost = anim_s * P["animation"]["price"] * P["animation"]["billed_overrun"]
        rows.append(("Animation", f"{anim_s:.0f} s x ${P['animation']['price']}/s", cost))
    elif motion in ("animated", "mixed"):
        rows.append(("Animation", "your own clips", 0.0))
    else:
        rows.append(("Camera moves on stills", "made locally", 0.0))
    if voice == "ai":
        c = chars or round(seconds * (9 if pace == "kids" else 14))
        rows.append(("Narration", f"~{c} characters", c / 1000 * P["voice"]["price"]))
    else:
        rows.append(("Narration", "your own recording", 0.0))
    if music == "new":
        t = tracks or max(1, math.ceil(seconds / 120))
        rows.append(("Music", f"{t} track(s)", t * P["music"]["price"]))
    else:
        rows.append(("Music", "your own track" if music == "own" else "none", 0.0))
    rows.append(("Sound effects, text, captions, editing, mixing", "made locally", 0.0))
    sub = sum(r[2] for r in rows)
    return rows, sub, sub * reserve, n


def fmt_money(x):
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
    ap.add_argument("--voice", default="ai", choices=["ai", "own"])
    ap.add_argument("--beat", type=float)
    ap.add_argument("--chars", type=int)
    ap.add_argument("--pace", default="normal", choices=["kids", "normal"])
    ap.add_argument("--presenter", action="store_true")
    ap.add_argument("--references", type=int, default=0, help="cast sheet + location pictures to make")
    ap.add_argument("--reserve", type=float, default=0.15)
    ap.add_argument("--compare", action="store_true")
    A = ap.parse_args()
    kw = dict(fmt=A.format, share=A.animated_share, clips=A.clips, music=A.music, tracks=A.tracks, voice=A.voice,
              beat=A.beat, chars=A.chars, pace=A.pace, presenter=A.presenter, reserve=A.reserve, references=A.references)
    mins = A.seconds / 60
    if A.compare:
        print(f"### Options for a {A.seconds:.0f}-second {A.format} video\n")
        print("| | Pictures made here | Your own pictures |\n|---|---|---|")
        for m in ("still", "mixed", "animated"):
            cells = []
            for p in ("generate", "own"):
                _, sub, res, _ = quote(A.seconds, motion=m, pictures=p, **kw)
                cells.append(f"{fmt_money(sub)} (up to {fmt_money(sub + res)})")
            label = {"still": "Still (free camera moves)", "mixed": f"Mixed ({A.animated_share:.0%} animated)", "animated": "Animated"}[m]
            print(f"| **{label}** | {cells[0]} | {cells[1]} |")
        print("\nSecond figure includes the retry reserve. Sound effects, text, editing and mixing are always free.")
        return
    rows, sub, res, n = quote(A.seconds, motion=A.motion, pictures=A.pictures, **kw)
    print(f"### Quote: {A.seconds:.0f} s {A.format}, {A.motion}, pictures: {A.pictures}, music: {A.music}\n")
    print(f"{n} beats of about {A.seconds / n:.1f} s\n")
    print("| Item | Quantity | Cost |\n|---|---|---|")
    for name, q, c in rows:
        print(f"| {name} | {q} | {fmt_money(c)} |")
    print(f"| **Expected total** | | **{fmt_money(sub)}** |")
    print(f"| Retry reserve ({A.reserve:.0%}) | only spent if a take fails | {fmt_money(res)} |")
    print(f"| **Spending cap** | | **{fmt_money(sub + res)}** |")
    print(f"\nPer minute: {fmt_money(sub / mins)}. Prices from prices.json; re-check live before approving.")


if __name__ == "__main__":
    main()
