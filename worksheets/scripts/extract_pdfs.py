#!/usr/bin/env python3
"""Extract text from slide decks / exam PDFs into .txt files (one '=== pN ===' header per page).

    python3 extract_pdfs.py OUT_DIR file1.pdf [file2.pdf ...]

Drops common slide-footer noise (course/lecture/slide-number lines, calendar cells).
Needs PyMuPDF (`import pymupdf`); falls back to `pdftotext` if available.
"""
import re, sys, pathlib, shutil, subprocess

NOISE = re.compile(r'^(Lec\.?\s*\d+.*Slide \d+|Slide \d+|\d{1,2}-(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)|[MTWFS])$')

def extract(pdf):
    try:
        import pymupdf
    except ImportError:
        try:
            import fitz as pymupdf   # PyMuPDF < 1.24
        except ImportError:
            pymupdf = None
    if pymupdf is None:
        if shutil.which("pdftotext"):
            return subprocess.run(["pdftotext", "-layout", pdf, "-"], capture_output=True, text=True).stdout
        sys.exit("Install PyMuPDF (pip install pymupdf) or poppler (pdftotext).")
    d = pymupdf.open(pdf)
    pages = []
    for i, p in enumerate(d):
        lines = [l for l in p.get_text().split('\n') if not NOISE.match(l.strip())]
        pages.append(f'=== p{i+1} ===\n' + '\n'.join(lines))
    return '\n'.join(pages)

if __name__ == "__main__":
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    for f in sys.argv[2:]:
        t = extract(f)
        dst = out / (pathlib.Path(f).stem + ".txt")
        dst.write_text(t, encoding="utf-8")
        print(f"{f}: {t.count('=== p')} pages, {len(t)} chars -> {dst}")
