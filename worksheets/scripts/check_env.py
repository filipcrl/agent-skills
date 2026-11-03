#!/usr/bin/env python3
"""Check that this machine can run the worksheets skill. Run once on a new computer:

    python3 check_env.py        (Windows: py check_env.py)

Checks Python >= 3.8, PyMuPDF (text extraction, figure cropping, renders), Typst (CLI >= 0.11 or the
`typst` pip package), then compiles a tiny test sheet with non-ASCII symbols (µ, □, ≈, γ) in a temp dir.
"""
import os, re, shutil, subprocess, sys, tempfile

ok = True
def report(name, good, msg):
    global ok
    ok &= good
    print(f"[{'OK' if good else 'MISSING'}] {name}: {msg}")

report("python", sys.version_info >= (3, 8), sys.version.split()[0] + " (need >= 3.8)")

try:
    try:
        import pymupdf
    except ImportError:
        import fitz as pymupdf
    report("pymupdf", True, getattr(pymupdf, "VersionBind", getattr(pymupdf, "__version__", "?")))
except ImportError:
    report("pymupdf", False, "pip install pymupdf   (fallback for text only: poppler's pdftotext)")

if shutil.which("typst"):
    v = subprocess.run(["typst", "--version"], capture_output=True, text=True).stdout.strip()
    m = re.search(r"(\d+)\.(\d+)", v)
    report("typst CLI", bool(m) and (int(m[1]), int(m[2])) >= (0, 11), v + " (need >= 0.11)")
else:
    try:
        import typst  # noqa: F401
        report("typst", True, "python package `typst` (no CLI; wslib falls back to it)")
    except ImportError:
        report("typst", False, "install the CLI (brew install typst / winget install Typst.Typst / "
                               "cargo install typst-cli) or: pip install typst")

if ok:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from wslib import Sheet
    cwd = os.getcwd()
    with tempfile.TemporaryDirectory() as d:
        os.chdir(d)
        try:
            s = Sheet("Env test: µ □ ≈ γ", "envtest", course="Test")
            s.part("Part A: Unicode", "Symbols µ □ ≈ γ and math $I_(\"spec\"□) = 2 n mu C_\"ox\" U_T^2$.")
            s.q(r'''Fill in: #ft(("x", "y"), (("1", "2"),))''', "1cm", r'''#at(("x", "y"), [1], [2])''')
            s.build()
            report("test build", os.path.exists("envtest-worksheet.pdf") and os.path.exists("envtest-answer-key.pdf"),
                   "compiled worksheet + answer key")
        except BaseException as e:
            report("test build", False, repr(e))
        finally:
            os.chdir(cwd)

print("\nReady." if ok else "\nFix the MISSING items above, then re-run.")
sys.exit(0 if ok else 1)
