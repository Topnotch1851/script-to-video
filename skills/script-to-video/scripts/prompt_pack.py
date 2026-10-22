"""Turn a shot list into ready-to-use prompts and job lists (free).

Writes, next to the shot list (folder prompts/):
  PICTURE-PROMPTS.md     step 0 reference images (cast sheet, location plates) + one copy-paste prompt per picture,
                         with how to save, name and upload them (for people making pictures in any other tool)
  ANIMATION-PROMPTS.md   one motion prompt per beat (for any image-to-video tool)
  fal-references.json    jobs for the cast sheet and location plates (nano-banana-2)
  fal-pictures.json      jobs for every picture (nano-banana-2/edit) with placeholders
                         {CAST_URL}, {PLATE_URL_<location id>}, {GUIDE_URL}
  fal-clips.json         jobs for every animated beat (minimax h3) with placeholder {PICTURE_URL_<beat id>}
  fal-voice.json         jobs for every spoken line (eleven-v3), one per narrator line or dialogue line

Shot list fields used: style_lock, look, cast[] (or character), locations[], guide_subject, voice, motion_style,
beats[].scene/action/motion/cast/location/subject_size/loop/clip_seconds/line/lines/speaker.
usage: prompt_pack.py SHOTLIST.json
"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_shotlist

NO_TEXT = ("No text, no letters, no numbers, no symbols, no logos, no writing anywhere, including on signs, books, "
           "screens, paper, clothing and flags.")
FULL_CANVAS = ("The picture is one continuous scene that fills the WHOLE canvas evenly from the top edge to the bottom "
               "edge with detail all the way to the edges: no bands, no panels, no faded or blurred strips, no borders, "
               "no frames, no empty boxes, no split screens.")
TAIL_LOOP = ("Locked camera, fixed shot. Every character keeps the same face, body, clothes and colours. "
             "Nothing new appears, no text appears. Everyone returns to the starting pose at the end.")
TAIL_FREE = ("Mostly locked camera. Characters act with their whole bodies; their designs, faces, clothes and colours "
             "never change. No new characters, no text appears.")
TAIL_CHAIN = ("Locked camera, fixed wide shot, no zoom; the place and furniture stay where they are. Characters keep the "
              "same faces, bodies, clothes and colours. Mouths closed, not talking. Nothing written appears anywhere. "
              "The shot ends exactly on the last frame.")
cap = lambda s: s[:1].upper() + s[1:] if s else s
PRICES = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "prices.json")))
KLING_NEGATIVE = ("blur, distortion, extra limbs, extra characters, morphing faces, new text appearing, morphing text, "
                  "garbled letters, photorealism, colour shifts, camera shake")


def cast_in(S, b):
    cast = S.get("cast", [])
    if not cast:
        return []
    ids = b.get("cast")
    if ids is None:
        return cast if len(cast) == 1 else [c for c in cast if c.get("always", True)]
    return [c for c in cast if c.get("id") in ids]


def location_of(S, b):
    lid = b.get("location")
    return next((l for l in S.get("locations", []) if l.get("id") == lid), None) if lid else None


def refs_for(S, b):
    """Ordered reference images for a beat: [(kind, placeholder)]."""
    out = []
    if cast_in(S, b):
        out.append(("cast", "{CAST_URL}"))
    loc = location_of(S, b)
    if loc and loc.get("plate", True):
        out.append(("plate", "{PLATE_URL_%s}" % loc["id"]))
    elif S.get("guide_subject", "person") != "none":
        out.append(("guide", "{GUIDE_URL}"))
    return out


def describe(c):
    s = f"{c.get('name', c.get('id'))}: {c['description'].rstrip('.')}"
    if c.get("outfit"):
        s += f"; this time wearing {c['outfit']}"
    return s + "."


def picture_prompt(S, b, refs):
    parts = ["Draw a NEW picture." if S.get("look", "illustrated") != "photo" else "Create a NEW photograph."]
    people = cast_in(S, b)
    loc = location_of(S, b)
    for k, (kind, _) in enumerate(refs, 1):
        if kind == "cast":
            if len(S["cast"]) == 1:
                c = S["cast"][0]
                parts.append(f"Image {k} is the character design of {c.get('name', 'the presenter')}. Keep the "
                             f"{c.get('keep', 'face, hair, body shape, line style and colours')} exactly like Image {k}."
                             + (f" This time the outfit is: {c['outfit']}." if c.get("outfit") else ""))
            else:
                parts.append(f"Image {k} is the cast sheet. Match the characters in this picture to it exactly: same faces, "
                             f"bodies, proportions, clothes and colours.")
        elif kind == "plate":
            parts.append(f"Image {k} shows the {loc.get('name', loc['id'])}. Match this place exactly: same furniture, "
                         f"colours and layout. The camera may be closer or at a slightly different angle if the scene asks for it.")
        elif kind == "guide":
            subj = S.get("guide_subject", "person")
            if subj == "object":
                parts.append(f"Image {k} is a LAYOUT GUIDE ONLY. Make the main subject the same SIZE and POSITION as the grey "
                             f"shape in Image {k}: same height on the canvas, centred horizontally, resting on the same ground line. "
                             f"Do not copy its shape, colours or plain background.")
            else:
                who = "figures" if subj == "group" else "figure"
                parts.append(f"Image {k} is a LAYOUT GUIDE ONLY. Copy exactly the SIZE and POSITION of the grey {who} in Image {k}: "
                             f"same height on the canvas, centred horizontally, head at the same place, standing on the same "
                             f"ground line. Do not copy the pose, colours or plain background.")
    if people and (len(S["cast"]) > 1 or not any(k == "cast" for k, _ in refs)):
        parts.append("In this picture: " + " ".join(describe(c) for c in people))
    if loc and not any(k == "plate" for k, _ in refs):
        parts.append(f"Location, {loc.get('name', loc['id'])}: {cap(loc['description'].rstrip('.'))}.")
    if b.get("picture_prompt"):                   # director mode: the person's own scene prompt, word for word
        parts.append(b["picture_prompt"])
        if "no text" not in b["picture_prompt"].lower():
            parts.append(NO_TEXT)
        return "\n\n".join(parts)
    parts.append("Scene: " + cap(b.get("scene", "").rstrip(".")) + "." +
                 (" " + cap(b["action"].rstrip(".")) + "." if b.get("action") else ""))
    if b.get("subject_size") == "small":
        parts.append("Keep the main character SMALL: about one quarter of the picture height.")
    elif b.get("subject_size") == "close":
        parts.append("Show the main character closer (waist up), still centred.")
    if S.get("guide_subject", "person") in ("person", "group") and not loc:
        parts.append("Any object or animal stays beside the characters with its bottom on the same ground line, never below their feet.")
    parts.append(FULL_CANVAS)
    parts.append("Style: " + S.get("style_lock", "clean, bright, detailed illustration").rstrip(".") + ".")
    parts.append(NO_TEXT)
    return "\n\n".join(parts)


def cast_sheet_prompt(S):
    cast, style = S["cast"], S.get("style_lock", "")
    if len(cast) == 1:
        c = cast[0]
        return (f"Character reference sheet for an animation. One character named {c.get('name', 'the presenter')}: "
                f"{c['description']} Show the same character four times in a row on a plain light-grey background: "
                f"standing front view, walking side view, pointing up and to the side with one arm, sitting. Same size in all "
                f"four. No labels. Style: {style.rstrip('.')}. {NO_TEXT}")
    lines = " ".join(f"{i}) {describe(c)}" for i, c in enumerate(cast, 1))
    return (f"Character reference sheet for an animation, plain light-grey background, no scene. {len(cast)} characters "
            f"in a row, each shown in a front view and a three-quarter view, all at the same scale: {lines} "
            f"Below them, a row of small head close-ups for each character showing four expressions: happy, surprised, "
            f"thinking, talking. No labels. Style: {style.rstrip('.')}. {NO_TEXT}")


def plate_prompt(S, loc):
    return (f"Establishing shot of the {loc.get('name', loc['id'])} with no characters in it. {cap(loc['description'].rstrip('.'))}. "
            f"Wide, level camera. {FULL_CANVAS} Style: {S.get('style_lock', '').rstrip('.')}. {NO_TEXT}")


def motion_prompt(S, b):
    loop = b.get("loop", S.get("motion_style", "loop") == "loop")
    if b.get("chain"):
        loop = False
    if b.get("clip_prompt"):                      # director mode: the person's own clip prompt, word for word
        return b["clip_prompt"], loop
    m = b.get("motion") or "gentle idle movement: the characters breathe, blink and shift weight slightly"
    if b.get("chain"):
        return ("Continuous shot in the same place. " + m.rstrip(".") + ". " + TAIL_CHAIN), loop
    return m.rstrip(".") + ". " + (TAIL_LOOP if loop else TAIL_FREE), loop


def voice_jobs(S):
    voices = {c.get("id"): c.get("voice") for c in S.get("cast", [])}
    default = S.get("voice", "Rachel")
    jobs = []
    for b in S["beats"]:
        if b.get("lines"):
            for i, ln in enumerate(b["lines"], 1):
                jobs.append({"beat": b["id"], "file": ln.get("file") or f"voice/{b['id']:02d}-{i}.mp3",
                             "speaker": ln.get("speaker"),
                             "input": {"text": ln["text"], "voice": ln.get("voice") or voices.get(ln.get("speaker")) or default,
                                       "stability": 0.5}})
        elif b.get("line"):
            jobs.append({"beat": b["id"], "file": b.get("voice") or f"voice/{b['id']:02d}.mp3", "speaker": b.get("speaker"),
                         "input": {"text": b["line"], "voice": voices.get(b.get("speaker")) or default, "stability": 0.5}})
    for j in jobs:
        j["file"] = os.path.relpath(j["file"], S["_root"]) if os.path.isabs(j["file"]) else j["file"]
        j["endpoint_id"] = "fal-ai/elevenlabs/tts/eleven-v3"
    return jobs


def main():
    S = load_shotlist(sys.argv[1])
    out = os.path.join(S["_root"], "prompts"); os.makedirs(out, exist_ok=True)
    asp = S["_fmt"]["aspect"]
    cast, locs = S.get("cast", []), S.get("locations", [])
    sheet_needed = cast and not all(c.get("sheet") for c in cast) and not S.get("cast_sheet")
    plates_needed = [l for l in locs if l.get("plate", True) and not str(l.get("plate", "")).startswith("http")]
    n = len(S["beats"])
    # ---------- PICTURE-PROMPTS.md ----------
    refs_txt = []
    if cast:
        refs_txt.append("the **cast sheet**" if len(cast) > 1 else "the **character sheet**")
    if plates_needed:
        refs_txt.append("the **location picture** for that scene")
    refs_txt.append("the **layout guide** (`layout-guide.png`) when a scene has no location picture")
    PMs = PRICES["picture"][S.get("picture_model", "standard")]
    L = [f"# Picture prompts — {S.get('title', 'video')}", "",
         f"**{n} pictures**, shape **{asp}** ({S['_fmt']['W']}x{S['_fmt']['H']} or larger, same shape).", "",
         f"These are **exactly** the prompts this production sends to {PMs['label']} when it makes the pictures itself: "
         f"same words, same reference pictures in the same order, same shape. Paste them unchanged (best results with the "
         f"same model, e.g. Nano Banana in Gemini or on fal) so your pictures match the plan with no differences. "
         f"Keep this file: it is how the pictures can be re-made later.", "",
         "## How to make them", "",
         "1. Use any image tool you like (free or paid). Set the shape to **" + asp + "** before you start.",
         "2. Make the Step 0 reference pictures first (if any). Keep them; they are reused for every scene and every future video.",
         "3. If your tool accepts reference images, attach " + ", then ".join(refs_txt) + ", in that order, to each picture. "
         "If it does not, the prompts still describe everything; ignore the lines that mention Image 1/Image 2.",
         "4. Paste one prompt per picture. Re-roll any picture that has writing in it, a band or empty strip across it, "
         "or a character who looks different from the sheet.",
         "5. Save as PNG or JPG named by beat number: " + ", ".join(f"`{b['id']:02d}.png`" for b in S["beats"][:3]) + " ...",
         "6. Put them all in one folder. Then attach them in the chat, or upload the folder to Google Drive, share it as "
         "*Anyone with the link can view*, and paste the link in the chat.", ""]
    if sheet_needed or plates_needed:
        L += ["## Step 0: reference pictures (make these first)", ""]
        if sheet_needed:
            L += ["### cast-sheet.png" if len(cast) > 1 else "### character-sheet.png", "", "```", cast_sheet_prompt(S), "```", ""]
        for l in plates_needed:
            L += [f"### location-{l['id']}.png — {l.get('name', l['id'])}", "", "```", plate_prompt(S, l), "```", ""]
    L += ["## Pictures", ""]
    for b in S["beats"]:
        refs = refs_for(S, b)
        attach = ", ".join({"cast": "cast sheet", "plate": f"location-{(location_of(S, b) or {}).get('id')}.png",
                            "guide": "layout-guide.png"}[k] for k, _ in refs)
        names = {c.get("id"): c.get("name", c.get("id")) for c in cast}
        said = b.get("line") or " / ".join(f"{names.get(ln.get('speaker'), ln.get('speaker') or '')}: {ln['text']}" for ln in b.get("lines") or [])
        L += [f"### {b['id']:02d}.png" + (f" — {said}" if said else ""), "",
              f"Attach: {attach}" if attach else "", "", "```", picture_prompt(S, b, refs), "```", ""]
    open(os.path.join(out, "PICTURE-PROMPTS.md"), "w").write("\n".join(L))
    # ---------- ANIMATION-PROMPTS.md ----------
    L = [f"# Animation prompts — {S.get('title', 'video')}", "",
         "For any image-to-video tool. Use the picture as the FIRST frame. For beats marked *loop*, also use the SAME picture "
         "as the LAST frame (the clip loops cleanly and characters stay on-model). Beats marked *free* have no last frame.", ""]
    PM = PRICES["picture"][S.get("picture_model", "standard")]
    MM_KEY = S.get("motion_model", "standard")
    clips = []
    for b in S["beats"]:
        if S.get("motion_mode", "still") == "still" or b.get("still"):
            continue
        p, loop = motion_prompt(S, b)
        want = b.get("clip_seconds", b["seconds"])
        if MM_KEY == "pro":                       # Kling 2.6 Pro: 5 or 10 s only, no own soundtrack, negative prompt
            dur = 5 if want <= 7 else 10          # up to 7 s: a 5 s clip, then held/looped (cheaper than paying for 10 s)
            inp = {"prompt": p, "start_image_url": f"{{PICTURE_URL_{b['id']}}}", "duration": str(dur),
                   "generate_audio": False, "negative_prompt": S.get("negative_prompt", KLING_NEGATIVE)}
        else:                                     # MiniMax H3: 2-15 s, keeps its own room sound
            dur = max(2, min(15, round(want)))
            inp = {"prompt": p, "image_url": f"{{PICTURE_URL_{b['id']}}}", "duration": dur, "resolution": "768P",
                   "prompt_expansion_mode": "disabled"}
        nxt = next((x for x in S["beats"][S["beats"].index(b) + 1:]), None)
        if b.get("chain") and nxt:                # continuous shot: this picture -> the next picture
            inp["end_image_url"] = f"{{PICTURE_URL_{nxt['id']}}}"
            mode = f"chain: last frame {nxt['id']:02d}.png"
        elif loop:
            inp["end_image_url"] = f"{{PICTURE_URL_{b['id']}}}"
            mode = "loop: last frame = same picture"
        else:
            mode = "free: no last frame"
        L += [f"### {b['id']:02d}.mp4 (first frame {b['id']:02d}.png, {dur} s, {mode})", "", "```", p, "```", ""]
        clips.append({"index": b["id"], "endpoint_id": PRICES["animation"][MM_KEY]["endpoint"], "input": inp})
    open(os.path.join(out, "ANIMATION-PROMPTS.md"), "w").write("\n".join(L))
    # ---------- fal job lists ----------
    res = PM["resolution"]
    refs_jobs = []
    if sheet_needed:
        refs_jobs.append({"name": "cast-sheet", "endpoint_id": PM["t2i"],
                          "input": {"prompt": cast_sheet_prompt(S), "aspect_ratio": "16:9" if len(cast) > 2 else asp,
                                    "resolution": "2K" if len(cast) > 1 else res, "num_images": 1, "output_format": "png"}})
    for l in plates_needed:
        refs_jobs.append({"name": f"location-{l['id']}", "endpoint_id": PM["t2i"],
                          "input": {"prompt": plate_prompt(S, l), "aspect_ratio": asp, "resolution": res,
                                    "num_images": 1, "output_format": "png"}})
    pics = []
    for b in S["beats"]:
        refs = refs_for(S, b)
        urls = [u for _, u in refs]
        pics.append({"index": b["id"], "endpoint_id": PM["endpoint"] if urls else PM["t2i"],
                     "input": {"prompt": picture_prompt(S, b, refs), **({"image_urls": urls} if urls else {}),
                               "aspect_ratio": asp, "resolution": res, "num_images": 1, "output_format": "png"}})
    voice = voice_jobs(S)
    for name, data in (("fal-references.json", refs_jobs), ("fal-pictures.json", pics), ("fal-clips.json", clips),
                       ("fal-voice.json", voice)):
        json.dump(data, open(os.path.join(out, name), "w"), indent=1)
    chars = sum(len(j["input"]["text"]) for j in voice)
    print(f"wrote {out}: PICTURE-PROMPTS.md, ANIMATION-PROMPTS.md, fal-references.json ({len(refs_jobs)}), "
          f"fal-pictures.json ({len(pics)}), fal-clips.json ({len(clips)}), fal-voice.json ({len(voice)} lines, {chars} characters)")


if __name__ == "__main__":
    main()
