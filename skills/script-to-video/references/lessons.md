# Lessons already paid for

Each line is a real failure from production and the rule that fixed it. They are built into the tools and prompts;
this list explains why, so nobody "simplifies" them away.

| What went wrong | Rule now |
|---|---|
| Asking the picture model for "empty space at the top" drew a hard pale band across the picture | Frame with a layout guide image; ask for the whole canvas filled |
| The model drew the presenter huge in one beat, ignoring the guide | Name the size in that beat's prompt ("SMALL: one quarter of the picture height"); `subject_size: small` |
| Generated letters scrambled when animated | Never let a model draw text; all text is added at assembly |
| Animated clips drifted off-model and invented marks | Same picture as first and last frame; locked camera; one simple action |
| "magic e" was spoken as "magi-cee" | Separate blending words: "The magic e…" |
| A bare "k" was read as the letter name "kay" | Respell isolated sounds: "kuh", "sss", "nnn" |
| A line ran 5.6 s in a 5 s beat | Measure every line; retake shorter; never cut words |
| Text-to-speech word timestamps drifted from the audio | Time text changes from the measured audio |
| Joining 12 AAC beat files drifted ~45 ms per beat | Build one audio track sample-exact, encode once |
| A hosted ffmpeg service cut scenes short and lost audio | Assemble locally with ffmpeg |
| A preview with placeholder music was mistaken for the final | Previews have no music, and say so |
| The second video opened with the first video's exact line | Series memory: never repeat lines; open with a callback |
| Same outfit and setting every beat looked dull to children | New setting per beat; new outfit colour per video |
| Plain empty strip at the bottom of some pictures | "detail all the way to the bottom edge"; `check_pictures.py` warns |
| Caption pill covered a crouching character's legs | Crouching poses keep the feet a little higher; check frames at every text change |
| Social captions/tags were forgotten in the handoff | SOCIAL.md for every platform is part of every delivery |
| Resubmitting a slow job charged twice | Check the request id; never resubmit |
| Costs ran well over plan on an early video | Quote first, cap = quote + 15%, report at every gate, stop at the cap |
