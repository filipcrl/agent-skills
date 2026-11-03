#!/usr/bin/env python3
"""Check that this machine can run the worksheets skill: python3 check_env.py"""
import os, sys, tempfile

print("python", sys.version.split()[0])
if sys.version_info < (3, 8):
    sys.exit("Need Python 3.8 or newer.")
try:
    import pymupdf
except ImportError:
    try:
        import fitz as pymupdf  # PyMuPDF < 1.24
    except ImportError:
        sys.exit("Missing PyMuPDF: pip install pymupdf")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wslib import Sheet

with tempfile.TemporaryDirectory() as d:
    os.chdir(d)
    s = Sheet("Env test: µ □ ≈ γ", "envtest", course="Test")
    s.part("Part A", 'Math $I_"spec" = 2 n mu C_"ox" U_T^2$.')
    s.q('Fill in: #ft(("x", "y"), (("1",),))', "1cm", '#at(("x", "y"), [1], [2])')
    try:
        s.build()
    except Exception as e:
        sys.exit(f"Typst build failed ({e!r}). Install Typst 0.11+ (brew install typst, "
                 "winget install Typst.Typst) or: pip install typst")
print("Ready.")
