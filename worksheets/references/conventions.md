# Worksheet conventions

## Question-writing rules

1. **Self-contained.** Every question must be answerable without the slides, the lecture, or
   another question. Using course terminology is fine (MOSI, Jetty, R-NUCA, warp...). Pointers to
   material outside the question are not:
   - ✗ "the topology from slide 4", "the lecture's ring example", "as listed in the lecture",
     "same program as the previous question", "the trace from Part C"
   - ✓ restate the program/sequence/parameters inline; describe a graph in words; define a
     niche mechanism in one sentence before asking about it ("Jetty is a small filter on the L2
     backside that discards snoops that would miss...").
   - A shared machine-model box at the start of a part is OK if questions say "using the machine
     model at the start of this part" (it is on the same sheet).
2. **Progressive.** Order: definitions → mechanisms → small worked exercises → full exam-format
   problems → synthesis/design → a rapid "behavior exploited + metric optimized" review.
3. **Textbook style.** Mix: define/explain, compare (tables), trace (fill-in tables),
   compute (with all numbers given), design (open-ended with sub-parts (a)(b)(c)).
4. **Fresh numbers.** Mirror past-exam formats but change parameters so old solutions can't be
   copied. Tag the matching past question with `#ex("2021 Q4b–e")`.
5. **Verify every calculation** yourself (ideally with a quick Python snippet) before writing
   the answer. For cycle-by-cycle traces, state the timing model explicitly (structure sizes,
   dispatch/retire rules, latencies) and choose query cycles far from transitions so the answer
   is robust (say "approximate cycle counts ±2 are fine").
6. **Answers are complete teaching text**, not just final values: show the formula, the
   substitution, and one sentence of "why". Note where course conventions are debatable.
   The answer key always restates each question (statement first, then "Answer."), so a
   student can study from the key alone; part intros/machine models are repeated there too.
   Write answers so they read naturally right after the statement (no "see above").
7. **Given data goes inside the table.** When a fill-in table has per-row inputs (bias points,
   parameters, instruction sequences), pre-fill them in their own columns with
   `#ft(header, (("1", "1.2", "0", "1.0"), ...))` (a row given as an array: leading cells are
   given, the rest blank). Never list the inputs in a separate line under/over a table with an
   empty column for them, and never make the student copy given values into the table.
   The key strips the blank `#ft` from the restated question, so the filled `#at` answer table
   must repeat the given columns too.
8. **Answer space** (`space` arg): 2–2.6cm short definition, 3–4cm explanation/small calc,
   4.5–6cm multi-part, 7–8cm design or big calculation; ~0.6cm when the question has a fill-in
   table (the table itself is the space).

## Sizing by exam weight

Score each past exam's points by topic (sub-question granularity), compute % over all exams and
over the most recent ~3 (trend). Rough question counts per worksheet:
- ≥20% of points → 40–50 questions
- 10–20% → 25–35
- 5–10% → 18–25
- 2–5% → 12–18
- <2% → 8–12
Upweight topics that are rising in recent exams; topics absent from current slides get folded
into a related sheet as a short section (or omitted, and say so).

## Figures

Only where text is not enough (see SKILL.md step 7): typically 0 to 3 per sheet, ~5 to 10 per
course. Each figure must be referenced by the question that uses it ("the circuit below") and the
question must still state all numbers in text. A whole part may share one figure placed in the part
intro. Crops come from slides/exams via `scripts/crop_figure.py`; no colour fills, no slide titles,
equations or footers in the crop, no clipped labels. Store them in `figs/` next to the build scripts.

## Titles and headings

No em (—) or en (–) dashes in sheet titles, part titles, section headings, footers or cheat-sheet
headings. Use a colon ("Part A: Foundations", "CS gain cells: GBW = ...") or a pipe in footers.
Prefer plain punctuation in prose too.

## Print styling

Output is printed: black and white only. Highlight with borders (`stroke: 0.5pt + black`),
bold or italic, never with fills, colours or grey text. This applies to any custom helper or
`extra_head` you add, and to companion documents (e.g. cheat sheets) made for the same course.

## Typst pitfalls (markup mode)

| Character / pattern | Problem | Fix |
|---|---|---|
| `_` | emphasis; underscore disappears | wrap identifiers in backticks, or `#sub[i]` |
| `*` | bold | use `×` for multiplication |
| `#` | code mode | only for helpers (`#ex`, `#ft`, `#at`, `#sub`, `#super`) |
| `$` | math mode | avoid, or write deliberate math |
| `@`, `<x>` | reference / label | escape `\<`, `\>`, or write "less than" |
| `~` | non-breaking space | use `≈` |
| `//`, `/*` | comment start! | avoid outside raw code |
| `[ ]` | may start content after a call | escape `\[9:6\]` |
| `--` | en dash | use a plain `-`, "to", or reword (no em dashes) |
| line starting `=`, `- `, `+ `, `1. ` | heading / list | reword |
| `#sub[j](a)` | parsed as call args | `#sub[j]\(a\)` |
| math `X_a(...)`, `X_"ab"(...)`, `X_(..)(...)`, `x^2(...)` | the `(...)` is swallowed into the sub/superscript (`V_"P1"(1+x)` → tiny subscript) | always a space: `V_"P1" (1 + x)`, `S_x (f)`, `ln^2 (1 + x)`; wslib auto-fixes, check_sheets reports `[attach]` |
| `("ST X")` | string, iterated as chars | 1-element array: `("ST X",)` |

Sub-parts "(a) ... \n(b) ..." get forced line breaks automatically by `wslib`.
Code listings: use ```` ``` ```` raw blocks inside the question string (comments with `;` or `#` are safe there).

## Visual check

Typst compiling cleanly ≠ correct layout. Render a few pages (tables, traces, code) with
`scripts/check_sheets.py --render <slug> <page>...` and view the PNGs. The image viewer may
cache by path, so always use fresh filenames (the script does). Delete `_render_*.png` afterwards.
