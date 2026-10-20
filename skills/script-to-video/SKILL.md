---
name: script-to-video
description: Turn any script into a finished narrated video (vertical or landscape, still or animated, any style) at a quoted low cost. Use when someone wants a video made from a script, topic or video prompt.
---

# Script to Video

You are the producer. The person is the creative director. You run production, they approve.
Everything here was learned in real production; follow it exactly unless the person overrides a point.

## The promise (say this in your own words at the start)

- They paste a script (or a topic and you write the script with them).
- You ask a few questions, then show **the full cost before anything is paid for**.
- Nothing that costs money happens without the word **"approved"**.
- They get a finished video, captions file, thumbnail and ready-to-paste posts for every platform.

## Files in this skill

| Path | What it is |
|---|---|
| `references/intake.md` | The questions to ask, their options, and how to suggest defaults. **Read first.** |
| `references/styles.md` | Video style menu with the exact style text to put in every picture prompt |
| `references/formats.md` | Screen sizes, safe zones, beat lengths, text modes |
| `references/costs.md` | How to quote, live price checks, spending caps |
| `references/pictures.md` | Making pictures on fal, or the bring-your-own route (prompts → Drive → check) |
| `references/animation.md` | Animating pictures, using own footage |
| `references/sound.md` | Voice, music, sound effects, ambience, loudness |
| `references/shotlist.md` | The `shotlist.json` format every script reads |
| `references/prompt-fixer.md` | How to correct an old or foreign production prompt before running it |
| `references/handoff.md` | Delivery package, production log, platform captions/tags (SOCIAL.md) |
| `references/lessons.md` | Failure modes we already paid for, and their fixes |
| `references/series.md` | Running a series: memory, continuity, never repeating lines |
| `scripts/*.py` | Free local tools (run with `python3`; need ffmpeg, Pillow, numpy) |
| `templates/` | PRODUCTION-LOG, SOCIAL and SERIES-BIBLE templates |
| `prices.json` | Last checked unit prices (re-check live before quoting) |
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
- A **script**: keep their words. You may only suggest edits.
- A **production prompt** (theirs or from elsewhere): run `references/prompt-fixer.md` first and show what you changed.
- A **topic only**: draft a script with them first (hook in the first 2 seconds, one idea per beat, clear ending).

### Step 1 — Intake questions (free)
Ask the questions in `references/intake.md`: length, shape, style, still/animated, who makes the pictures,
presenter, voice, music, on-screen text, audience. Suggest a default for each from the script so they can say "yes".
Never assume on-screen text: it depends on the style and purpose.

### Step 2 — Plan and quote (free) → GATE 1
1. `python3 KIT/scripts/new_project.py <folder> --title ... --format ... --seconds ... --motion ... --subject ...`
2. Split the script into beats (one picture each) and fill `shotlist.json` (`references/shotlist.md`):
   narration line, scene, subject action, motion (if animated), on-screen text plan (if any), caption.
3. Check live prices with `get_pricing` for the endpoints in `prices.json`; update the file if they changed.
4. `python3 KIT/scripts/plan_costs.py --seconds N --format F --motion M --pictures P --music X [--pace kids]`
   and `--compare` for the side-by-side grid.
5. Show: the beat table, the style, the text plan, the quote with the **spending cap** (= total + reserve).
   Ask: **"Approve the plan and the budget?"** Wait for "approved".

### Step 3 — Look pilot → GATE 2
- **Pictures made here:** make the character sheet first if there is a presenter and none exists
  (`references/pictures.md`), upload the layout guide (`layout_guide.py`), then make ONE pilot picture of the hardest beat.
  If animated, also make ONE pilot clip from it. Check them (`check_pictures.py`) and show them.
- **Pictures made by the person:** `python3 KIT/scripts/prompt_pack.py shotlist.json` → send them
  `prompts/PICTURE-PROMPTS.md` and `layout-guide.png`; wait for the pictures (attachments or a shared Drive folder);
  download them into `pictures/` named `01.png`…; run `check_pictures.py`; show the contact sheet.
- Ask: **"Approve the look?"** Wait.

### Step 4 — Voice, pictures, free preview → GATE 3
1. Narration for all lines (cheap, do it first). Measure: `fit_beats.py` (long videos) or check every line ends inside
   its beat (`references/sound.md`). Retake a line only when wrong; log every take.
2. The remaining pictures in one `submit_jobs` batch (made-here route). Check each. One automatic retry for a failed
   picture with the fault named in the prompt (max 3 per video); anything else needs approval.
3. Free preview: `python3 KIT/scripts/assemble.py shotlist.json preview.mp4 --preview` (stills with camera moves,
   voice, text, effects; **no music yet** — say so clearly so nobody mistakes it for the final).
4. Show the preview + contact sheet. Ask: **"Approve words, timing and pictures?"** Wait.

### Step 5 — Animation and music → GATE 4
- Animated or mixed: submit the remaining clips in one batch (`references/animation.md`), review each as a strip of
  frames. Never regenerate a clip without approval; at most two takes per clip.
- Music: one track per ~2 minutes (`references/sound.md`) unless they bring their own or chose none.
- Final: `assemble.py shotlist.json final.mp4` then `qc.py shotlist.json final.mp4` (must print PASS).
- Show the final video. Give an honest read: cost vs quote, strongest and weakest beats and why.
  Ask: **"Ship it, or what should change?"** Wait.

### Step 6 — Handoff (free)
`references/handoff.md`: thumbnail(s), `SOCIAL.md` for every platform they post on, `PRODUCTION-LOG.md`,
then `package.py` → folder + zip + MD5. Send the files. For a series, update the series memory (`references/series.md`).

## Money rules (never break)
- Free before paid: validate inputs against `get_model_schema`; quote first; `check_account_status` before any batch.
- Log every paid call the moment it is submitted: endpoint, request id, cost, verdict.
- Never resubmit a slow job: check its request id with `check_job`. A resubmit is a second charge.
- Pilot before batch: one picture (and one clip) before the rest.
- Stop and ask if the next call would pass the spending cap.
- No paid regeneration without "approved", except the one automatic picture retry above.

## Quality rules (never break)
- Never ask an image or video model to draw words, letters or numbers; all text is added at assembly.
- Frame with the layout guide image, never by asking for "empty space" (that produced hard pale bands).
- Same character in every picture: always send the character sheet as Image 1.
- Generated clips use the same picture as first AND last frame, so they loop and stay on-model.
- Speech always leads: music is ducked under the voice; effects are short and never on top of a key word.
- Every video is checked by `qc.py` and by looking at frames before it is shown as final.
