# Prompt fixer: correct any production prompt before running it

People will paste old prompts, prompts written for other tools, or prompts from someone else. Never run them as-is.
Rewrite them into the standard below, show **what you changed and why** in a short list, and ask for "approved".
Keep everything that is the person's creative choice (script, characters, style, words, colours) unless it breaks a
rule here; then say so and offer the fix.

## Checklist (fix every item that applies)
| Found in the prompt | Replace with |
|---|---|
| Other picture/video/voice/music models or old prices | the endpoints and live prices in `costs.md` (keep theirs only if they insist; then quote at their prices) |
| A fixed money cap (e.g. "$8 per video") | a cap from the live quote: expected total + 15% reserve |
| "Leave the top third / bottom fifth empty", "blank paper zones" | layout guide image + "fills the whole canvas" (blank-zone prompts produced hard bands) |
| Words, letters or numbers drawn by the model | removed; text is added at assembly, and only if the chosen text mode needs it |
| Text always on screen | the text mode the person chose (none / subtitles / key words / teaching) |
| Assembly on a hosted ffmpeg service | local `assemble.py` (hosted joins cut scenes short and lost sync) |
| Cue timing from text-to-speech timestamps | cue timing from the measured audio |
| No music / no sound effects / no ambience / no loudness target | music choice, free effects, clip ambience, −16 LUFS |
| No pilot, no approval gates, no cost reporting | the gates in SKILL.md, spend reported at each gate |
| Character described differently from the existing sheet (pronouns, clothes, features) | aligned to the sheet / series bible; flag the conflict |
| Same setting or outfit in every beat | a different setting per beat; a new outfit colour per video |
| Lines or openings repeated from earlier videos in a series | new lines; open with a callback to the last video (`series.md`) |
| Isolated sounds or blending words in narration | respellings and pauses (`sound.md`) |
| A delivery path on someone's computer | a zip sent in the chat (plus the folder if their computer is connected) |
| Only one platform's caption | `SOCIAL.md` for every platform they post on (`handoff.md`) |
| Clips regenerated automatically | never without approval; max two takes |
| Captions or labels drawn inside the pictures ("caption rendered exactly", "labelled CALENDAR") | captions added at assembly (`caption_box: "tv"` for the yellow subtitle look); labels become icons or objects, or on-screen text at assembly |
| Reference sheets "labelled in small letters" | no labels on sheets (the model copies them into scenes) |
| Cast + room plate + cutaway structure | keep it: `cast`, `locations` with plates, cutaways described per scene |
| Long action clips (10 s) with several gags | keep them as free clips (`"loop": false`, `clip_seconds`) |
| Fixed narration timing per clip | voices first, then `fit_beats.py` sets scene lengths |

## Output format
1. **What I changed** — 5–12 bullets, plain words.
2. **The corrected prompt** — in the structure of `MASTER-PROMPT.md` with the script and answers filled in.
3. **Quote** — from `plan_costs.py`.
4. Ask: "Approve the corrected prompt and budget?"
