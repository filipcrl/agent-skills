"""Build a worksheet and its answer key (Typst -> PDF).

    from wslib import Sheet
    s = Sheet("Cache Coherence", "coherence", course="CS471")
    s.part("Part A: Foundations", "One-line intro.")
    s.q(r'''Question in Typst markup.
    (a) first sub-part
    (b) second sub-part #ex("2019 Q2b")''', "3cm", r'''Answer.''')
    s.build()   # writes <slug>-worksheet.pdf and <slug>-answer-key.pdf

Typst helpers usable in questions and answers:
    #ex("2021 Q3")                 tag linking to a past exam question
    #ft(header, rows, h: 1.7em)    fill-in table; a row is a label, or an array whose leading
                                   cells are given data (the remaining cells are left blank)
    #at(header, [a], [b], ...)     filled table for answers (cells row-major)
    #fig("figs/x.png", w: 35%)     centred figure
Add more with Sheet(..., extra_head="#let ...").

The answer key repeats each question (blank #ft tables removed) before its answer.
"""
import pathlib, re, shutil, subprocess

HEAD = r'''#set page(paper: "PAPER", margin: (x: 1.5cm, y: 1.3cm),
  footer: context [#set text(8pt); FOOTER #h(1fr) #counter(page).display() / #counter(page).final().first()])
#set text(size: 10pt)
#set par(justify: true)
#let ex(s) = text(8pt, style: "italic")[ (exam link: #s)]
#let ft(header, rows, h: 1.7em) = table(
  columns: (auto,) + (1fr,) * (header.len() - 1), inset: 4pt, align: center + horizon,
  ..header.map(x => [*#x*]),
  ..rows.map(r => {
    let g = if type(r) == array { r } else { (r,) }
    ([*#g.at(0)*],) + g.slice(1).map(x => [#x]) + range(header.len() - g.len()).map(_ => box(height: h))
  }).flatten())
#let at(header, ..cells) = table(columns: header.len(), inset: 4pt, align: center + horizon,
  ..header.map(x => [*#x*]), ..cells.pos())
#let fig(path, w: 35%) = align(center, image(path, width: w))
'''

# In math, "(" right after a sub/superscript gets swallowed into it: $V_"P1"(1+x)$.
ATTACH = re.compile(r'([_^](?:"[^"$]*"|\([^()$]*\)|[A-Za-z0-9]))\(')


def fix(s):
    """Detach "(" from math sub/superscripts and force line breaks before "(a)", "(b)", ..."""
    parts = s.split("$")
    parts[1::2] = [ATTACH.sub(r"\1 (", p) for p in parts[1::2]]
    return "$".join(parts).replace("\n(", " \\\n(")


def strip_ft(s):
    """Remove blank #ft(...) tables (and an #align(center)[...] around them)."""
    wrap = "#align(center)["
    while (i := s.find("#ft(")) >= 0:
        k, depth = i + 3, 0
        while True:
            depth += {"(": 1, ")": -1}.get(s[k], 0)
            k += 1
            if depth == 0:
                break
        if s[:i].endswith(wrap) and s[k:k + 1] == "]":
            i, k = i - len(wrap), k + 1
        s = s[:i] + s[k:]
    return s.strip()


def nodash(s):
    return re.sub(r"\s*[—–]\s*", ": ", s)


def compile_typst(f):
    if shutil.which("typst"):
        subprocess.run(["typst", "compile", f], check=True)
    else:
        import typst  # pip install typst
        typst.compile(f, output=f[:-4] + ".pdf")


class Sheet:
    def __init__(self, title, slug, course="", extra_head="", paper="a4"):
        self.title, self.slug, self.items = nodash(title), slug, []
        footer = f"{course} | {self.title}" if course else self.title
        self.head = HEAD.replace("PAPER", paper).replace("FOOTER", footer) + extra_head

    def part(self, title, intro=""):
        self.items.append((nodash(title), fix(intro)))

    def q(self, text, space, ans):
        self.items.append((fix(text), space, fix(ans)))

    def build(self):
        title = f'#align(center)[#text(16pt, weight: "bold")[{self.title}] \\ #text(12pt)[KIND]]\n'
        w = self.head + title.replace("KIND", "Worksheet") + (
            "Name: #box(width: 3in, repeat[\\_]) #h(1fr) Date: #box(width: 1.4in, repeat[\\_])\n#v(6pt)\n")
        k = self.head + title.replace("KIND", "Answer Key") + "#v(8pt)\n"
        n = 0
        for it in self.items:
            if len(it) == 2:
                t, intro = it
                w += (f'#block(breakable: false, stroke: 0.8pt + black, inset: 6pt, width: 100%)'
                      f'[#text(12pt, weight: "bold")[{t}] \\ #text(9pt)[{intro}]]\n#v(4pt)\n')
                k += f'#v(4pt)\n#text(12pt, weight: "bold")[{t}]\n\n#text(9pt)[{intro}]\n\n'
            else:
                n += 1
                text, space, ans = it
                w += (f'#block(breakable: false, width: 100%)[*{n}.* {text}\n#v({space})]\n'
                      f'#line(length: 100%, stroke: 0.3pt)\n')
                k += (f'#block(stroke: 0.5pt + black, inset: 5pt, width: 100%)[*{n}.* {strip_ft(text)}]\n'
                      f'*Answer.* {ans}\n#v(6pt)\n\n')
        for kind, body in (("worksheet", w), ("answer-key", k)):
            f = f"{self.slug}-{kind}.typ"
            pathlib.Path(f).write_text(body, encoding="utf-8")
            compile_typst(f)
        print(f"{self.slug}: {n} questions")
