---
name: worksheets
description: Build progressive, textbook-style exam-prep worksheets with separate answer keys (Typst to PDF) from course slides and past exams. Questions teach concepts step by step from simple to hard, prioritized by what could reasonably be asked on an exam. Use when the user asks for study worksheets, practice problems, exercise sheets, or exam prep for a course, or wants to analyse past exams by topic.
---

# Exam-prep worksheets

For each topic this skill produces `<slug>-worksheet.pdf` (questions with answer space) and
`<slug>-answer-key.pdf`, generated from a Python content script via `scripts/wslib.py`.
Read `references/conventions.md` before writing questions.

## What a good worksheet is

A worksheet is a short course that teaches the topic, not a pile of exam questions. Before
writing, think about what each question teaches the reader and how it builds on the ones
before it. Start with the simplest idea, then add one new thing per question, and end with
full exam-style problems that combine everything. If a question teaches nothing new and does
not practise a format that appears on exams, cut it. Prefer fewer, well-chosen questions over
many similar ones.

Use past exams to decide what matters, but do not overfit to them:

- The slides define what can be asked. A concept that is in the slides but has never appeared
  on an exam can still appear on the next one, so cover it.
- Past exams show how things are asked (formats, recurring problem templates, point values)
  and which topics carry the most weight. Use that to choose formats and to give heavy topics
  more space, not to skip the rest.
- Prioritize material that could reasonably be an exam question: definitions, mechanisms,
  calculations, traces, comparisons, design trade-offs. Give little or no space to things
  that could not reasonably be asked (history, anecdotes, motivational slides, tool screenshots,
  details the slides only mention in passing).

## Format rules

- The answer key must be readable on its own. Every answer is preceded by its full question
  statement in a bordered box, and each part's title and intro (for example a shared machine
  model box) are repeated in the key. wslib does this automatically and strips blank `#ft`
  tables from the repeated statement, since the answer shows the filled version. A custom builder (for example from the user's own question file) must replicate
  this: `#block(stroke: 0.5pt + black, inset: 5pt, ...)[*n.* statement]` then `*Answer.* ...`.
- No em dashes in titles or headings. Write "Part A: Topic", not "Part A — Topic". Sheet
  titles, part titles, footers and cheat-sheet headings use ":" or "|" (wslib auto-converts).
- Print-friendly: black and white only. Boxes and headers use a black border, never a fill or
  colour (no `fill:`, no `rgb(...)`, no grey text).

## Requirements (any OS)

- Python 3.8 or newer (`python3` on macOS/Linux, `py` on Windows) with PyMuPDF:
  `pip install pymupdf`.
- Typst 0.11 or newer, either the CLI (`brew install typst`, `winget install Typst.Typst`,
  `cargo install typst-cli`, or a release binary) or `pip install typst` (wslib falls back to it).
- For drawn figures: `pip install schemdraw matplotlib` (only needed if a sheet draws circuits).
- On a new machine, run `python3 <skill>/scripts/check_env.py` once. It checks the above and
  test-compiles a sheet with µ □ ≈ γ. All files are read and written as UTF-8 (needed on Windows).
- Paper is A4 by default; pass `Sheet(..., paper="us-letter")` for US users.

## Workflow

1. Inventory sources. Find slides, past exams and solutions, notes, papers in the project
   (`ls`, `find -iname "*.pdf"`). Ask for missing slides only if a topic has none. The user may
   add more later; re-list when they say so.
2. Extract text with `python3 <skill>/scripts/extract_pdfs.py <tmpdir> slides/*.pdf exams/*.pdf`
   and read all of it. Slides tell you what to teach; exams tell you how it is asked.
3. Weight the topics. Assign each past-exam sub-question's points to one topic and make a table
   of points per exam, % over all exams, and % over the last ~3 exams. Note recurring templates
   (for example "fill the state diagram", "pipeline snapshot at cycle N", "storage-cost
   calculation"). Also list slide concepts that are examinable but have not appeared yet. If the
   user only asked for the analysis, stop here and report.
4. Plan the sheets. One sheet per lecture or topic (merge tiny ones). Size them with the table
   in `references/conventions.md`. For each sheet, sketch the learning path: the list of concepts
   in the order they should be learned, and which question teaches each one. Tell the user the
   plan briefly (topic, slides, weight, number of questions), then proceed.
5. Set up. In the project (for example `worksheets/`), copy `scripts/wslib.py` and write one
   `build_<topic>.py` per sheet (see `assets/example_build.py`). Structure each sheet as Parts
   A, B, C... that go from basics to exam-style synthesis, each with a one-line intro.
6. Write the questions following the conventions: self-contained (no "slide 4", "the lecture's
   example", "previous question"; restate everything inline), fresh numbers, exam-format mirrors
   tagged with `#ex("YEAR Qn")`, fill-in tables via `#ft` with per-row given data pre-filled in
   the table, filled answer tables via `#at`. Check every number with a quick calculation before
   writing the answer. For timing or trace problems, state the full machine model in a box and
   choose robust query points. Answers must be long, worked explanations, not bare results:
   explain the concept, show every step, justify non-obvious moves, and flag the common mistake
   (see rule 5 in `references/conventions.md`).
7. Figures where they really help. For each question ask: would a reader understand it faster
   or more reliably with a picture than with the text alone? If yes, add one; if it would only
   decorate or repeat what one sentence already says, don't. Typical yes: a circuit, netlist or
   structure the reader would otherwise sketch themselves to work on it (any multi-gate or
   multi-transistor circuit, a fault or bridge location, a scan chain, a pipeline or FSM), a
   given plot or characteristic, a timing diagram, the exam's own figure for an exam-mirror
   question. Typical no: definitions, conceptual "why" questions, simple formulas, a single
   gate. Keep the text complete anyway (the figure supports it, it does not replace it), and
   reuse one figure for a whole part when several questions share it. See "Figures" in
   `references/conventions.md`.
   Sources, in order: crop from the course material so notation matches; draw gate-level
   circuits from their netlist with `scripts/logic_fig.py`; draw anything else with
   schemdraw (transistor circuits, blocks) or Typst/cetz (plots, timing, graphs). To crop, run `python3 <skill>/scripts/crop_figure.py grid
   deck.pdf PAGE`, read the box off the grid image, then `crop_figure.py crop deck.pdf PAGE X0 Y0
   X1 Y1 figs/name.png`. Look at every crop and redo it until no label is clipped and no slide
   text, equations or footers are included. For a gate-level circuit, call
   `circuit("figs/name.svg", inputs=[...], gates=[("g1", "AND", "a ~b"), ...], marks={...},
   bridges=[...])` (layout is automatic; see the docstring) from a `figs.py` next to the build
   scripts. Fix any printed warning with `y=` hints. Look at every figure before embedding it
   and redo it if wires cross gates, labels overlap or it is cluttered. Embed with `#fig("figs/name.png", w: 30%)` inside the question (or once in a part
   intro if the whole part uses it) and refer to it as "the circuit below". Keep crops black and
   white and at most ~40% width (wide circuits up to ~65%).
8. Build with `python3 build_<topic>.py` (compiles both PDFs).
9. Check with `python3 <skill>/scripts/check_sheets.py` and fix every `[ref]` and `[underscore]`
   hit. Skim the question list for questions that silently rely on slide content (unexplained
   numbers or figures, "the three X from class"), and for the progression: does each question
   add something, and are there near-duplicates to cut? Render a few pages with tables, traces or
   code (`check_sheets.py --render <slug> <page> ...`), look at the PNGs, fix layout problems,
   rebuild, and delete `_render_*.png`. Open one answer-key page to confirm statements and
   answers appear together.
10. Combined sheets. Always merge all topic sheets into `ALL-worksheets.pdf` and
    `ALL-answer-keys.pdf` (with PDF bookmarks per topic). Only if the user explicitly asks for a
    mock or practice exam, build a mixed-topic one (`build_mock.py`) in the official past-exam
    format (category tag, points, for example 4-option MCQ). Its distractors should come from
    computed typical mistakes and differ from the correct value by at least ~15%.
11. Report briefly: files, a per-sheet table (topic, slides, number of questions, exam weight,
    highlights), assumptions (for example the timing model or debatable course conventions), and
    topics left out and why.

## Notes

- The build scripts are the editable source; regenerate the PDFs after any change.
- When the user adds slides or asks for revisions, edit the content scripts, rebuild the
  affected sheets, and re-run `check_sheets.py`.
- Typst helpers available in markup: `#ex`, `#ft`, `#at`, `#fig` (documented at the top of
  wslib.py). Add more via `Sheet(..., extra_head="#let ...")`.
