# Sound: voice, music, effects, ambience, loudness

## Voice (AI)
- Endpoint `fal-ai/elevenlabs/tts/eleven-v3`. Fields: `text`, `voice` (a NAME, not an ID), `stability` 0.5,
  optional `language_code` (ISO 639-1, e.g. "fr"). One voice for a whole video (and a whole series).
- Voice names include: Rachel (calm female, default), Aria, Sarah, Laura, Charlotte, Alice, Matilda, Jessica, Lily,
  Roger, Charlie, George, Callum, River, Liam, Will, Eric, Chris, Brian, Daniel, Bill. Check the live list in the schema.
  Offer 2–3 one-line samples (fractions of a cent each) before choosing.
- One file per beat: `voice/NN.mp3`. Generate all lines in one batch (they are the cheapest item), then measure.

### Writing for the voice (learned the hard way)
- Isolated sounds are respelled: "sss", "nnn", "fff", "kuh" (a bare "k" is read as the letter name "kay").
- Words that blend get a pause: "The magic e…" or "magic… e" (plain "magic e" came out as "magi-cee").
- Ellipses make pauses: "Say it with me… cake!". Short sentences beat long ones.
- Numbers, symbols and abbreviations: write them as words if pronunciation matters.
- Bracketed delivery hints (e.g. "[softly]") work but can occasionally be spoken; check by ear.

### Timing
- Every line must end inside its beat with a little air: vertical 5 s beats end by about 4.6 s.
- Repeat-after-me lines keep at least 1.5 s of silence at the end: set `"answer_gap": 1.5` (ends by 3.4 s).
- Long videos: `python3 KIT/scripts/fit_beats.py shotlist.json` sets every beat's length from its line.
- A line that runs long is retaken shorter or split; never squeezed or sped up.

## Several voices (dialogue, or a character who narrates)
- Each cast member gets a voice name in the cast list (pick voices that sound clearly different: age, pitch, accent).
  Offer a one-line sample of each before the batch.
- Each spoken line is its own file (`prompts/fal-voice.json` has one job per line with the right voice).
- Lines in a scene are placed one after another with a 0.25 s gap (or at a set `"at"` time); `fit_beats.py` lengthens
  the scene to fit. Keep dialogue scenes to 2–3 short lines.
- It is voice-over: characters act in the pictures and clips, but mouths are not lip-synced. Write scenes so that works
  (reactions, gestures, the speaker turned toward the other character).

## Voice (their own recording)
One file per beat in `voice/`, or one long file split at the pauses:
`python3 KIT/scripts/split_voice.py recording.wav --beats N --out voice/`. Quiet rooms, phone close to the mouth.

## Music
- New: `fal-ai/lyria3/pro`, $0.08 per track. Prompt pattern:
  "Instrumental background music for a [audience] video about [topic]. [mood], [instruments], about [N] BPM,
  no vocals, no singing, steady and light under a speaking voice, gentle start, soft ending, about 60 seconds."
  A track runs about a minute; `assemble.py` loops and cross-fades tracks to any length. For videos over ~2 minutes,
  make one track per ~2 minutes for variety. New music every video in a series.
- Own track: they confirm they own the rights or it is licensed for this use; put it in `music/`.
- None: allowed; effects and ambience still play.
- In the shot list: `"music": [{"file": "music/bed.mp3"}]`.

## Sound effects (free, synthesised: `scripts/sfx.py`)
pop, plink, sparkle, boing, whoosh, swoosh_up, soft_down, click, tick, chime, ding, thud.
- Automatic (default on): a pop when on-screen text appears, rising plinks on text reveals and list items.
- Explicit per beat: `"sfx": [{"at": 0.55, "sound": "whoosh", "db": -9}]`; `"transition": "whoosh"` at a beat start.
- Never put an effect on top of a key spoken word, and nothing inside an answer gap.
- Turn off with `"auto_sfx": false` (whole video) or `"no_auto_sfx": true` (one beat).

## Ambience
Animated clips bring their own room sound; it is levelled to `ambience_db` (default −36 dB) so every beat has a
gentle, even background. Own footage with real sound: `"clip_audio": "full"`.

## Mix and loudness (assemble.py does all of this)
- Speech leads. Music sits `music_db` (−14 dB) under the voice and ducks a further `duck_db` (8 dB) while anyone speaks.
- Effects peak about 18 dB under full scale.
- Final loudness `loudness` −16 LUFS integrated, true peak −1.5 dBTP (social apps and YouTube normalise near −14,
  so this plays at full level with headroom).
- One audio track is built sample-exact and encoded once (per-beat encoding drifted ~45 ms per beat in production).
