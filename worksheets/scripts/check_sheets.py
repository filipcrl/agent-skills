#!/usr/bin/env python3
"""Check generated worksheets. Run in the directory with the .typ files.

    python3 check_sheets.py [slug ...]            references to slides/other questions, stray
                                                  underscores, and a list of all questions
    python3 check_sheets.py --render slug page... render pages of both PDFs to PNG
"""
import glob, re, sys, time

REF = re.compile(r".{0,50}\b(slides?|lectures?|in class|previous question|earlier question|same program|"
                 r"same machine|from part|part [a-h]\)|shown above|figures?|listed in|covered in)\b.{0,40}", re.I)


def check(slugs):
    files = [f"{s}-worksheet.typ" for s in slugs] or sorted(glob.glob("*-worksheet.typ"))
    for f in files:
        t = open(f, encoding="utf-8").read()
        qs = re.findall(r"\[\*(\d+)\.\* (.*?)\n#v\(", t, re.S)
        print(f"\n===== {f}")
        for n, q in qs:
            for m in REF.finditer(q):
                if not ("#fig(" in q and re.search("figure|shown above", m[0], re.I)):
                    print(f"  [ref] Q{n}: ...{m[0]}...")
        for g in (f, f.replace("-worksheet", "-answer-key")):
            body = open(g, encoding="utf-8").read().split("\n", 20)[-1]
            body = re.sub(r"```.*?```|`[^`\n]*`|\$[^$]*\$", "", body, flags=re.S)
            for m in re.finditer(r"(?<![\\#(a-zA-Z])_", body):
                print(f"  [underscore] {g}: ...{body[max(0, m.start() - 40):m.start() + 20]!r}")
        for n, q in qs:
            q = re.sub(r"#(ft|at|align)\(.*", "[TABLE]", q, flags=re.S)
            print(f"  {n:>3} {' '.join(q.split())[:200]}")


def render(slug, pages):
    try:
        import pymupdf
    except ImportError:
        import fitz as pymupdf
    for kind in ("worksheet", "answer-key"):
        d = pymupdf.open(f"{slug}-{kind}.pdf")
        for p in pages:
            name = f"_render_{slug}_{kind}_p{p}_{int(time.time())}.png"  # fresh name: viewers cache
            d[p].get_pixmap(dpi=60).save(name)
            print(name)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[:1] == ["--render"]:
        render(a[1], [int(x) for x in a[2:]] or [0])
    else:
        check(a)
