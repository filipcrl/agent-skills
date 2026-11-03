#!/usr/bin/env python3
"""Crop a figure out of a PDF page into a PNG.

    python3 crop_figure.py grid deck.pdf PAGE                       page image with a 50 pt grid
    python3 crop_figure.py crop deck.pdf PAGE X0 Y0 X1 Y1 OUT.png   crop that box (in points)

PAGE is 1-based. Read the box off the grid image, crop, and look at the result.
"""
import sys, time
try:
    import pymupdf
except ImportError:
    import fitz as pymupdf  # PyMuPDF < 1.24

a = sys.argv[1:]
if len(a) < 3 or a[0] not in ("grid", "crop"):
    sys.exit(__doc__)
page = pymupdf.open(a[1])[int(a[2]) - 1]

if a[0] == "crop":
    page.get_pixmap(dpi=220, clip=pymupdf.Rect(*map(float, a[3:7]))).save(a[7])
    print(a[7])
else:
    # Draw the grid on a rendered image so it matches the displayed (possibly rotated) page.
    z = 1.5
    pix = page.get_pixmap(matrix=pymupdf.Matrix(z, z))
    g = pymupdf.open().new_page(width=pix.width, height=pix.height)
    g.insert_image(g.rect, pixmap=pix)
    for v in range(0, int(max(page.rect.width, page.rect.height)) + 1, 50):
        g.draw_line((v * z, 0), (v * z, pix.height), color=(1, 0, 0), width=0.4)
        g.draw_line((0, v * z), (pix.width, v * z), color=(1, 0, 0), width=0.4)
        g.insert_text((v * z + 1, 9), str(v), fontsize=7, color=(1, 0, 0))
        g.insert_text((1, v * z - 1), str(v), fontsize=7, color=(1, 0, 0))
    out = f"_grid_{a[2]}_{int(time.time())}.png"
    g.get_pixmap().save(out)
    print(out)
