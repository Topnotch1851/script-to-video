# Handoff: what the person receives

## The package (`package.py`)
`deliver/<slug>/` and `deliver/<slug>.zip` containing:
- `<slug>.mp4` (+ MD5 in README.txt) and `<slug>.srt` (captions; upload to YouTube as subtitles)
- `thumbnails/` — `thumbnail.py`: `youtube` 1280x720 for landscape; `vertical` cover for Shorts/Reels
- `SOCIAL.md` — ready-to-paste posts (below)
- `PRODUCTION-LOG.md` — every paid call (endpoint, request id, cost, verdict), totals vs quote, what to fix next time
- `shotlist.json`, `prompts/`, `pictures/`, `clips/`, `voice/`, `music/`, `layout-guide.png` (so anything can be rebuilt)
Send the zip and the video with the file-sending tool. Never paste huge file contents in the chat.

## SOCIAL.md — always, for every platform they use
Write fresh copy for each video (never reuse the last one). Plain, warm, specific; no hype words.
Use `templates/SOCIAL-template.md`. Per platform:

**Instagram (Reels)** — caption 1–3 short sentences + a call to action (save / share / comment);
**at most 5 hashtags** (Instagram's current limit); a comment to pin.

**TikTok** — a hook caption (first line works alone), 3–5 hashtags, a comment to pin (often a question or a teaser).

**YouTube Shorts** — title under 100 characters (first ~50 show), ends with #Shorts; description (2–4 lines);
3 hashtags; tags field (comma-separated, under 500 characters); settings checklist:
audience ("Yes, it's made for kids" when aimed at children — required by law, turns off comments and personalised ads),
playlist, category, captions file, **altered or synthetic content: Yes** when realistic AI people/places appear.

**YouTube (long-form)** — title (~60 characters), description with a 2-line summary first, **chapters**
(from `_work/chapters.txt` when beats have a `"chapter"` name; the first chapter is 00:00, at least 3 chapters,
each at least 10 s), tags, end-screen/cards suggestion, thumbnail text (2–5 words), the same settings checklist.

**Facebook** — a slightly longer caption (2–4 sentences, speaks to the viewer), a question to invite comments,
up to 3 hashtags.

**AI labels** — realistic AI-made people or events: YouTube "altered or synthetic content", TikTok "AI-generated" label,
Meta "AI info". Cartoon and clearly stylised content usually does not need it; when in doubt, label.

## The closing message
Five lines: total cost vs quote · what is strongest · what is weakest and why · where the files are · one next step.
