---
name: worksheets
description: Build progressive, textbook-style exam-prep worksheets with separate answer keys (Typst → PDF) from course slides and past exams, sized by each topic's weight in previous exams. Use when the user asks for study worksheets, practice problems, exercise sheets, or exam prep for a course, or wants to analyse past exams by topic.
---

# Exam-prep worksheets

Produces, per topic, `<slug>-worksheet.pdf` (questions + answer space) and
`<slug>-answer-key.pdf`, generated from a Python content script via `scripts/wslib.py`.

**The answer key must be readable on its own:** every answer is preceded by its full question
statement (bordered box), and each part's title and intro (e.g. a shared machine-model box) are
repeated in the key. `wslib` does this automatically; blank fill-in tables (`#ft`, `#snap()`)
are stripped from the repeated statement because the answer shows the filled version. If you
write a custom builder (e.g. from a user's own question file), replicate this format:
`#block(stroke: 0.5pt + black, inset: 5pt, ...)[*n.* statement]` then `*Answer.* ...`.
**No em dashes in titles/headings:** write "Part A: Topic", never "Part A — Topic"; sheet
titles, part titles, footers and cheat-sheet headings use ":" or "|" (wslib auto-converts).
**Print-friendly:** everything is black and white. Boxes/headers use a black border only, never a
fill or colour (no `fill:`, no `rgb(...)`, no grey text); emphasis via bold/italic/border weight.
Read `references/conventions.md` before writing questions (rules, sizing table, Typst pitfalls).

## Requirements (any OS)

- Python ≥ 3.8 (`python3` on macOS/Linux, `py` on Windows) with PyMuPDF: `pip install pymupdf`
  (PyMuPDF < 1.24 is fine too; `pdftotext` is a text-only fallback).
- Typst ≥ 0.11, either the CLI (`brew install typst`, `winget install Typst.Typst`,
  `cargo install typst-cli`, or a release binary) **or** just `pip install typst` (wslib falls back to it).
- First time on a machine, run `python3 <skill>/scripts/check_env.py`: it checks all of the above
  and test-compiles a sheet with µ □ ≈ γ. All files are read/written as UTF-8 (needed on Windows).
- Paper: `Sheet(..., paper="a4")` is the default; pass `paper="us-letter"` for US users.

## Workflow

1. **Inventory sources.** Find slides, past exams/solutions, notes, papers in the project
   (`ls`, `find -iname "*.pdf"`). Ask for missing slides only if a topic has none; the user
   may add more; re-list when they say so.
2. **Extract text.** `python3 <skill>/scripts/extract_pdfs.py <tmpdir> slides/*.pdf exams/*.pdf`
   and read all of it. Slides are the source of truth for *what* to teach; exams for *how* it is
   asked (formats, recurring problem templates, point values).
3. **Weight the topics.** Assign every past-exam sub-question's points to one topic; table the
   points per exam, % over all exams, and % over the last ~3 exams. Note recurring templates
   (e.g. "fill the state diagram", "pipeline snapshot at cycle N", "storage-cost calculation").
   If the user only asked for the analysis, stop here and report.
4. **Plan sheets.** One sheet per lecture/topic (merge tiny ones). Size with the table in
   `references/conventions.md`; upweight rising topics. Tell the user the plan (topic → slides
   → weight → #questions) briefly, then proceed.
5. **Set up.** In the project (e.g. `worksheets/`), copy `scripts/wslib.py`; write one
   `build_<topic>.py` per sheet (see `assets/example_build.py`). Structure each sheet as Parts
   A, B, C... that progress from basics to exam-style synthesis; each part gets a one-line intro.
6. **Write questions** following the rules: self-contained (no "slide 4", "the lecture's
   example", "previous question"; restate everything inline), fresh numbers, exam-format
   mirrors tagged with `#ex("YEAR Qn")`, fill-in tables via `#ft` (per-row given data pre-filled in the table, never listed
   below it), filled answer tables via
   `#at`. Verify every number with a quick calculation before writing the answer. For
   timing/trace problems, state the full machine model in a box and choose robust query points.
7. **Figures (sparingly).** Add a figure only where the question cannot be followed reliably from
   text: multi-transistor circuits/OTAs whose topology would take more than ~2 sentences, given
   plots/characteristics, or the exam's own schematic for an exam-mirror question. Single-transistor
   stages, mirrors or anything a sentence describes need no figure. Prefer cropping from the course
   material so notation matches: `python3 <skill>/scripts/crop_figure.py grid deck.pdf PAGE`, read
   the box off the grid image (displayed coordinates, rotated slide pages handled), then
   `crop_figure.py crop deck.pdf PAGE X0 Y0 X1 Y1 figs/name.png`; view every crop and re-crop until
   no label is clipped and no slide text/equations/footers are included. Hand-build (Typst/cetz)
   only if no source drawing exists. Embed with `#fig("figs/name.png", w: 30%)` inside the
   question (or once in a part intro when a whole part shares one circuit) and refer to it as
   "the circuit below". Keep crops black and white and ≤ ~40% width (wide OTAs up to ~65%).
8. **Build:** `python3 build_<topic>.py` (compiles both PDFs).
9. **Check:** `python3 <skill>/scripts/check_sheets.py` → fix every `[ref]` (self-containment)
   and `[underscore]` hit, and skim the question list for questions that silently rely on slide
   content (unexplained numbers, figures, "the three X from class"). Then render a few pages
   with tables/traces/code (`check_sheets.py --render <slug> <page> ...`), view the PNGs, fix
   layout (narrow cells, runs-together sub-parts, split boxes), rebuild, delete `_render_*.png`.
   Also open one answer-key page to confirm statements + answers appear together.
10. **Combined sheets.** Always merge all topic sheets into `ALL-worksheets.pdf` /
   `ALL-answer-keys.pdf` (PDF bookmarks per topic); this is what "combined worksheet" means.
   Only if the user explicitly asks for a mock/practice exam, build a mixed-topic one
   (`build_mock.py`) in the official past-exam format (category tag, points, e.g. 4-option MCQ);
   its distractors must come from computed typical mistakes (forgotten n, ×k² instead of solving,
   swapped W/L, tail vs branch current) and differ from the correct value by ≥ ~15%.
11. **Report** concisely: files, per-sheet table (topic, slides, #Qs, exam weight, highlights),
   any assumptions (e.g. timing model, debatable course conventions), topics left out and why.

## Notes

- Keep build scripts as the editable source; regenerate PDFs after any change.
- When the user later adds slides or asks for revisions, edit the content scripts and rebuild
  all affected sheets; re-run `check_sheets.py`.
- Typst helpers available in markup: `#ex`, `#ft`, `#at`, `#fig`, `#qbox`, `#snap` (ROB/LSQ/SB
  snapshot), `#sub`, `#super`. Add more via `Sheet(..., extra_head="#let ...")`.
