# Style menu

Each style has a **style lock**: paste it word for word into `style_lock` in `shotlist.json`; `prompt_pack.py` puts it
in every picture prompt so all pictures match. Text is never drawn by the model, in any style.

| # | Style | Good for | Style lock (paste exactly) |
|---|---|---|---|
| 1 | Storybook cartoon | kids, stories, light explainers | flat 2D children's storybook cartoon, bright saturated cheerful colours, clean black hand-drawn outlines with a slight wobble, flat colour fills, no 3D, no photorealism |
| 2 | Stick figure / line art | simple teaching, humour | simple black-ink stick figures on warm off-white paper, thin hand-drawn lines with a slight wobble, one accent colour on the object that matters, no shading, flat 2D, generous space |
| 3 | Flat vector explainer | business, tech, how-to | clean flat vector illustration, geometric shapes, soft gradients allowed only in the background, limited modern palette, crisp edges, friendly rounded characters |
| 4 | 3D cartoon | kids, brands, product stories | soft 3D cartoon render, rounded friendly shapes, smooth clay-like materials, warm studio lighting, gentle shadows, bright saturated colours, family-film look |
| 5 | Anime-style | stories, gaming, youth | cel-shaded Japanese-animation-inspired illustration, clean line art, expressive eyes, vivid sky and lighting, painted backgrounds |
| 6 | Watercolour | calm, poetry, nature, wellbeing | soft watercolour illustration on textured paper, gentle bleeding edges, light pastel washes, delicate ink outlines |
| 7 | Paper cut-out | crafts, kids, history | layered paper cut-out collage, visible paper texture and soft drop shadows between layers, bright card colours |
| 8 | Whiteboard sketch | lessons, sales explainers | black marker sketch on a clean white board, simple shading lines, one or two highlight colours, hand-drawn look |
| 9 | Comic book | drama, history, fun facts | bold comic-book illustration, thick ink outlines, halftone shading, punchy saturated colours, dynamic angles |
| 10 | Pixel art | gaming, retro, tech | detailed 16-bit pixel art, limited palette, crisp pixels, no blur, retro game look |
| 11 | Cinematic real-life | documentaries, true stories, travel, real-people scenes | photorealistic cinematic photograph, natural light, shallow depth of field, realistic skin and materials, 35mm film look, true-to-life colours |
| 12 | Stock-photo clean | business, health, finance | bright clean professional photograph, soft daylight, neutral background, realistic people and objects, natural colours |
| 13 | Sitcom animation | comedy explainers, family gags, adults | flat cel-shaded TV sitcom animation, rounded soft characters with oversized heads, big oval eyes with small dot pupils, thick even black outlines, flat colours with almost no shading, clean flat pastel backgrounds, simple furniture, even sitcom lighting, wide level camera, original characters only |
| 14 | Your own footage/photos | vlogs, products, real events | (no lock; their media is used as-is, cropped to the shape) |

For styles 11–12 set `"look": "photo"` in the shot list so prompts say "photograph" instead of "picture".

## Real-looking people (styles 11–12)
- Make fictional people only, unless a real person gives consent and provides their photo as the reference.
- Never imitate a real public figure, brand or logo.
- Platforms require labelling realistic AI-made people and events (YouTube "altered or synthetic content",
  TikTok "AI-generated", Meta "AI info"). Put this in SOCIAL.md as a posting step.

## Presenter character in any style
Describe the character once in `character.description` (shape, face, hair, body, colours) and list what must
never change in `character.keep`. Change only `character.outfit` between videos for variety.
The character sheet (four poses, plain background) becomes Image 1 of every picture.

## Variety (keeps viewers watching)
Every beat gets a **different setting** (place, time of day, colours) unless the script needs continuity.
Across a series, change the outfit colour, settings and music each video; keep face, voice and style fixed.
