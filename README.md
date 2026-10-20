# Script to Video

**Paste a script. Answer a few questions. See the price. Say "approved". Get a finished video.**

Script to Video is a skill (and Claude Code plugin) that turns any script into a finished, narrated video —
vertical Shorts/Reels/TikTok or landscape YouTube, any length, any style — for about **$1–2.50 per minute**,
or **$0** if you bring your own pictures and voice. It was built and tested in real production of a children's
education series, then generalised so it works for any topic: lessons, stories, explainers, product videos,
documentaries, real-looking people or your own footage.

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## What you get

- **Start with anything** — a finished script, just a topic ("a 30-second video about agent rooms"), a description,
  an old production prompt, or "another one like the last episode". The skill asks only what is missing.
- **It designs the video for you** — from a topic it writes the script and a full **production brief**: the angle and
  hook, a cast of characters (one presenter or 2–4 characters), the locations, every scene (picture, action, lines,
  caption), voices, music, cost and the approval steps. You can keep the brief and reuse it for the next video.
- **One voice or a conversation** — an unseen narrator, a character who narrates, or **dialogue** between characters,
  each with their own voice (voice-over; mouths are not lip-synced).
- **A guided intake** — length, vertical or landscape (suggested from length), video style, still or animated,
  who makes the pictures, voice, music and on-screen text (or none). It suggests an answer for each.
- **The full price before anything is paid for**, with a spending cap. Nothing that costs money runs until you type **approved**.
- **Two picture routes**
  - *Made for you* on fal.ai (about $0.08 a picture), framed with a layout guide so the subject always sits right.
  - *Made by you* in any tool you like, free ones included: you get **one ready-to-paste prompt per picture**,
    a layout guide and naming rules; upload them to the chat or a shared Google Drive folder and the rest is automatic.
- **Still or animated**
  - *Still*: smooth camera moves on every picture, made locally for free.
  - *Animated*: every picture becomes a short looping clip (character stays on-model).
  - *Mixed*: animate only the moments that matter.
- **Proper sound**: AI narration (or your recording), new music (or yours, or none) that automatically drops under the
  voice, free synthesised sound effects, room ambience, and broadcast-correct loudness.
- **On-screen text only if you want it**: none, subtitles, key words, or teaching words with timed colour changes.
- **A ready-to-post package**: the video, a captions file (.srt), thumbnails, YouTube chapters, and **SOCIAL.md** with
  captions, hashtags, titles, descriptions and tags for Instagram, TikTok, YouTube (Shorts and long-form) and Facebook.
- **Checks at every step**: pictures are checked for text, bands and wrong shapes; the final video is checked for length,
  timing, loudness and spelling (frame grabs at every text change).

![On-screen text options: none, subtitles, key words, teaching](docs/images/text-modes.png)

## What it costs

Live prices are checked before every quote. Typical totals:

| 60-second vertical | Pictures made for you | Your own pictures |
|---|---|---|
| **Still** (free camera moves) | about $1.12 | about $0.16 |
| **Mixed** (half animated) | about $1.63 | about $0.67 |
| **Animated** | about $2.13 | about $1.17 |

| 5-minute landscape | Pictures made for you | Your own pictures |
|---|---|---|
| **Still** | about $4.70 | about $0.66 |
| **Animated** | about $9.70 | about $5.71 |

Your own pictures + your own voice recording + your own or no music + still = **$0 paid**.
Everything else — camera moves, text, effects, mixing, loudness, thumbnails, captions, packaging — is free and local.
A real 60-second animated episode made with this workflow cost **$2.36** in total, retakes included.

## How it works

```mermaid
flowchart LR
  A[Script, topic,<br/>old prompt or<br/>'another like X'] --> B[Questions<br/>cast · places · who speaks<br/>length · shape · style<br/>still/animated · pictures<br/>music · text]
  B --> C[Production brief<br/>+ price + spending cap]
  C -->|approved| D[Look pilot<br/>1 picture / clip<br/>or your prompt pack]
  D -->|approved| E[Voice + all pictures<br/>+ free preview]
  E -->|approved| F[Animation + music<br/>+ final checks]
  F -->|ship it| G[Video · .srt · thumbnails<br/>SOCIAL.md · log · zip]
```

---

## Install

You need three things: **the skill**, **the fal connector** (for anything generated; it is optional for the $0 route)
and a place where Claude can run code (Claude Code, or the Claude app with code execution on).

### Option A — Claude Code (recommended)

1. Install the plugin:
   ```bash
   claude plugin marketplace add Topnotch1851/script-to-video
   claude plugin install script-to-video@script-to-video
   ```
2. Connect fal (sign in with your browser; no API key is pasted anywhere):
   ```bash
   claude mcp add --transport http --scope user fal https://mcp.fal.ai/mcp-relay
   ```
   Then start `claude`, type `/mcp`, choose **fal** → **Authenticate**, and finish the sign-in.
3. Make sure Python 3.9+ and ffmpeg are installed:
   ```bash
   python3 -m pip install Pillow numpy        # add imageio-ffmpeg if you cannot install ffmpeg
   ffmpeg -version
   ```
4. Add credit to your fal.ai account (a few dollars is plenty to start).

### Option B — Claude app (claude.ai on the web, or Claude desktop)

1. Download **[`script-to-video-skill.zip`](https://github.com/Topnotch1851/script-to-video/raw/main/download/script-to-video-skill.zip)** (the skill folder, ready to upload).
2. In Claude, make sure **code execution** is turned on in your settings (skills need it).
3. Go to **Customize → Skills**, upload the zip, and switch the skill on.
4. Add the fal connector: in your connector settings choose **Add custom connector**, use the URL
   `https://mcp.fal.ai/mcp-relay`, and sign in.
5. Optional: connect **Google Drive** if you will make your own pictures and share them from a Drive folder.

### Option C — copy the skill folder by hand (Claude Code without plugins)

```bash
git clone https://github.com/Topnotch1851/script-to-video.git
mkdir -p ~/.claude/skills && cp -r script-to-video/skills/script-to-video ~/.claude/skills/
```
Then connect fal as in Option A, step 2.

### Option D — other AI assistants

fal's connector also works with ChatGPT, Codex, Cursor and any MCP client. Give your assistant the
`skills/script-to-video` folder (or clone the repo into its workspace), make sure it can run Python, then paste the
master prompt. The tools are plain Python and ffmpeg, so anything that can run them can produce the video.

---

## Make your first video (step by step)

1. **Open a new chat** (Claude app) or start `claude` in an empty folder (Claude Code).
2. **Say what you want.** One line is enough:
   ```text
   /script-to-video:make-video a 35-second sitcom-style video for small business owners about password managers
   ```
   In the Claude app: *"Use script-to-video to make me a video about …"*. Have a script already? Paste it after the
   command, or use the fuller [`MASTER-PROMPT.md`](MASTER-PROMPT.md) to give your script and all your answers at once.
3. **Answer the questions.** Only what your request left open: who is on screen, who speaks, where it happens, style,
   length, still or animated, who makes the pictures, music, on-screen text. Each comes with a suggestion; "yes to all" is fine.
4. **Read the production brief and the price.** You see the cast, the places and every scene (picture, action, lines,
   caption), the cost and the spending cap. Type **approved** to start, or ask for changes. Keep `BRIEF.md`: hand it
   back any time to make another video like it.
5. **Approve the look.** You see one pilot picture (and one clip if animated).
   *Making your own pictures?* You get `PICTURE-PROMPTS.md` instead: make the pictures in any tool,
   name them `01.png`, `02.png` …, and attach them or share a Google Drive folder link.
6. **Approve the preview.** All pictures with the narration, text and effects, as a free preview (no music yet).
7. **Approve the final.** Animation (if chosen) and music are added, the video is checked, and you see it.
   Say **ship it** or ask for changes.
8. **Download your package**: the video, captions file, thumbnails, SOCIAL.md with posts for each platform,
   the production log with every cost, and one zip with everything.

Worked examples:
- [`examples/topic-only-sitcom`](examples/topic-only-sitcom) — a one-line topic turned into a three-character sitcom
  video with dialogue: the brief the skill wrote, the shot list and every generated prompt. Quote: $1.27 for 35 s animated.
- [`examples/why-the-sky-is-blue`](examples/why-the-sky-is-blue) — a finished script, still pictures you make yourself,
  subtitles. Quote: $0.12 for 30 s.

## Already have a production prompt?

Paste it into the script box. The skill **corrects it first** — wrong models or prices, fixed budgets, text drawn by
the AI, "leave the top empty" framing, missing music or captions, repeated lines in a series — and shows you a short
list of what it changed before anything runs.

## Casts, locations and dialogue

For videos with several characters the skill makes one **cast sheet** (everyone side by side, with expressions) and one
**reference picture per main location**, then sends the right ones with every scene so faces and rooms stay the same.
Cutaways are described in the scene. Each character gets a voice; lines in a scene play one after another and the scene
length is fitted to them. Acting scenes use free animation (a whole gag in one clip, up to 15 s); presenter scenes loop.

## Making a series

After the first video you get a **series bible**: the character sheet, voice, style, the outfits and settings
already used, and every line already spoken. Paste it into the master prompt's "Series" field each time. Each new
episode opens with a callback to the last one, never repeats a line, changes the outfit, settings and music,
and keeps the face, voice and style the same.

---

## Use the tools directly (for developers)

Everything local lives in `skills/script-to-video/scripts/` and reads one file, `shotlist.json`
([format](skills/script-to-video/references/shotlist.md)).

| Script | What it does |
|---|---|
| `new_project.py` | Create a project folder, starter shot list and layout guide |
| `plan_costs.py` | Price quote; `--compare` prints every option side by side |
| `prompt_pack.py` | Picture, animation and voice prompts, reference-picture prompts (cast sheet, locations) and fal job lists |
| `layout_guide.py` | The framing reference image for any format |
| `check_pictures.py` | Checks pictures (shape, size, bands, empty strips) + contact sheet |
| `fit_beats.py` | Times every beat to its narration (long videos) |
| `split_voice.py` | Splits one long voice recording into one file per beat |
| `build_beat.py` | Renders one beat (still camera move or clip + timed text) |
| `assemble.py` | Builds the whole video: pictures, voice, effects, ambience, ducked music, loudness, .srt, chapters |
| `qc.py` | Final checks: length, speech timing, loudness, frame contact sheet |
| `thumbnail.py` | YouTube (1280x720) and vertical cover thumbnails |
| `package.py` | Folder + zip + MD5 of everything |

```bash
K=skills/script-to-video/scripts
python3 $K/new_project.py my-video --title "My Video" --format vertical --seconds 60 --motion still
# …fill my-video/shotlist.json, add pictures/ and voice/ …
python3 $K/assemble.py my-video/shotlist.json my-video/final.mp4
python3 $K/qc.py my-video/shotlist.json my-video/final.mp4
```

## Troubleshooting

| Problem | Fix |
|---|---|
| "fal is not connected" | Add the connector (Install, step 2) and sign in; or choose the $0 route |
| A job seems stuck | It is checked by its request id; it is never resubmitted (that would charge twice) |
| `ffmpeg not found` | Install ffmpeg, or `pip install imageio-ffmpeg` |
| Writing appears inside a picture | That picture is re-made with the fault named (the AI is never asked to draw text) |
| A band or empty strip across a picture | Re-made; framing uses the layout guide, never "leave space empty" |
| The voice says a letter's name instead of its sound | Respell it ("kuh", "sss"); see `references/sound.md` |
| The preview has no music | Correct — previews are silent of music on purpose; music is added in the final step |
| Out of fal credit mid-way | Credit is checked before every batch; top up and continue from the same step |

## Responsible use

- Realistic AI people or events must be labelled when posted (YouTube "altered or synthetic content",
  TikTok "AI-generated", Meta "AI info"). SOCIAL.md reminds you.
- Only show real people with their consent; never imitate public figures, brands or logos.
- Videos aimed at children must be marked **made for kids** on YouTube.
- Use music you own or have licensed, or let the skill make new music.

## Repository layout

```
.claude-plugin/          plugin + marketplace manifests (Claude Code)
commands/make-video.md   /script-to-video:make-video
skills/script-to-video/  the skill: SKILL.md, references/, scripts/, templates/, fonts/, prices.json
examples/                worked example
docs/images/             pictures used in this README
MASTER-PROMPT.md         the prompt you paste into a chat
```

## Contributing

Issues and pull requests are welcome: new styles, better prompts, more platforms, other model providers.
Please keep the rules in `references/lessons.md`; each one exists because something went wrong without it.
Run both example builds and `claude plugin validate .` before opening a pull request.

## Credits and licence

MIT © 2026 Topnotch1851 — see [LICENSE](LICENSE).
Fonts: Andika (SIL International), Patrick Hand (Patrick Wagesreiter), Poppins (Indian Type Foundry),
all under the SIL Open Font License 1.1.
Generation runs on [fal.ai](https://fal.ai) models: Nano Banana 2 (pictures), MiniMax H3 (animation),
ElevenLabs v3 (voice), Lyria 3 (music). Prices belong to fal and can change; the skill checks them live.
