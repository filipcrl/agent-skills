"""Shared builder for exam-prep worksheets + answer keys (Typst -> PDF).

Usage in a content script (keep it next to this file or add this dir to sys.path):

    from wslib import Sheet
    s = Sheet("Cache Coherence", "coherence", course="CS471")
    s.part("Part A: Foundations", "One-line intro shown under the part title.")
    s.q(r'''Question text (raw Typst markup). Sub-parts on new lines:
    (a) first part
    (b) second part
    #ex("2019 Q2b")''', "3cm", r'''Answer text (raw Typst markup).''')
    s.build()   # writes <slug>-worksheet.typ/.pdf and <slug>-answer-key.typ/.pdf in CWD

The answer key repeats every question statement (bordered box; blank #ft/#snap fill-ins stripped)
followed by "Answer." and the answer, plus each part's title and intro, so it reads on its own.

Helpers available inside question/answer markup (defined in the Typst header):
    #ex("2021 Q3")                          grey "exam link" tag
    #ft(("State","PrRd","PrWr"), ("I","S","M"), h: 2em, w: 100%)
                                            fill-in table: header row + row labels + blank cells
    #ft(("Case","VG","VS","Mode"), (("1","1.2","0"), ("2","0.9","0.6")))
                                            row = array -> leading cells are GIVEN data (pre-filled),
                                            remaining columns are blank. Put given data in the table,
                                            never in a list below it.
    #at(("Col1","Col2"), [a], [b], [c], [d]) filled table for answer keys (cells row-major)
    #fig("figs/ota5.png", w: 40%)           centered figure (path relative to the .typ file); use only
                                            when a circuit/plot is hard to describe in words
    #qbox(title, n, entries: ())            single-column box column (e.g. ROB/LSQ snapshots)
    #snap(rob: (), lsq: (), sb: ())         ROB(4)/LSQ(4)/SB(2) snapshot; blank in sheet, filled in key
                                            NOTE: a 1-element Typst array needs a trailing comma: ("ST X",)

Pass extra_head="..." to Sheet() to define additional Typst helpers.

Typst pitfalls (see references/conventions.md): escape or avoid bare _ * # $ @ < > ~ [ ]
in markup; never write // or /* outside raw code; avoid "--" (en dash) and lines starting
with "=", "- ", "+ ". Put identifiers with underscores in `backticks`.
"""
import pathlib, re, shutil, subprocess, sys

BASE_HEAD = r'''#set page(paper: "PAPER", margin: (x: 1.5cm, y: 1.3cm),
  footer: context [#set text(8pt); COURSE | TITLE #h(1fr) #counter(page).display() / #counter(page).final().first()])
#set text(size: 10pt)
#set par(justify: true)
#let ex(s) = text(8pt, style: "italic")[ (exam link: #s)]
#let ft(header, labels, h: 1.7em, w: 100%) = block(width: w, table(
  columns: (auto,) + (1fr,) * (header.len() - 1), inset: 4pt, align: center + horizon,
  ..header.map(x => [*#x*]),
  ..labels.map(l => {
    let g = if type(l) == array { l } else { (l,) }
    ([*#g.at(0)*],) + g.slice(1).map(x => [#x]) + range(header.len() - g.len()).map(_ => box(height: h))
  }).flatten()))
#let fig(path, w: 35%) = align(center, block(above: 4pt, below: 4pt, image(path, width: w)))
#let at(header, ..rows) = table(
  columns: header.len(), inset: 4pt, align: center + horizon,
  ..header.map(x => [*#x*]), ..rows.pos().flatten())
#let qbox(title, n, entries: ()) = table(columns: (2.9cm,), inset: 4pt, align: center + horizon,
  table.header([*#title*]),
  ..range(n).map(i => box(height: 1.1em, if i < entries.len() [#entries.at(i)] else [])))
#let snap(rob: (), lsq: (), sb: ()) = align(center, grid(columns: 3, column-gutter: 1.2cm,
  qbox("ROB", 4, entries: rob), qbox("LD/ST queue", 4, entries: lsq), qbox("Store buffer", 2, entries: sb)))
'''


def compile_typst(f):
    """Compile with the typst CLI if present, else with the `typst` pip package (pip install typst)."""
    if shutil.which("typst"):
        subprocess.run(["typst", "compile", f], check=True)
        return
    try:
        import typst
    except ImportError:
        sys.exit("Typst not found. Install either the CLI (https://github.com/typst/typst/releases, "
                 "`brew install typst`, `winget install Typst.Typst`, `cargo install typst-cli`) "
                 "or the Python package: pip install typst")
    typst.compile(f, output=f[:-4] + ".pdf")


class Sheet:
    def __init__(self, title, slug, course="", extra_head="", paper="a4"):
        title = self._nodash(title)
        self.title, self.slug, self.items = title, slug, []
        self.head = BASE_HEAD.replace("COURSE | ", f"{course} | " if course else "").replace("TITLE", title).replace("PAPER", paper) + extra_head

    @staticmethod
    def _nodash(s):
        """No em/en dashes in titles or section headings: 'Part A — X' -> 'Part A: X'."""
        return re.sub(r"\s*[—–]\s*", ": ", s)

    def part(self, title, intro=""):
        self.items.append(("part", self._nodash(title), intro))

    def q(self, text, space, ans):
        self.items.append(("q", text, space, ans))

    @staticmethod
    def _strip_blanks(s):
        """Remove blank fill-in helpers (#ft(...), #snap()) from a question for the answer key,
        including an enclosing #align(center)[...] wrapper. The filled version is in the answer."""
        out, i = [], 0
        while i < len(s):
            j = min([x for x in (s.find('#align(center)[#ft(', i), s.find('#ft(', i), s.find('#snap()', i)) if x >= 0],
                    default=-1)
            if j < 0:
                out.append(s[i:]); break
            out.append(s[i:j])
            if s.startswith('#snap()', j):
                i = j + len('#snap()'); continue
            wrapped = s.startswith('#align(center)[', j)
            k = s.find('#ft(', j) + len('#ft(')
            depth = 1
            while k < len(s) and depth:
                depth += {'(': 1, ')': -1}.get(s[k], 0); k += 1
            if wrapped and k < len(s) and s[k] == ']':
                k += 1
            i = k
        return ''.join(out).strip()

    ATTACH = re.compile(r'([_^](?:"[^"$]*"|\([^()$]*\)|[A-Za-z0-9]))\(')

    @classmethod
    def _detach(cls, s):
        """Typst math pitfall: a '(' right after a sub/superscript is swallowed into it
        ($V_"P1"(1+x)$ renders the whole (1+x) as subscript). Insert a space inside $...$."""
        parts = s.split('$')
        for j in range(1, len(parts), 2):
            parts[j] = cls.ATTACH.sub(r'\1 (', parts[j])
        return '$'.join(parts)

    @staticmethod
    def _breaks(s):
        # "(a) ...\n(b) ..." -> forced line breaks so sub-parts don't run together
        return s.replace('\n(', ' \\\n(')

    def build(self, compile=True):
        H = self.head
        w = H + f'''#align(center)[#text(16pt, weight: "bold")[{self.title}] \\ #text(12pt)[Worksheet]]
#v(2pt)
Name: #box(width: 3in, repeat[\\_]) #h(1fr) Date: #box(width: 1.4in, repeat[\\_])
#v(6pt)
'''
        k = H + f'#align(center)[#text(16pt, weight: "bold")[{self.title}] \\ #text(12pt)[Answer Key]]\n#v(8pt)\n'
        n = 0
        for item in self.items:
            if item[0] == "part":
                _, title, intro = item
                intro = self._detach(intro)
                w += (f'#v(4pt)\n#block(breakable: false, stroke: 0.8pt + black, inset: 6pt, width: 100%)'
                      f'[#text(12pt, weight: "bold")[{title}] \\ #text(9pt)[{intro}]]\n#v(4pt)\n')
                k += f'#v(4pt)\n#text(12pt, weight: "bold")[{title}]\n\n'
                if intro:
                    k += f'#text(9pt)[{intro}]\n\n'
            else:
                n += 1
                _, text, space, ans = item
                text, ans = self._breaks(self._detach(text)), self._breaks(self._detach(ans))
                w += (f'#block(breakable: false, width: 100%)[*{n}.* {text}\n#v({space})]\n'
                      f'#line(length: 100%, stroke: 0.3pt + black)\n#v(1pt)\n')
                stmt = self._strip_blanks(text)
                k += (f'#block(breakable: true, stroke: 0.5pt + black, inset: 5pt, width: 100%)'
                      f'[*{n}.* {stmt}]\n#v(-2pt)\n*Answer.* {ans}\n#v(6pt)\n\n')
        outs = []
        for suffix, body in (("worksheet", w), ("answer-key", k)):
            f = f"{self.slug}-{suffix}.typ"
            pathlib.Path(f).write_text(body, encoding="utf-8")   # utf-8: Windows default would crash
            if compile:
                compile_typst(f)
            outs.append(f)
        print(self.slug, n, "questions ->", ", ".join(o.replace('.typ', '.pdf') for o in outs))
        return n
