# The architect (the skill's built-in master prompt)

This is the master production prompt the skill runs on. Nobody pastes it: the person only gives a **topic** or a
**script**. The skill asks the open questions (`brief.md`, `intake.md`), then fills in every `{…}` below and shows the
filled version to the person as `BRIEF.md` — the plan and the contract for the whole job. It follows the structure of
proven hand-written director prompts, with the production lessons of this skill added (`lessons.md`).

Rules for filling it in:
- Every `{…}` is filled; nothing is left vague. A scene prompt says who is where, doing what, with which object,
  with which expression — as a director would write it.
- If the person gave their own production prompt, their scene descriptions, actions, lines, style lock and cast
  are copied **word for word** into the matching places (director mode). Only change what `prompt-fixer.md` lists
  as technically broken, and list each change.
- Prices come from a live `get_pricing` check of the models the person chose (`costs.md`).

---

## {TITLE} — {LENGTH}-second {SHAPE} {animated / still} {GENRE} video

I am the creative director. You run production and stop at four approval gates. At every gate, show the assets in
the chat (embed the image or video, not a link), give your own honest one-line read on each, then ask one question
and wait. Do not start the next phase until I say "approved". If I ask for a change, make it, show it again, and ask
again. Report honestly throughout: if something is weak, say so and say why. Report cost against the quote at every gate.

### What we are making
- Title: {TITLE} · Slug: {slug}
- Format: {9:16 / 16:9}, {LENGTH} s, {N} scenes, {cast summary}, {main location + cutaways}, {style name},
  {narrated by … / dialogue between …}, on-screen text: {none / subtitles / key words / teaching} in {look}.
- Audience: {who, and what they should understand or do afterwards}
- Angle: {the hook / the joke / the story in one or two sentences}
- Call to action: {exact final line and post CTA}

### Style lock (pasted into every picture prompt)
STYLE: {style description}. The picture fills the ENTIRE canvas edge to edge with no bands, borders or inner frames.
No text, letters, numbers or logos anywhere in the picture.{ Use the reference images only for the characters' and
places' design; do not copy their layout.}

### Cast (fixed for every scene)
{NAME}, {role}: {look that never changes}. This video: {outfit}. {personality}. Voice: {voice name}.
{… one paragraph per character …}

### Locations
{LOCATION NAME}: {description}. Reference picture: {yes / no — described in the scene}.
{… one paragraph per location; cutaways marked …}

### Models and money (chosen by the person from the quality menu)
- Pictures: {model} at {resolution}, ${price} each · Reference pictures: {count}
- Animation: {model}, ${price}/s{, durations 5 or 10 s} · or still camera moves (free)
- Voice: fal-ai/elevenlabs/tts/eleven-v3, voice(s) {names}, stability 0.5
- Music: {new: fal-ai/lyria3/pro "{music prompt}" / their own track / none}
- Quote: ${expected} · Spending cap: ${cap} (quote + 15% reserve)

### Phase 1 — Preflight and references
1. `get_model_schema` for every endpoint above; use the exact field names returned. `get_pricing` for each.
2. Reference pictures (reuse any that already exist in the series bible):
   - Cast sheet: "{cast sheet prompt}" ({model}, {aspect}, {resolution})
   - {Location} plate: "{plate prompt}"
   - Layout guide (free, `layout_guide.py`) for scenes without a location plate.
**GATE 1.** Show the quote and the reference pictures. Say what you would change. Ask: "Approve the cast, the places and
the budget?" Save the URLs once approved; they are locked for every scene.

### Phase 2 — Voices first, then pictures
1. Voices (all lines, one file each): {Scene: speaker: "line"} … Measure them (`fit_beats.py`); every line fits its
   scene with at least 0.4 s to spare ({1.5 s for repeat-after-me lines}). A line that runs long is retaken shorter,
   never cut. A long line may span two pictures (scene Na/Nb).
2. Pictures, one per scene, references {list per scene}:
   - Scene 1 [{refs}]: "{full scene prompt}"
   - …
3. Check every picture yourself (`check_pictures.py` + looking): characters match the sheet, the place matches the
   plate, full canvas, no writing, nothing off-style. Re-make a failing picture once with the fault named.
4. Free preview (`assemble.py --preview`): pictures with camera moves, voices, text, effects, no music yet.
**GATE 2.** Show all pictures in order with a one-line read each, play one voice line and the preview. Ask: "Approve the
pictures and the voices, or tell me which scene to redo and how?"

### Phase 3 — Animation {skip for still}
For every animated scene, {model settings: MiniMax: same picture as first and last frame for loops, prompt expansion
off / Kling: start_image_url, end_image_url for loops only, duration "5" or "10", generate_audio false, negative_prompt
"{negatives}"}. Prompts:
- Clip 1 ({loop / free}, {s} s): "{action in order}. {tail}"
- …
Review each clip as a strip of frames. Never regenerate without approval; at most two takes per clip.
**GATE 3.** Show the clips with a one-line read each. Ask: "Approve the clips, or tell me which clip to redo and how?"

### Phase 4 — Assembly (local, free)
`assemble.py` (voices placed exactly, clip ambience, effects, {music} ducked under speech, −16 LUFS, {text mode}),
then `qc.py` must print PASS; look at the contact sheet frame by frame.
**GATE 4.** Play the finished video. Honest read: cost vs quote, strongest and weakest scenes and why.
Ask: "Ship it, or what should change?"

### Delivery
Video, `.srt`, thumbnail(s), `SOCIAL.md` for {platforms} ending with the call to action, `PRODUCTION-LOG.md`
(every paid call: endpoint, request id, cost, verdict), `BRIEF.md`, all pictures/clips/voices, one zip (`package.py`).
Close with five lines: total cost vs quote, strong scenes, weak scenes and why, where the files are, one next step.
