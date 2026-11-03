#!/usr/bin/env python3
"""Extract the text of PDFs into OUT_DIR/<name>.txt, with a "=== pN ===" line per page.

    python3 extract_pdfs.py OUT_DIR file1.pdf [file2.pdf ...]
"""
import pathlib, sys
try:
    import pymupdf
except ImportError:
    import fitz as pymupdf  # PyMuPDF < 1.24

out = pathlib.Path(sys.argv[1])
out.mkdir(parents=True, exist_ok=True)
for f in sys.argv[2:]:
    pages = [f"=== p{i + 1} ===\n{p.get_text()}" for i, p in enumerate(pymupdf.open(f))]
    dst = out / (pathlib.Path(f).stem + ".txt")
    dst.write_text("\n".join(pages), encoding="utf-8")
    print(f"{f}: {len(pages)} pages -> {dst}")
