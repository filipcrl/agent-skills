# Worksheet conventions

## Progression

Each sheet teaches its topic from simple to complicated. Before writing, list the concepts in
the order a student should learn them, then give each question a job: introduce one idea, apply
it, or combine it with earlier ones. A typical order is definitions, then mechanisms, then small
worked exercises, then full exam-format problems, then synthesis or design, and finally a short
review.

For each question, ask: what does the reader learn here that they did not know after the
previous question? If the answer is "nothing", cut it or merge it. Two questions that practise
the same thing with different numbers are only worth it when the format is a recurring exam
template. Keep the sheet as short as it can be while still covering everything examinable.

## What to cover

Cover every concept in the slides that could reasonably be asked on an exam, including ones
that have not appeared on past exams yet. Past exams decide the weight and the format, not
whether a topic is included. Give little or no space to material that could not reasonably be
asked: history, anecdotes, motivation slides, tool screenshots, things mentioned only in passing.

## Question rules

1. Self-contained. Every question must be answerable without the slides, the lecture, or
   another question. Course terminology is fine (MOSI, Jetty, warp...). Pointers to outside
   material are not:
   - Bad: "the topology from slide 4", "the lecture's ring example", "as listed in the lecture",
     "same program as the previous question", "the trace from Part C".
   - Good: restate the program, sequence or parameters inline; describe a graph in words; define
     a niche mechanism in one sentence before asking about it.
   - A shared machine-model box at the start of a part is fine if questions say "using the
     machine model at the start of this part".
2. Vary the type: define or explain, compare (tables), trace (fill-in tables), compute (all
   numbers given), design (open-ended with sub-parts (a)(b)(c)).
3. Fresh numbers. Mirror past-exam formats but change the parameters so old solutions can't be
   copied. Tag the matching past question with `#ex("2021 Q4b")`.
4. Verify every calculation (ideally with a quick Python snippet) before writing the answer. For
   cycle-by-cycle traces, state the timing model (structure sizes, dispatch and retire rules,
   latencies) and pick query cycles far from transitions so the answer is robust.
5. Answers teach, not just give the final value. Write full, worked explanations (typically a
   short paragraph or more, not a one-liner), as if tutoring a student who got it wrong:
   - State the underlying concept or rule and why it applies here.
   - Show every step: formula, substitution with units, intermediate results, final value.
   - Explain the reasoning behind each non-obvious step (why this case, why this formula, why
     this row of the trace changes).
   - Point out the common mistake or trap and why it is wrong.
   - End with a one-line takeaway or sanity check (order of magnitude, limiting case).
   For conceptual questions, give the model answer plus a few sentences explaining it and,
   where useful, a contrast with the closely related concept. For tables and traces, add notes
   below the filled table explaining the key rows. Note where course conventions are
   debatable. The key restates each question, so write answers that read naturally right after
   it (no "see above").
6. Given data goes inside the table. When a fill-in table has per-row inputs, pre-fill them:
   `#ft(header, (("1", "1.2", "0"), ...))` (leading cells given, the rest blank). Never list the
   inputs separately next to an empty table. The key drops the blank table, so the filled `#at`
   answer table must include the given columns too.
7. Answer space (`space` argument): 2 to 2.6cm for a short definition, 3 to 4cm for an
   explanation or small calculation, 4.5 to 6cm for multi-part, 7 to 8cm for design or a big
   calculation, about 0.6cm when the question has a fill-in table.

## Sizing

Score each past exam's points by topic, and compute % over all exams and over the last ~3.
These are upper bounds on questions per sheet; use fewer if the concepts are covered:

| Share of exam points | Questions |
|---|---|
| 20% or more | 25 to 35 |
| 10 to 20% | 18 to 25 |
| 5 to 10% | 12 to 18 |
| 2 to 5% | 8 to 12 |
| under 2%, or never examined but in the slides | 5 to 8 |

Give more space to topics rising in recent exams. Topics in old exams but not in the current
slides get folded into a related sheet as a short section, or left out (say so).

## Figures

Add a figure when it clearly makes the question easier to understand, and only then. The test:
would a student working on this question start by sketching it? If so, give them the sketch.
If the picture would only repeat one clear sentence, or decorate a conceptual question, leave
it out. Don't go overboard: most sheets need a handful, not one per question.

| Usually worth a figure | Usually not |
|---|---|
| A circuit with 2+ gates or transistors given as a netlist or in words | A single gate or a formula |
| Where a fault, bridge or test point sits in a circuit | Definitions and "why" questions |
| Scan chains, pipelines, FSMs, block structures to trace | Lists of facts, comparisons |
| Given plots, characteristics, waveforms, timing diagrams | Calculations from stated numbers |
| The exam's own figure for an exam-mirror question | Anything a single clear sentence conveys |

Rules:
- The text stays complete: the question still defines the circuit or data in words ("g1 =
  AND(a, b)") and refers to the figure as "the circuit below". The figure is support, not the
  only source.
- Several questions on the same circuit share one figure, placed in the part intro ("the
  circuit at the start of this part"), since pointing to another question is not allowed.
- Mark what the question is about on the figure when it helps (a fault as × with "s-a-0", a
  bridge as a dashed line), but never mark the answer.
- No colour, no slide titles, equations or footers in crops, no clipped or overlapping labels.
  Store figures in `figs/` next to the build scripts; keep the generating code (`figs.py`) so
  figures can be regenerated.
- Width: about 30 to 45% for small circuits, up to 65% for wide ones.
- Gate-level circuits: `scripts/logic_fig.py` (`circuit(...)`, automatic layout, inversion
  bubbles with `~a`, fault marks, bridges). Other drawings: schemdraw or Typst/cetz.
- Always look at the rendered figure, then at the rendered sheet page, before moving on.

## Style

Black and white only, for printing. Highlight with borders (`stroke: 0.5pt + black`), bold or
italic; never fills, colours or grey text. This also applies to helpers added via `extra_head`
and to companion documents like cheat sheets.

No em or en dashes in titles, headings or footers. Use a colon ("Part A: Foundations") or a pipe.

## Typst pitfalls (markup mode)

| Pattern | Problem | Fix |
|---|---|---|
| `_` | starts emphasis | wrap identifiers in backticks, or use `#sub[i]` |
| `*` | bold | use `×` for multiplication |
| `#` | code mode | only for helpers |
| `$` | math mode | avoid, or write deliberate math |
| `@`, `<x>` | reference or label | escape `\<`, `\>`, or write "less than" |
| `~` | non-breaking space | use `≈` |
| `//`, `/*` | comment | avoid outside raw code |
| `[ ]` | may attach content to a call | escape `\[9:6\]` |
| `--` | en dash | use `-` or "to" |
| line starting with `=`, `- `, `+ `, `1. ` | heading or list | reword |
| `#sub[j](a)` | parsed as call arguments | `#sub[j]\(a\)` |
| `("ST X")` | a string, not an array | `("ST X",)` |

wslib automatically adds line breaks before "(a)", "(b)"... and a space between a math
sub/superscript and a following "(" (`$V_"P1"(1+x)$` would otherwise put "(1+x)" in the
subscript). Code listings go in ```` ``` ```` raw blocks.

## Visual check

A clean compile does not mean a correct layout. Render a few pages with tables, traces or code
using `check_sheets.py --render <slug> <page>...` and look at the PNGs. Delete `_render_*.png`
afterwards.
