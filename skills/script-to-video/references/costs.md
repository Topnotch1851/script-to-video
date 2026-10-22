# Costs and spending caps

## Where money is spent (everything else is free and local)
| Item | Endpoint (fal) | Price checked 2026-10-20 |
|---|---|---|
| Picture | `fal-ai/nano-banana-2/edit` (with reference images) or `fal-ai/nano-banana-2` | $0.08 each (1K) |
| Animation | `minimax/h3-max-turbo/image-to-video` | $0.01625 per second (a 5 s clip bills about 5.18 s) |
| AI voice | `fal-ai/elevenlabs/tts/eleven-v3` | $0.10 per 1,000 characters |
| Music | `fal-ai/lyria3/pro` | $0.08 per track |

Free: camera moves on stills, text, captions, sound effects, mixing, loudness, thumbnails, packaging, prompt packs.

## The quality menu (ask every time; `plan_costs.py --menu`)
| Level | Pictures | Animation | 30 s animated, pictures made here |
|---|---|---|---|
| Budget | Nano Banana 2, 1K — $0.08 | MiniMax H3 — $0.01625/s | about $1.19 |
| Sharper pictures | Nano Banana Pro, 2K — $0.15 | MiniMax H3 | about $1.68 |
| Better motion | Nano Banana 2 | Kling 2.6 Pro — $0.07/s (5 or 10 s clips) | about $2.78 |
| Premium | Nano Banana Pro | Kling 2.6 Pro | about $3.27 |
| Still | Nano Banana 2 / Pro | free camera moves | about $0.68 / $1.17 |
Prices checked 2026-10-22 (Nano Banana Pro at 4K costs double). Making the pictures yourself removes the picture cost
at every level: real 21–31 s animated episodes made that way cost $0.47–$0.96. Music adds $0.08 per new track,
nothing with their own track or none.

## Typical totals at Budget level (from `plan_costs.py --compare`)
| 60 s vertical | Pictures made here | Your own pictures |
|---|---|---|
| Still | about $1.12 | about $0.16 |
| Mixed (half animated) | about $1.63 | about $0.67 |
| Animated | about $2.13 | about $1.17 |

5-minute landscape: still about $4.70 · animated about $9.70 · with own pictures $0.66 / $5.71.
Own pictures + own voice + own/no music + still = **$0**.
Real production check: a 60 s animated vertical episode cost $2.36 including two picture retakes and four voice retakes.

## How to quote
1. Check live prices: `get_pricing` with all endpoints in `prices.json`. If any changed, update `prices.json`.
2. Run `plan_costs.py` with the person's answers; show the table and the `--compare` grid.
3. The **spending cap** is the expected total plus the 15% retry reserve. Write it at the top of `PRODUCTION-LOG.md`.
4. At every gate: spent so far, what the next step costs, remaining under the cap.
5. If a step would pass the cap, stop and ask. Never "just one more".

## Ways to make it cheaper (offer when the budget is tight)
- Mixed instead of animated (animate the hook, key moments and ending only).
- Longer beats in long videos (fewer pictures).
- Their own pictures from a free tool (prompt pack).
- Reuse the character sheet and layout guide across a series (made once).
- Music: one track looped with cross-fades for long videos.
