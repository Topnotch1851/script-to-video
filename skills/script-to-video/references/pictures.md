# Pictures

Two routes. Both end the same way: numbered files in `pictures/` (`01.png`, `02.png` …) that pass `check_pictures.py`.

## Route A — made here on fal

1. **Layout guide** (free): `python3 KIT/scripts/layout_guide.py --format vertical --subject person --out layout-guide.png`
   (`object` for a product or thing, `group` for several people). Upload it once with the fal upload tools
   (`upload_file`, or prepare upload → PUT → verify) and keep the URL as `GUIDE_URL`.
2. **Reference pictures** (`prompts/fal-references.json`, $0.08 each, made once and reused for every future video):
   - **Cast/character sheet**: one presenter → four poses; a cast of 2–4 → everyone side by side, front and three-quarter
     views, plus a row of expressions (2K, wide). Check: same characters as described, nothing written.
   - **Location plates**: one establishing picture per main location, with no characters in it.
   Save the URLs in the shot list (`cast_sheet`, `locations[].plate`), the production log and the series bible.
3. **Prompts**: `python3 KIT/scripts/prompt_pack.py shotlist.json` writes `prompts/fal-pictures.json`.
   Replace `{CAST_URL}`, `{PLATE_URL_<id>}` and `{GUIDE_URL}` with the uploaded URLs. Each scene gets the right references
   automatically: the cast sheet when characters appear, its location plate (or the layout guide when there is none).
   Validate one input against `get_model_schema` first.
4. **Pilot**: submit the hardest beat alone (crouching, two subjects, a big object, close-up). Show it. Wait for approval.
5. **Batch**: `check_account_status`, then one `submit_jobs` call for the rest; `wait_for_jobs`.
6. **Download** every result into `pictures/NN.png`. Log request ids and costs.
7. **Check**: `python3 KIT/scripts/check_pictures.py --format F pictures --sheet qc/pictures.png`, then look at the
   contact sheet yourself: same character, right size and place, no writing anywhere, no band or empty strip,
   the scene matches the beat, nothing odd (extra limbs, melted objects).
8. **Retry**: one automatic retry for a picture that fails, with the fault named in the prompt
   (e.g. "The presenter must be SMALL: one quarter of the picture height."). Max 3 automatic retries per video.

## Route B — made by the person, anywhere

**Same prompts, no differences.** Route B uses exactly the prompts Route A would send: `prompt_pack.py` writes
`PICTURE-PROMPTS.md` and `fal-pictures.json` from the same function, so the words, the reference pictures and their order
(cast sheet = Image 1, location picture or layout guide = Image 2), the shape and the style lock are identical. Step 0
(cast sheet, location pictures) comes first, and every scene says which references to attach. Tell the person to paste
the prompts unchanged, ideally into the same model family (Nano Banana), and to keep the file.

1. `python3 KIT/scripts/prompt_pack.py shotlist.json` → send `prompts/PICTURE-PROMPTS.md`, `layout-guide.png`
   and the character sheet (if any). The file explains everything: shape, reference images, naming, upload.
2. They make the pictures in any tool and either **attach them in the chat**, or put them in a **Google Drive folder**
   shared as "Anyone with the link can view" and paste the link.
3. Fetching from Drive: use the Google Drive connector (search the folder, download each file). If no connector is
   available, ask them to attach the files instead. Rename to `01.png`, `02.png` … by beat.
4. Run `check_pictures.py`. Tell them exactly which pictures to redo and why (wrong shape, writing in the picture,
   band across it, presenter looks different, too small). Accept the rest.
5. If they chose animation on fal, upload each accepted picture with `upload_file` to get its URL for the clip jobs.

## Own photos and footage
Photos go in `pictures/` (a camera move is added for free). Videos go in `clips/` with, per beat:
`"clip_fit": "hold"` (freeze the last frame if short; `"loop"` only for seamless loops), `"clip_start": 12.5`
(start point in the source), `"clip_audio": "full"` to keep their real sound (dialogue) or `"ambience"` / `"off"`.

## Prompt rules that matter (all built into prompt_pack.py)
- Start with "Draw a NEW picture." so the model does not copy a reference image's layout.
- Image 1 = character sheet ("keep face, hair … exactly; change only the outfit"), Image 2 = layout guide
  ("copy only the SIZE and POSITION of the grey figure").
- Say what the subject does and where; keep objects beside the subject on the same ground line.
- "Fills the WHOLE canvas evenly … no bands, no panels, no empty boxes."
- Paste the style lock. End with the no-text sentence, including signs, books, screens and clothing.
