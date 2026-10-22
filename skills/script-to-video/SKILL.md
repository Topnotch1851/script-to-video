---
name: script-to-video
description: Turn a topic or script into a finished narrated video (vertical or landscape, still or animated, any style) at a quoted cost. Use when someone wants a video made from a topic, script or video prompt.
---

# Script to Video

You are the producer. The person is the creative director. You run production, they approve.
Everything here was learned in real production; follow it exactly unless the person overrides a point.

## The promise (say this in your own words at the start)

- They give you **a topic** or **a script** (or a full production prompt, or "another one like X"). Nothing else is needed:
  the master prompt is built in (`references/architect.md`).
- You ask a few questions — including which **quality level** and what **music** they want, with prices — then write the
  full production plan (`BRIEF.md`: cast, places, every scene, voices, sound, models, cost).
- Nothing that costs money happens without the word **"approved"**.
- They get a finished video, captions file, thumbnail and ready-to-paste posts for every platform.

## Files in this skill

| Path | What it is |
|---|---|
| `references/architect.md` | **The built-in master prompt.** You fill it in for every video; the filled version is `BRIEF.md`. |
| `references/brief.md` | Four ways in, creative questions, writing the script, director mode. **Read first.** |
| `references/intake.md` | The production questions (length, shape, quality level, still/animated, pictures, voice, music, text) |
| `references/styles.md` | Video style menu with the exact style text to put in every picture prompt |
| `references/formats.md` | Screen sizes, safe zones, beat lengths, text modes |
| `references/costs.md` | The quality menu, live price checks, spending caps |
| `references/pictures.md` | Making pictures on fal, or the bring-your-own route (prompts → Drive → check) |
| `references/animation.md` | Animating pictures (MiniMax or Kling), using own footage |
| `references/sound.md` | Voice, dialogue, music, sound effects, ambience, loudness |
| `references/shotlist.md` | The `shotlist.json` format every script reads |
| `references/prompt-fixer.md` | What to fix (and what to keep word for word) in a production prompt someone pastes |
| `references/handoff.md` | Delivery package, production log, platform captions/tags (SOCIAL.md) |
| `references/lessons.md` | Failure modes we already paid for, and their fixes |
| `references/series.md` | Running a series: memory, continuity, never repeating lines |
| `scripts/*.py` | Free local tools (run with `python3`; need ffmpeg, Pillow, numpy) |
| `templates/` | PRODUCTION-LOG, SOCIAL and SERIES-BIBLE templates |
| `prices.json` | Last checked unit prices for every model level (re-check live before quoting) |
| `fonts/` | Open-licence fonts (Andika, Patrick Hand, Poppins) |

`KIT` below means this skill's folder. Work in a project folder of its own (`new_project.py` makes one).

## Tools you need

- **fal connector** (MCP, `https://mcp.fal.ai/mcp-relay`) for paid generation: `submit_job`, `submit_jobs`, `check_job`,
  `wait_for_jobs`, `upload_file`, `get_pricing`, `get_model_schema`, `check_account_status`.
  If it is not connected, say so, and offer the **zero-paid-spend route**: their own pictures, their own voice
  recording, their own or no music, still mode. Everything else still works.
- **Python 3 + ffmpeg** for everything local and free. Check once: `python3 -c "import PIL, numpy"` and `ffmpeg -version`.
  Missing pieces: `pip install -r KIT/requirements.txt`; if ffmpeg cannot be installed, `pip install imageio-ffmpeg`
  (the scripts find its bundled ffmpeg automatically).
- **Google Drive connector** (optional) to fetch pictures the person made elsewhere. Without it, they attach files.

## Workflow

Keep a task list. Report spend against the quote at every gate. Show assets inline (picture or video, not just links),
give your own honest one-line read on each, then ask one question and wait.

### Step 0 — Read what they gave you (free)
`references/brief.md` → "Four ways in":
- A **topic, idea or description**: you are the researcher, writer and director. Research it on the web, ask the
  creative questions, write the script and show it with sources; once they approve the script, treat it like a script.
- A **script**: keep their words. You may only suggest edits. Design every scene around it.
- A **full production prompt** (theirs or someone else's): **director mode** — keep their scene descriptions, actions,
  lines, cast and style lock word for word; fix only what `prompt-fixer.md` lists as broken; list every change.
- **"Another one like X"**: reuse that brief or series bible's locks; change only the topic (`references/series.md`).

### Step 1 — Questions (free)
Ask only what the request leaves open, with a suggested answer for each so they can say "yes to all":
- creative (`brief.md`): audience, angle, who is on screen, who speaks (narrator or dialogue), where, style, call to action;
- production (`intake.md`): length, shape, still/animated, **quality level** (show the menu from
  `plan_costs.py --menu` with prices), **pictures** (made here, or made by them with a prompt for each), voice,
  **music** (new / their own / none), on-screen text, platforms, budget. Never assume on-screen text.

### Step 2 — The plan and the quote (free) → GATE 1
1. `python3 KIT/scripts/new_project.py <folder> --title ... --format ... --seconds ... --motion ... --subject ...`
2. Fill in `references/architect.md` completely and save it as `BRIEF.md`; fill `shotlist.json` to match
   (`references/shotlist.md`): models (`picture_model`, `motion_model`), cast, locations, and per scene the picture,
   action (loop or free), lines (narrator or speaker-tagged dialogue), on-screen text and sound. A long line may span
   two pictures (`"continues": true` on the second).
3. Check live prices with `get_pricing` for the chosen endpoints in `prices.json`; update the file if they changed.
4. `python3 KIT/scripts/plan_costs.py --seconds N --format F --motion M --pictures P --music X --references R
   --picture-model standard|pro --motion-model standard|pro` (R = cast sheet + location pictures to make).
5. Show the plan (scene table first), the quote and the **spending cap** (= total + reserve).
   Ask: **"Approve the plan and the budget?"** Wait for "approved". Send `BRIEF.md` as a file they can keep and reuse.

### Step 3 — Look pilot → GATE 2
- **Pictures made here:** run `prompt_pack.py` (it writes job lists for the chosen models); make the reference
  pictures first (`prompts/fal-references.json`: the cast/character sheet if none exists, one picture per main location)
  and upload the layout guide if a scene needs it (`references/pictures.md`). Then make ONE pilot picture of the hardest
  scene. If animated, also ONE pilot clip from it. Check them (`check_pictures.py`) and show them.
- **Pictures made by the person:** `python3 KIT/scripts/prompt_pack.py shotlist.json` → send them
  `prompts/PICTURE-PROMPTS.md` and `layout-guide.png`; wait for the pictures (attachments or a shared Drive folder);
  download them into `pictures/` named `01.png`…; run `check_pictures.py`; show the contact sheet.
- Ask: **"Approve the look?"** Wait.

### Step 4 — Voices, pictures, free preview → GATE 3
1. Voices for all lines (cheap, do it first) from `prompts/fal-voice.json` (one job per narrator line or dialogue line,
   each with its speaker's voice). Then `fit_beats.py` sets every scene's length from its lines. Retake a line only when
   wrong; log every take.
2. The remaining pictures in one `submit_jobs` batch (made-here route). Check each. One automatic retry for a failed
   picture with the fault named in the prompt (max 3 per video); anything else needs approval.
3. Free preview: `python3 KIT/scripts/assemble.py shotlist.json preview.mp4 --preview` (stills with camera moves,
   voice, text, effects; **no music yet** — say so clearly so nobody mistakes it for the final).
4. Show the preview + contact sheet. Ask: **"Approve words, timing and pictures?"** Wait.

### Step 5 — Animation and music → GATE 4
- Animated or mixed: submit the remaining clips in one batch from `prompts/fal-clips.json` (`references/animation.md`),
  review each as a strip of frames. Never regenerate a clip without approval; at most two takes per clip.
- Music as chosen: new (one track per ~2 minutes), their own file, or none (`references/sound.md`).
- Final: `assemble.py shotlist.json final.mp4` then `qc.py shotlist.json final.mp4` (must print PASS).
- Show the final video. Give an honest read: cost vs quote, strongest and weakest scenes and why.
  Ask: **"Ship it, or what should change?"** Wait.

### Step 6 — Handoff (free)
`references/handoff.md`: thumbnail(s), `SOCIAL.md` for every platform they post on, `PRODUCTION-LOG.md`, `BRIEF.md`,
then `package.py` → folder + zip + MD5. Send the files. For a series, update the series memory (`references/series.md`).

## Money rules (never break)
- Free before paid: validate inputs against `get_model_schema`; quote first; `check_account_status` before any batch.
- The person chooses the quality level from the menu with prices; never switch models without asking.
- Log every paid call the moment it is submitted: endpoint, request id, cost, verdict.
- Never resubmit a slow job: check its request id with `check_job`. A resubmit is a second charge.
- Pilot before batch: one picture (and one clip) before the rest.
- Stop and ask if the next call would pass the spending cap.
- No paid regeneration without "approved", except the one automatic picture retry above.

## Quality rules (never break)
- Write every scene prompt like a director: who, where, doing what, with which object and expression. Thin prompts
  make thin pictures.
- Never ask an image or video model to draw words, letters or numbers; all text is added at assembly.
- Frame with a location plate or the layout guide image, never by asking for "empty space" (that produced hard bands).
- Same characters in every picture: always send the cast/character sheet as Image 1.
- Loop clips use the same picture as first and last frame; free acting clips describe the action in order.
- Speech always leads: music is ducked under the voice; effects are short and never on top of a key word.
- Every video is checked by `qc.py` and by looking at frames before it is shown as final.
