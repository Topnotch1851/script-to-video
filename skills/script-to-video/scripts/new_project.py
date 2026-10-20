"""Start a project folder with the standard layout and a starter shot list (free).

usage: new_project.py FOLDER --title "Why the sky is blue" --format vertical --seconds 60 [--beat 5]
                      [--text-style clean|kids] [--motion still|animated|mixed] [--subject person|object|group|none]
Creates: FOLDER/{pictures,clips,voice,music,prompts,deliver}/, shotlist.json with empty beats, layout-guide.png
"""
import os, sys, json, math, argparse, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import layout_guide


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("folder"); ap.add_argument("--title", required=True)
    ap.add_argument("--format", default="vertical", choices=["vertical", "landscape", "square"])
    ap.add_argument("--seconds", type=float, default=60); ap.add_argument("--beat", type=float)
    ap.add_argument("--text-style", default="clean"); ap.add_argument("--motion", default="still", choices=["still", "animated", "mixed"])
    ap.add_argument("--subject", default="person", choices=["person", "object", "group", "none"])
    A = ap.parse_args()
    beat = A.beat or (5.0 if A.format != "landscape" else 6.0)
    n = math.ceil(A.seconds / beat)
    for d in ("pictures", "clips", "voice", "music", "prompts", "deliver"):
        os.makedirs(os.path.join(A.folder, d), exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", A.title.lower()).strip("-")
    S = {"title": A.title, "slug": slug, "format": A.format, "fps": 30, "text_style": A.text_style,
         "motion_mode": A.motion, "guide_subject": A.subject, "style_lock": "", "character": None,
         "loudness": -16, "music": [], "music_db": -14, "duck_db": 8, "auto_sfx": True,
         "beats": [{"id": i + 1, "seconds": beat, "line": "", "scene": "", "action": "", "motion": "",
                    "picture": f"pictures/{i + 1:02d}.png", "voice": f"voice/{i + 1:02d}.mp3",
                    "headline": None, "caption": "", "move": ["zoom-in", "pan-left", "zoom-out", "pan-right"][i % 4]}
                   for i in range(n)]}
    p = os.path.join(A.folder, "shotlist.json")
    if os.path.exists(p):
        sys.exit(f"{p} already exists; not overwriting")
    json.dump(S, open(p, "w"), indent=1)
    if A.subject != "none":
        layout_guide.make(A.format, A.subject, os.path.join(A.folder, "layout-guide.png"))
    print(f"{p}: {n} beats of {beat}s ({n * beat:.0f}s)")


if __name__ == "__main__":
    main()
