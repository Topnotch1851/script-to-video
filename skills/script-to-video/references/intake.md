# Intake: the questions to ask before anything is made

Ask in two short rounds (use a multiple-choice question tool when available, max 4 questions per round).
Always pre-select a suggestion from the script so the person can just say "yes to all". Never ask what the script
already answers. Then show the quote.

## Round 1 — the shape of the video

**1. How long?**
Options: 15 s · 30 s · 60 s · 90 s · 3 min · 5 min · 10 min · other.
Suggest from the script: about 2.3 spoken words per second at a normal pace, 1.5 for young children
(slow, with pauses). Say the estimate: "Your script reads in about 70 seconds."

**2. Vertical or landscape?** (suggest from length)
- Up to 3 minutes → suggest **vertical 9:16** (Shorts, Reels, TikTok).
- Over 3 minutes → suggest **landscape 16:9** (YouTube, Facebook video, websites).
- Square 1:1 on request (feed posts). One render = one shape; a second shape is a second (free) assembly
  but needs pictures made for that shape, so ask early.

**3. Style of video?** Show the menu in `styles.md` (one line each). Suggest one from the topic and audience.
If they name something not on the menu, write a style lock for it in the same pattern.

**4a. Quality level?** Always ask, always with prices, for the motion they chose. Run
`plan_costs.py --seconds N --references R --menu` and show the table: every model level for animated videos
(Budget: Nano Banana 2 + MiniMax · Sharper pictures: Nano Banana Pro + MiniMax · Better motion: Nano Banana 2 + Kling 2.6 Pro
· Premium: Nano Banana Pro + Kling 2.6 Pro) and both picture models for still videos. One line on the difference:
Pro pictures are richer and sharper (2K); Kling acts out whole scenes more convincingly but costs about 4x per second
and only makes 5 s or 10 s clips. Suggest Budget for tests and long videos, Premium for hero Shorts.
Store the answer as `picture_model` / `motion_model` in the shot list.

**4. Still or animated?**
- **Still**: every picture gets a slow, smooth camera move (zoom/pan) made locally for free. Cheapest.
- **Animated**: every picture becomes a short animated clip (the subject moves). Costs the most.
- **Mixed**: animate only the beats that matter (hook, key moments, ending); stills elsewhere. Good for long videos.
Show the price difference right here (`plan_costs.py --compare`).

## Round 2 — who makes what

**5. Pictures: made here, or made by you?**
- **Made here** on fal (about $0.08 each).
- **Made by you** in any tool (free tools included): you get one ready-to-paste prompt per picture, a layout guide and
  naming rules; you upload them (attach, or a shared Google Drive folder). Picture cost here: $0.
- **Your own footage / photos** (real video, product shots, phone clips): no picture cost; they go in as clips or stills.

**6. Who is on screen, and who speaks?** (details in `brief.md`)
- None (scenes only) · one recurring presenter (a character sheet, made once, reused forever) · a cast of 2–4 characters
  (one cast sheet) · a real person with consent (their photo as reference) · the narrator is never seen.
- Speaking: an unseen narrator · one character narrates · dialogue between characters (one voice each).

**7. Voice?**
- AI narrator (pick a voice; offer a 1-line sample of 2–3 voices for a few cents) · their own recording
  (one file per beat, or one file we split) · no narration (music + text only).
- Language and accent. Pace: normal or slow (young children, learners).

**8. Music?**
- New music made for this video (about $0.08 per track; one track per ~2 minutes) · their own track
  (they must own the rights) · none (voice, effects and ambience only).
- Mood in a few words (e.g. "warm marimba, playful", "calm piano", "upbeat electronic").

**9. On-screen text?** Do not assume. Suggest from the style and purpose:
- **None**: pictures, voice and music only (storytelling, cinematic, ASMR, most landscape videos).
- **Subtitles**: the spoken words at the bottom (most social videos are watched without sound) + an .srt file.
- **Key words / titles**: a few big words or a title card per beat (teaching, lists, steps, quotes).
- **Teaching words with timed colour changes and reveals** (phonics, vocabulary, formulas).
Text look: on a soft card, or white with a dark outline straight on the picture.

**10. Audience and platform** (only if not obvious): children / general / professional; which platforms they post to.
Child-directed videos must be marked "made for kids" on YouTube (comments and personalised ads switch off).

## After the answers
Read back one short summary ("60 s vertical, storybook cartoon, animated, pictures made here, AI voice 'Rachel',
new music, teaching words on a card") and the quote table with the spending cap. Ask "Approve the plan and the budget?"

## Defaults when the person says "you choose"
60 s or the script's natural length · shape by length · style from topic · still for anything over 3 minutes,
animated for short hooks · pictures made here · AI voice · new music · subtitles for social, none for landscape
storytelling · prices from a live check.
