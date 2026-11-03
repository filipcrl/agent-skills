#!/usr/bin/env python3
"""Quality checks for generated worksheets. Run in the directory with the .typ files.

    python3 check_sheets.py [slug ...]        # default: all *-worksheet.typ

Reports:
  1. Self-containment violations in questions (references to slides/lectures/other questions).
  2. Bare underscores outside code; '(' glued to a math sub/superscript ([attach]). (Typst turns them into emphasis and swallows them).
  3. Question list (number + first 200 chars) for a manual read-through.
Optionally renders pages to PNG for visual checks:  --render slug page [page...]
(PNG names include a counter so image viewers don't show a cached old render.)
"""
import re, sys, glob, time

REF = re.compile(r".{0,50}\b(slides?|lectures?|in class|(?<!-)readers?|previous question|earlier question|"
                 r"same machine|same program|same system|from part|\(part [a-h]\)|part [a-h]\)|shown above|"
                 r"figures?(?!-of-merit)|listed in|given in the|covered in)\b.{0,40}", re.I)

def questions(t):
    for m in re.finditer(r'#block\(breakable: false, width: 100%\)\[\*(\d+)\.\* (.*?)\n#v\(', t, re.S):
        yield m.group(1), m.group(2)

def strip_code(t):
    t = re.sub(r'```.*?```', '', t, flags=re.S)
    return re.sub(r'`[^`\n]*`', '', t)

def main(slugs):
    files = [f"{s}-worksheet.typ" for s in slugs] if slugs else sorted(glob.glob("*-worksheet.typ"))
    for f in files:
        t = open(f, encoding="utf-8").read()
        print(f"\n===== {f}")
        for n, q in questions(t):
            for m in REF.finditer(q):
                # a question that embeds its own figure (#fig) may refer to it
                if '#fig(' in q and re.search(r"figures?|shown above", m.group(0), re.I):
                    continue
                print(f"  [ref] Q{n}: ...{m.group(0)}...")
        for g in (f, f.replace("-worksheet", "-answer-key")):
            src = open(g, encoding="utf-8").read().split('$')
            for j in range(1, len(src), 2):
                for m in re.finditer(r'[_^](?:"[^"$]*"|\([^()$]*\)|[A-Za-z0-9])\(', src[j]):
                    print(f"  [attach] {g}: ${src[j][max(0, m.start()-15):m.end()+10]}$  -> add a space before '('")
            body = strip_code(open(g, encoding="utf-8").read()).split('\n', 20)[-1]
            body = re.sub(r'\$[^$]*\$', '', body)   # '_' inside math is a subscript, not a bug
            for m in re.finditer(r'(?<![\\#(a-zA-Z])_', body):
                print(f"  [underscore] {g}: ...{body[max(0, m.start()-40):m.start()+20]!r}")
        for n, q in questions(t):
            q = re.sub(r'#fig\([^)]*\)', '[FIG]', q)
            q = re.sub(r'#(ft|at|snap|align|table)\(.*', '[TABLE]', q, flags=re.S)
            print(f"  {n:>3} {q.replace(chr(10), ' ')[:200]}")

def render(slug, pages):
    try:
        import pymupdf
    except ImportError:
        import fitz as pymupdf
    for kind in ("worksheet", "answer-key"):
        d = pymupdf.open(f"{slug}-{kind}.pdf")
        for p in pages:
            if p < len(d):
                name = f"_render_{slug}_{kind}_p{p}_{int(time.time())}.png"
                d[p].get_pixmap(dpi=60).save(name); print(name)

if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--render":
        render(a[1], [int(x) for x in a[2:]] or [0])
    else:
        main(a)
