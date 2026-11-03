#!/usr/bin/env python3
"""Crop a figure (schematic, plot) out of a slide/exam PDF page into a PNG for a worksheet.

  Locate:  python3 crop_figure.py grid  deck.pdf PAGE            -> _grid_<page>.png (page with a
           labelled 50-pt coordinate grid; view it, read off the figure's bounding box)
  Crop:    python3 crop_figure.py crop  deck.pdf PAGE X0 Y0 X1 Y1 OUT.png [--dpi 220]

PAGE is 1-based (as printed in extract_pdfs.py output). Coordinates are displayed-page points (origin top-left), read off the grid image;
rotated pages are handled.
Crop tightly around the drawing; leave out slide titles, footers, equations and logos.
Always view the cropped PNG before using it.
"""
import sys, time
try:
    import pymupdf
except ImportError:          # PyMuPDF < 1.24 only provides the legacy name
    import fitz as pymupdf


def grid(pdf, page):
    """Render the page as displayed and overlay a grid in DISPLAYED point coordinates (handles
    rotated slide pages, where the internal coordinate system is mirrored/rotated)."""
    d = pymupdf.open(pdf)
    p = d[page - 1]
    W, H = p.rect.width, p.rect.height          # displayed size
    z = 110 / 72
    pix = p.get_pixmap(matrix=pymupdf.Matrix(z, z))
    out_doc = pymupdf.open()
    q = out_doc.new_page(width=pix.width, height=pix.height)
    q.insert_image(q.rect, pixmap=pix)
    for x in range(0, int(W) + 1, 50):
        q.draw_line((x * z, 0), (x * z, pix.height), color=(1, 0, 0), width=0.4)
        q.insert_text((x * z + 1, 9), str(x), fontsize=7, color=(1, 0, 0))
    for y in range(0, int(H) + 1, 50):
        q.draw_line((0, y * z), (pix.width, y * z), color=(1, 0, 0), width=0.4)
        q.insert_text((1, y * z - 1), str(y), fontsize=7, color=(1, 0, 0))
    out = f"_grid_{page}_{int(time.time())}.png"
    q.get_pixmap().save(out)
    print(out, f"(displayed page size {W:.0f} x {H:.0f} pt)")


def crop(pdf, page, x0, y0, x1, y1, out, dpi=220):
    d = pymupdf.open(pdf)
    p = d[page - 1]
    clip = pymupdf.Rect(x0, y0, x1, y1)   # get_pixmap clip uses displayed (page.rect) coords
    p.get_pixmap(dpi=dpi, clip=clip).save(out)
    print(out)


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "grid":
        grid(a[1], int(a[2]))
    elif a and a[0] == "crop":
        dpi = int(a[a.index("--dpi") + 1]) if "--dpi" in a else 220
        crop(a[1], int(a[2]), *map(float, a[3:7]), a[7], dpi)
    else:
        sys.exit(__doc__)
