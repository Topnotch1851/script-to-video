"""Turn a shot list into ready-to-use prompts (free).

Writes, next to the shot list:
  prompts/PICTURE-PROMPTS.md    one copy-paste prompt per picture, plus the character-sheet prompt and how to
                                save/name/upload the files (for people making pictures in any other tool)
  prompts/ANIMATION-PROMPTS.md  one motion prompt per beat (for any image-to-video tool)
  prompts/fal-pictures.json     fal job list for nano-banana-2/edit (placeholders {SHEET_URL} {GUIDE_URL})
  prompts/fal-clips.json        fal job list for minimax h3 (placeholder {PICTURE_URL_<id>})

Shot list fields used: style_lock, character{name, description, keep, outfit, sheet}, guide_subject,
beats[].scene, beats[].action, beats[].motion, beats[].subject_size ("normal"|"small"|"close").
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
MOTION_TAIL = {
    "loop": ("Locked camera, fixed shot. The subject stays the same size and shape and keeps the same face, clothes and colours. "
             "Nothing new appears, no text appears. The subject returns to the starting pose at the end."),
    "free": "Smooth, natural motion. The subject keeps the same face, clothes and colours. No text appears.",
}


def size_note(b, fmt, has_char):
    who = "the main subject"
    if b.get("subject_size") == "small":
        return f"Keep {who} SMALL: about one quarter of the picture height, standing on the ground line shown in the layout guide."
    if b.get("subject_size") == "close":
        return f"Show {who} closer (waist up), still centred, head at the same height as in the layout guide."
    return ""


def picture_prompt(S, b, refs):
    ch = S.get("character")
    parts = ["Draw a NEW picture." if S.get("look", "illustrated") != "photo" else "Create a NEW photograph."]
    k = 1
    if ch and refs.get("sheet"):
        keep = ch.get("keep", "face, hair, body shape, line style and colours")
        outfit = ch.get("outfit")
        parts.append(f"Image {k} is the character design of {ch.get('name', 'the presenter')}: {ch['description']} "
                     f"Keep the {keep} exactly like Image {k}." + (f" This time the outfit is: {outfit}." if outfit else ""))
        k += 1
    elif ch:
        parts.append(f"The main character, {ch.get('name', 'the presenter')}: {ch['description']}" +
                     (f" Outfit: {ch['outfit']}." if ch.get("outfit") else ""))
    subj = S.get("guide_subject", "person")
    if refs.get("guide"):
        if subj == "object":
            parts.append(f"Image {k} is a LAYOUT GUIDE ONLY. Make the main subject the same SIZE and POSITION as the grey shape "
                         f"in Image {k}: same height on the canvas, centred horizontally, resting on the same ground line. "
                         f"Do not copy its shape, colours or plain background.")
        else:
            who = "figures" if subj == "group" else "figure"
            parts.append(f"Image {k} is a LAYOUT GUIDE ONLY. Copy exactly the SIZE and POSITION of the grey {who} in Image {k}: "
                         f"same height on the canvas, centred horizontally, head at the same place, standing on the same ground line. "
                         f"Do not copy the pose, colours or plain background.")
    cap = lambda s: s[:1].upper() + s[1:]
    parts.append("Scene: " + cap(b["scene"].rstrip(".")) + "." + (" " + cap(b["action"].rstrip(".")) + "." if b.get("action") else ""))
    sn = size_note(b, S["format"], bool(ch))
    if sn:
        parts.append(sn)
    if subj in ("person", "group"):
        parts.append("Any object or animal stays beside the subject with its bottom on the same ground line, never below the feet.")
    parts.append(FULL_CANVAS)
    parts.append("Style: " + S.get("style_lock", "clean, bright, detailed illustration").rstrip(".") + ".")
    parts.append(NO_TEXT)
    return "\n\n".join(parts)


def motion_prompt(S, b):
    m = b.get("motion") or "gentle idle movement: the subject breathes, blinks and shifts weight slightly"
    return m.rstrip(".") + ". " + MOTION_TAIL[S.get("motion_style", "loop")]


def main():
    S = load_shotlist(sys.argv[1])
    out = os.path.join(S["_root"], "prompts"); os.makedirs(out, exist_ok=True)
    asp = S["_fmt"]["aspect"]
    ch = S.get("character")
    refs_gen = {"sheet": bool(ch), "guide": S.get("guide_subject", "person") != "none"}
    n = len(S["beats"])
    # ---------- PICTURE-PROMPTS.md (bring-your-own route) ----------
    L = [f"# Picture prompts — {S.get('title', 'video')}", "",
         f"**{n} pictures**, shape **{asp}** ({S['_fmt']['W']}x{S['_fmt']['H']} or larger, same shape).", "",
         "## How to make them", "",
         "1. Use any image tool you like (free or paid). Set the shape to **" + asp + "** before you start.",
         ("2. If your tool accepts reference images, attach the **character sheet** first and the **layout guide** "
          "(`layout-guide.png`) second to every picture. They keep the presenter the same and the framing right."
          if ch else
          "2. If your tool accepts reference images, attach the **layout guide** (`layout-guide.png`) to every picture; "
          "it keeps the framing right. If it does not, ignore the line about the layout guide in each prompt."),
         "3. Paste one prompt per picture. Make one picture per prompt. Re-roll any picture that has writing in it"
         + (", a band or empty strip across it, or a presenter who looks different." if ch else " or a band or empty strip across it."),
         "4. Save as PNG or JPG named by beat number: " + ", ".join(f"`{b['id']:02d}.png`" for b in S["beats"][:3]) + " ...",
         "5. Put them all in one folder. Then either attach them in the chat, or upload the folder to Google Drive, "
         "share it as *Anyone with the link can view*, and paste the link in the chat.", ""]
    if ch and not ch.get("sheet"):
        L += ["## Step 0: character sheet (make this first, reuse it for every picture)", "", "```",
              f"Character reference sheet for an animation. One character named {ch.get('name', 'the presenter')}: {ch['description']} "
              f"Show the same character four times in a row on a plain light background: standing front view, walking side view, "
              f"pointing up and to the side with one arm, sitting. Same size in all four. No labels. "
              f"Style: {S.get('style_lock', '')} {NO_TEXT}", "```", ""]
    L += ["## Pictures", ""]
    for b in S["beats"]:
        L += [f"### {b['id']:02d}.png" + (f" — {b['line']}" if b.get("line") else ""), "", "```", picture_prompt(S, b, refs_gen), "```", ""]
    open(os.path.join(out, "PICTURE-PROMPTS.md"), "w").write("\n".join(L))
    # ---------- ANIMATION-PROMPTS.md ----------
    L = [f"# Animation prompts — {S.get('title', 'video')}", "",
         "For any image-to-video tool. Use the picture as the FIRST frame and, where the tool allows it, the SAME picture "
         "as the LAST frame: the clip then loops cleanly and the presenter stays on-model. Length 5 s unless noted.", ""]
    for b in S["beats"]:
        L += [f"### {b['id']:02d}.mp4 (from {b['id']:02d}.png, {b['seconds']:.0f} s)", "", "```", motion_prompt(S, b), "```", ""]
    open(os.path.join(out, "ANIMATION-PROMPTS.md"), "w").write("\n".join(L))
    # ---------- fal job lists ----------
    pics = []
    for b in S["beats"]:
        urls = (["{SHEET_URL}"] if refs_gen["sheet"] else []) + (["{GUIDE_URL}"] if refs_gen["guide"] else [])
        pics.append({"index": b["id"], "endpoint_id": "fal-ai/nano-banana-2/edit" if urls else "fal-ai/nano-banana-2",
                     "input": {"prompt": picture_prompt(S, b, refs_gen), **({"image_urls": urls} if urls else {}),
                               "aspect_ratio": asp, "resolution": "1K", "num_images": 1, "output_format": "png"}})
    json.dump(pics, open(os.path.join(out, "fal-pictures.json"), "w"), indent=1)
    clips = []
    for b in S["beats"]:
        if S.get("motion_mode", "still") == "still" or b.get("still"):
            continue
        dur = max(2, min(15, round(b["seconds"])))
        clips.append({"index": b["id"], "endpoint_id": "minimax/h3-max-turbo/image-to-video",
                      "input": {"prompt": motion_prompt(S, b), "image_url": f"{{PICTURE_URL_{b['id']}}}",
                                "end_image_url": f"{{PICTURE_URL_{b['id']}}}", "duration": dur,
                                "resolution": "768P", "prompt_expansion_mode": "disabled"}})
    json.dump(clips, open(os.path.join(out, "fal-clips.json"), "w"), indent=1)
    print(f"wrote {out}/PICTURE-PROMPTS.md, ANIMATION-PROMPTS.md, fal-pictures.json ({len(pics)}), fal-clips.json ({len(clips)})")


if __name__ == "__main__":
    main()
