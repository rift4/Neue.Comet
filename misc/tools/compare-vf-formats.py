#!/usr/bin/env python3
"""Compare the glyf and CFF2 variable fonts of Neue Comet by rasterising them.

A CFF2 build that draws differently from the glyf build it was generated from
means outline variation was lost or mis-compiled - the class of bug that only
shows up once the font is rendered.

This is deliberately a *pixel* comparison rather than a comparison of outline
data: glyf glyphs expose quadratic pen calls and CFF2 exposes cubic ones, so
comparing pen output would always report a difference that does not exist.

For a grid of (opsz, wght) locations both fonts are rasterised at the same
size and the resulting bitmaps are compared.

Usage: python misc/tools/compare-vf-formats.py [size]
"""
import os
import sys

import numpy as np
from PIL import Image
from fontTools.ttLib import TTFont
from fontTools.misc.transform import Transform
from fontTools.pens.freetypePen import FreeTypePen
from fontTools.varLib.instancer import instantiateVariableFont

TTF = "build/fonts/var/NeueCometVariable.ttf"
OTF = "build/fonts/var/NeueCometVariable.otf"

# (wght, opsz). Defaults, both axis extremes, both corners, and interior points.
LOCATIONS = [
    (400, 14), (100, 14), (900, 14), (400, 32),
    (100, 32), (900, 32),
    (250, 14), (300, 20), (500, 18), (700, 23), (800, 28),
]

TEXT = ("Hamburgefonstiv 0123456789 "
        "\u00e4\u00f6\u00fc\u00df\u00c5 \u0391\u03b2\u0433\u0414"
        "frac 1/2 \u2192 \u2026")


def render(path, wght, opsz, px):
    """Rasterise TEXT at the given design location; return (image, advance)."""
    font = TTFont(path)
    instantiateVariableFont(font, {"wght": wght, "opsz": opsz}, inplace=True)

    gs = font.getGlyphSet()
    cmap = font.getBestCmap()
    hmtx = font["hmtx"]

    glyphs = []
    for ch in TEXT:
        gname = cmap.get(ord(ch))
        if gname is not None:
            glyphs.append(gname)

    upm = font["head"].unitsPerEm
    scale = px / upm
    advance = sum(hmtx[g][0] for g in glyphs)
    W = max(1, int(advance * scale) + 16)
    H = int(1.4 * px)

    canvas = np.zeros((H, W), dtype=float)
    x = 0.0
    for gname in glyphs:
        pen = FreeTypePen(gs)
        gs[gname].draw(pen)
        arr = pen.array(width=W, height=H,
                        transform=Transform(scale, 0, 0, scale, x, H * 0.75))
        np.maximum(canvas, arr, out=canvas)
        x += hmtx[gname][0] * scale

    img = Image.fromarray((np.clip(canvas, 0, 1) * 255).astype(np.uint8), "L")
    font.close()
    return img, advance, img



def diff(a, b):
    """Return (n_differing, worst, mean, note) comparing two rasters.

    glyf stores quadratic outlines and CFF2 stores cubic ones, so the same
    master outline round-trips through a different representation. Some
    antialiasing-level pixel differences are therefore expected; what must
    not happen is a structural difference (different size, or a visibly
    different shape).
    """
    if a.size != b.size:
        return None, 0, 0.0, "size %s vs %s" % (a.size, b.size)
    pa, pb = a.tobytes(), b.tobytes()
    deltas = [abs(x - y) for x, y in zip(pa, pb) if x != y]
    if not deltas:
        return 0, 0, 0.0, ""
    worst = max(deltas)
    mean = sum(deltas) / len(deltas)
    total = len(pa)
    return len(deltas), worst, mean, "%d/%d px (%.2f%%), mean %.1f" % (
        len(deltas), total, 100.0 * len(deltas) / total, mean)


# Tolerance: below this the two formats are treated as rendering the same
# design. ~8% of pixels differing by a mean of under 12/255 is antialiasing
# noise from the quadratic/cubic round trip, not a shape difference.
MAX_DIFF_PCT = 12.0
MAX_MEAN_DELTA = 12.0


def main():
    px = int(sys.argv[1]) if len(sys.argv) > 1 else 48
    outdir = sys.argv[2] if len(sys.argv) > 2 else None
    print("rasterising at %dpx em\n" % px)
    bad = 0
    for wght, opsz in LOCATIONS:
        ia, adva, na = render(TTF, wght, opsz, px)
        ib, advb, nb = render(OTF, wght, opsz, px)
        n, worst, mean, note = diff(na, nb)

        if n is None:
            status, bad = "SIZE MISMATCH", bad + 1
        elif n == 0:
            status = "identical"
        else:
            pct = 100.0 * n / (na.size[0] * na.size[1])
            if pct <= MAX_DIFF_PCT and mean <= MAX_MEAN_DELTA:
                status = "within tolerance"
            else:
                status = "MISMATCH"
                bad += 1

        advnote = "same" if adva == advb else \
            "%d vs %d  (%.3f%% of em)" % (adva, advb, 100.0 * abs(adva - advb) / 2048)
        print("wght=%-4g opsz=%-3g  %-18s advance %-34s %s"
              % (wght, opsz, status, advnote, note))

        if outdir:
            os.makedirs(outdir, exist_ok=True)
            na.save("%s/glyf-w%g-o%g.png" % (outdir, wght, opsz))
            nb.save("%s/cff2-w%g-o%g.png" % (outdir, wght, opsz))

    print()
    print("compared %d locations at %dpx" % (len(LOCATIONS), px))
    print("EQUIVALENT (within antialiasing tolerance)"
          if bad == 0 else "%d LOCATION(S) STRUCTURALLY DIFFER" % bad)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())