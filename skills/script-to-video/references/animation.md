# Animation

## Premium motion: Kling 2.6 Pro (`fal-ai/kling-video/v2.6/pro/image-to-video`, $0.07/s)
| Field | Value | Why |
|---|---|---|
| `start_image_url` | the picture's URL | first frame |
| `end_image_url` | the same URL for *loop* scenes; the next picture for *chain* scenes; none for free acting | keeps characters on-model |
| `duration` | `"5"` or `"10"` (strings, nothing else) | scenes up to 7 s use 5 s and hold/loop; longer use 10 s |
| `generate_audio` | `false` | Kling would add its own voices; the skill builds the soundtrack |
| `negative_prompt` | "blur, distortion, extra limbs, extra characters, morphing faces, new text appearing, morphing text, garbled letters, photorealism, colour shifts, camera shake" | the locks proven in hand-written director prompts |
Kling handles multi-step acting (jabs, slumps, objects arriving) better than MiniMax; describe the action in order.

## Budget motion: settings that work (`minimax/h3-max-turbo/image-to-video`)
| Field | Value | Why |
|---|---|---|
| `image_url` | the picture's URL | first frame |
| `end_image_url` | **the same URL** | the clip returns to the start: seamless loop, character stays on-model, no invented marks |
| `duration` | beat length, 2–15 s (5 for vertical) | billed per second; output can run ~0.2–0.7 s longer |
| `resolution` | `768P` | sharp enough after upscaling to 1080; `1080P` costs the same per second but is slower |
| `prompt_expansion_mode` | `disabled` | keeps your exact motion description |

Clips arrive with their own ambient sound. `assemble.py` keeps it quietly as room tone (`ambience_db`, default −36 dB).

## Loop or free
- **Loop** (default): first and last frame are the same picture. The subject does one simple action and returns to the
  start. Safest for presenters and teaching; clips repeat seamlessly if the scene is longer than the clip.
- **Free** (`"loop": false`): no last frame. Use for acting scenes where something happens — a gag, a reaction, an object
  arriving. Give `clip_seconds` (up to 15) for longer actions, describe the action in order ("jabs the remote three times,
  slumps back, Ellie raises an eyebrow"), keep the camera mostly locked. Review these more carefully for drifting faces.

## Motion prompts
`prompt_pack.py` writes them to `prompts/fal-clips.json` and `prompts/ANIMATION-PROMPTS.md`:
one simple action + the fixed tail ("Locked camera, fixed shot … returns to the starting pose at the end").
Good motions: a wave, a nod, pointing and sweeping an arm, lifting an object, an animal swaying, leaves moving,
lights twinkling. Avoid: walking out of frame, turning around, new objects appearing, anything with writing.

## Steps
1. **Pilot**: the hardest beat alone (big arm sweep, two characters). Show it as a video and as a strip:
   `ffmpeg -i clip.mp4 -vf "fps=1.5,scale=216:-1,tile=8x1" strip.png`.
2. **Batch**: `check_account_status`, one `submit_jobs` call, `wait_for_jobs`; download to `clips/NN.mp4`;
   set `"clip": "clips/NN.mp4"` on each beat.
3. **Review every clip** as a strip: same character throughout, no extra characters, nothing written appears,
   no warping, ends close to the start pose. If a clip fails, do NOT regenerate on your own: show the problem and
   the one extra instruction you would add; regenerate only on "approved". Max two takes per clip.

## Mixed videos
Set `"motion_mode": "mixed"` and `"still": true` on beats that stay still (they get a free camera move).
Animate the hook (first beat), the key moments and the last beat.

## Animating elsewhere
Send `prompts/ANIMATION-PROMPTS.md`. Ask for the same picture as first and last frame where the tool allows it,
then put the clips in `clips/` named by beat.
