# The production brief: how the skill designs a video

The brief is the "master prompt" for one video, written BY the skill. It is what an expert creative director would hand
to a production team: format, audience, angle, style lock, cast, locations, every scene (picture, action, words,
caption), sound, cost and the approval gates. The person approves the brief before anything is paid for.
Template: `architect.md` (the built-in master prompt). Fill it in, save it as `BRIEF.md` in the project and give it to
the person: they can edit it, reuse it, and hand it back later ("make another one like this").

## Director mode (when the person pastes a full production prompt)
Their prompt is the brief. Copy into the shot list, word for word: the style lock (`style_lock`), cast and location
descriptions, every scene prompt (`beats[].picture_prompt`), every clip prompt (`beats[].clip_prompt`), every line,
every caption, scene lengths and which references each scene uses. `prompt_pack.py` then sends their words unchanged,
adding only the reference-image lines and the no-text rule. Fix only what `prompt-fixer.md` lists (and list each fix).
Their model choices become the suggested quality level; still show the menu with prices.

## Four ways in (all end in a brief)
| The person gives you | You do |
|---|---|
| A finished script | Keep their words. Ask the open intake questions. Design the scenes around the script. |
| Only a topic, an idea or a description ("a video about agent rooms") | **Research first** (below), ask the creative questions, write the script and show it with its sources; once they approve the script, arrange it into the brief like any script. |

## Research (topic-only requests, free)
1. Run 2–4 web searches: the facts and the simple explanation, common myths, what similar short videos say, and one
   surprising detail for the hook. Prefer primary or reputable sources; never invent statistics or quotes.
2. Write 2 hook options and the script (one idea per scene, fitting the length).
3. Show the script with a short "Sources" list and ask: **"Approve the script, or what should change?"** Wait.
4. Only then arrange it into the brief (`architect.md`) and ask the production questions.
| A production prompt (theirs, old, or from someone else) | Run `prompt-fixer.md`, keep their creative choices, turn it into a brief, list what you changed. |
| "Another one like X" (an earlier brief, episode or series bible) | Reuse its locks (style, cast, voices, layout, price band), change the topic, keep series rules (`series.md`). |

## Creative questions (ask only what the request leaves open; suggest an answer for each)
1. **Goal and audience** — who watches, what they should understand or do afterwards.
2. **Angle** — the hook in the first 2 seconds, and the shape: plain explainer · story · sitcom-style gag (a clueless
   character, a smart character, a cutaway joke) · lesson with practice · documentary · list/steps.
3. **Who is on screen** — nobody (scenes only) · one presenter · a cast of 2–4 characters (names, roles, looks,
   personalities) · real people (their consent and photos) · their own footage.
4. **Who speaks** — an unseen narrator · one character narrates · **dialogue** between characters (each gets a voice) ·
   no voice (music and text only).
5. **Where** — one main location the story keeps returning to (plus cutaways) · a new place every scene · abstract
   (diagrams, objects). Main locations get a reference picture ("location plate") so every scene matches.
6. **Style** — from `styles.md`, or described in their words; write a style lock.
7. **Call to action** — what the last scene and the post ask for ("Comment MCP for the guide", "Follow for part 2").
Then the intake questions from `intake.md` that are still open (length, shape, still/animated, who makes pictures,
voice, music, on-screen text, platforms, budget).

## Writing the script (when you write it)
- One idea per scene; one scene = one picture. 5 s scenes for vertical, 5–10 s when a scene has an action gag or
  dialogue, 6–8 s average for landscape.
- Hook first (a question, a surprising line, a funny situation), payoff last, call to action in the final line.
- Speech fits the scene: about 2.3 words per second (1.5 for young children), with air at the end.
- Dialogue: short alternating lines, at most 3 lines per scene; every line is tagged with its speaker.
- Concrete pictures: say who is where doing what, and the one object that matters. Show ideas with objects,
  icons and actions, never with written words inside the picture.
- Keep it original: no characters, brands or logos from existing shows or companies.

## What the brief must contain
1. Title, slug, format, length, scene count, audience, angle, call to action.
2. Style lock (exact text pasted into every picture prompt).
3. Cast: each character's look (what never changes), outfit for this video, personality, voice name.
4. Locations: each main place described once; which scenes use it; cutaways.
5. Scene table: seconds · location · who is in it · picture · action/motion (loop or free) · lines (speaker: text) ·
   on-screen text (none/caption/key word) · sound effect.
6. Sound: narrator or voices per character, music mood, effects.
7. On-screen text mode and caption look (card, outline, or bold yellow TV subtitle).
8. Picture route (made here / made by them / their footage) and motion (still / animated / mixed).
9. Quote with spending cap (`plan_costs.py`, live prices) and the approval gates.
10. Delivery: what they will receive, including SOCIAL.md for their platforms and the call to action.

## Then
Fill `shotlist.json` from the brief (`shotlist.md`), run `prompt_pack.py`, and follow the gates in SKILL.md.
If the person changes the brief, update both files before going on.

## Honest limits to tell people when relevant
- Dialogue is voice-over: characters act and gesture in the clips, but mouths are not lip-synced to the words.
- Picture models can drift on small details (a logo-free badge, the number of fingers); the cast sheet and checks keep
  this low, and a scene can be re-made with the fault named.
- Real-looking people must be labelled as AI when posted.
