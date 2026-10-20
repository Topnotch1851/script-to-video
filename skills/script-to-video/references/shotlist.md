# shotlist.json — the one file every tool reads

`new_project.py` creates it. You fill it from the script. Paths are relative to the shot list's folder.

```json
{
  "title": "How Bees Make Honey",
  "slug": "how-bees-make-honey",
  "format": "vertical",                 // vertical | landscape | square
  "fps": 30,
  "motion_mode": "animated",            // still | animated | mixed
  "style_lock": "flat 2D children's storybook cartoon, …",   // from styles.md
  "look": "illustrated",                // illustrated | photo
  "character": {                        // null when there is no presenter
    "name": "Pip",
    "description": "a small round honeybee with big friendly eyes, a striped yellow-and-black body and tiny wings.",
    "keep": "face, eyes, body shape, stripes and wing shape",
    "outfit": "a little green scarf",
    "sheet": "https://…/sheet.png"      // once made
  },
  "guide_subject": "person",            // person | object | group | none (layout guide)
  "text_style": "clean",                // kids | clean | {headline_font, caption_font, caption_size}
  "headline_box": "card",               // card | outline
  "caption_box": "pill",                // pill | outline
  "colors": {"accent": "#D46F12"},      // also ink, card, text_on_picture
  "music": [{"file": "music/bed.mp3"}], // [] for none
  "music_db": -14, "duck_db": 8, "sfx_db": -6, "ambience_db": -36, "loudness": -16,
  "auto_sfx": true,
  "beats": [
    {
      "id": 1,
      "seconds": 5,
      "line": "Every jar of honey starts with a single flower.",   // narration (also the .srt text)
      "scene": "a sunny meadow full of purple clover",            // where, what is visible
      "action": "Pip hovers beside a clover flower, smiling",     // what the subject does in the picture
      "motion": "Pip hovers up and down gently, wings buzzing",   // what moves (animated beats)
      "subject_size": "normal",          // normal | small | close
      "picture": "pictures/01.png",
      "clip": "clips/01.mp4",            // optional; animated beats
      "still": false,                    // mixed videos: true keeps this beat still
      "move": "zoom-in",                 // stills: zoom-in | zoom-out | pan-left | pan-right | pan-up | pan-down | none
      "move_amount": 0.08,
      "voice": "voice/01.mp3",
      "voice_at": 0.0,                   // when the line starts inside the beat
      "answer_gap": 0.4,                 // silence kept at the end (1.5 for repeat-after-me)
      "headline": null,                  // or a text object, see below
      "caption": "Every jar starts with one flower",   // or null, or {"text", "from", "until"}
      "sfx": [{"at": 0.0, "sound": "whoosh", "db": -9}],
      "transition": null,                // "whoosh" plays a whoosh at the start
      "clip_fit": "loop",                // loop | hold
      "clip_start": 0,
      "clip_audio": "ambience"           // ambience | full | off
    }
  ]
}
```
(Comments are for reading only; the real file is plain JSON.)

## Several characters, locations and dialogue
```json
"voice": "Rachel",                       // default narrator voice
"motion_style": "loop",                  // loop (default) | free — per beat with "loop": true/false
"cast": [
  {"id": "doug", "name": "Doug", "description": "a round-bellied dad in a green polo shirt…", "keep": "face, body, hair",
   "outfit": null, "voice": "Roger"},
  {"id": "ellie", "name": "Ellie", "description": "a sharp 9-year-old in a white lab coat and round red glasses…", "voice": "Lily"},
  {"id": "byte", "name": "Byte", "description": "a pin-shaped smart speaker with a glowing ring face…", "always": false}
],
"cast_sheet": "https://…/cast-sheet.png",        // once made (one sheet with everyone)
"locations": [
  {"id": "room", "name": "living room", "description": "a green couch facing the camera, a big TV on the left…",
   "plate": "https://…/room.png"},               // true = make a reference picture; false = describe only (cutaways)
  {"id": "hotel", "name": "hotel room", "description": "a small beige hotel room…", "plate": false}
],
"beats": [
  {"id": 1, "seconds": 8, "location": "room", "cast": ["doug", "ellie", "byte"],
   "scene": "Doug sprawled on the couch pointing the remote at Byte", "action": "Ellie peeks over the couch",
   "motion": "Doug jabs the remote three times, Byte shrugs, Ellie raises an eyebrow", "loop": false, "clip_seconds": 8,
   "lines": [
     {"speaker": "doug", "text": "Book the dentist! Order pizza!", "file": "voice/01-1.mp3"},
     {"speaker": "ellie", "text": "It can talk about all of that. It can't do any of it.", "file": "voice/01-2.mp3"}
   ],
   "caption": "Your AI can talk. Can it do?"}
]
```
- `cast` on a beat lists who is in that picture (default: everyone with `"always": true`, or the single presenter).
- `location` with a plate: the plate is sent as a reference picture and the layout guide is skipped for that scene.
- `lines` replace `voice`/`line` for dialogue (or a narrating character). Lines without `"at"` are placed one after another
  with a short gap; `fit_beats.py` stretches the scene to fit. The .srt shows speaker names when several people speak.
- `"loop": false` (free) clips have no last-frame lock: characters can act a whole gag. Use `clip_seconds` up to 15.
- `"caption_box": "tv"` gives bold yellow subtitles with a thick black outline (TV look).
- The old single `"character"` field still works; it is treated as a cast of one.

## Text objects
```json
"headline": {
  "text": "tape",
  "size": "auto",
  "from": 0, "until": null,
  "ghost": 0.3,
  "reveal": [{"at": 1.45, "chars": [3], "fade": 0.35}],
  "marks":  [{"at": 0, "regex": "a", "color": "accent"},
             {"at": 0.55, "regex": "e$", "alpha": 0.45}]
}
"list": {"items": ["cake", "gate", "snake"], "at": [0.2, 0.9, 1.5], "size": 110, "marks": [...]}
```
- `reveal`: characters stay hidden (or at `ghost` opacity in plain ink) until `at`; `fade` makes them fade in.
- `marks`: from `at` until `until`, recolour (`color`) and/or change opacity (`alpha`) of the selected characters.
- Selectors: `"chars": [0, 2]` · `"word": 1` · `"match": "ph"` (first) · `"regex": "e$"` (all) · `"all": true`.
  Indices count every character including spaces.
- Positions never move when letters appear, so a word can grow ("tap" → "tape") without jumping.
- Times are seconds from the beat start. Take them from the measured voice: where the word is actually heard.

## Fields the tools add (do not write them)
Anything starting with `_` (`_start`, `_frames`, `_fmt` …).
