# Formats, framing and text modes

All numbers live in `scripts/common.py` (`FORMATS`); every script reads them from there.

| Format | Size | Picture model aspect | Used for |
|---|---|---|---|
| vertical | 1080x1920 | 9:16 | Shorts, Reels, TikTok, Stories (up to ~3 min) |
| landscape | 1920x1080 | 16:9 | YouTube long-form, Facebook video, websites |
| square | 1080x1080 | 1:1 | feed posts |

## Vertical layout (proven in production)
- Headline band 425–765 px: big words on a soft card (only if the video uses on-screen text).
- Subject 830–1350 px: the presenter or main object, centred, head to feet.
- Caption band 1368–1478 px, caption at most 620 px wide (clears the right-hand like/share buttons).
- The subject is big and centred with roughly equal space above and below the whole group.
- Keep anything important out of the top 270 px and below 1500 px (app buttons and captions cover them).

## Landscape layout
- Optional title band 60–280 px; subject 300–900 px centred; caption band 918–1014 px, max 1500 px wide.
- Keep a 5% margin on every side (title-safe).

## Framing pictures
Pictures are scaled to COVER the frame and centre-cropped. To make the subject land in the subject band, send the
**layout guide** (`scripts/layout_guide.py --format F --subject person|object|group`) as an extra reference
image and ask the model to copy only the size and position of the grey figure.

## Beat length
- One beat = one picture = usually one narration sentence.
- Vertical: 5 s beats (12 per minute) are proven. Landscape: 6–8 s beats; run `fit_beats.py` after the voice is made
  to fit each beat to its line. Lines longer than ~12 s should be split across two pictures.
- Generated clips are 2–15 s long; they loop seamlessly if the beat is longer than the clip.

## On-screen text modes (choose per video; none is a valid choice)
| Mode | Shot list | Notes |
|---|---|---|
| none | no `headline`, no `caption` | cleanest; most landscape storytelling |
| subtitles | `caption` = the spoken line (or a shortened version) | also exported as `.srt` from each beat's `line` |
| key words | `headline.text` per beat | auto-sized, up to 3 lines |
| teaching | `headline` with `reveal` and `marks` (timed colour changes, letters appearing) | cues timed from the voice |

Text look: `"headline_box": "card"` (soft white card, dark text) or `"outline"` (white text with dark outline,
straight on the picture); same for `"caption_box": "pill" | "outline"`.
Fonts: `"text_style": "kids"` (Andika, early-reader letter shapes + Patrick Hand) or `"clean"` (Poppins), or your own
`{"headline_font": "/path.ttf", "caption_font": "/path.ttf", "caption_size": 52}`.
Time text changes from the measured audio (when a word is actually heard), not from text-to-speech timestamps,
which drift.
