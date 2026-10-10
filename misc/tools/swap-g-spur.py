#!/usr/bin/env python3
"""Make the spurred G the default shape and the spurless G the cv10 alternate.

Inter draws the plain capital G once and derives the spurred G from it: the
spurred glyph keeps a plain `G` in its background and adds the spur as
foreground contours. That makes "spurred" a delta on top of "spurless", so the
spurred shape cannot become the default without breaking that relationship.

This script rewires the relationship so the spurred shape is the base glyph
and the plain shape is the alternate:

  * every affected base glyph (`G`, `Gbar`, ...) is given the contours that
    currently live in its `.1` counterpart, and its background reference is
    repointed at the new plain alternate;
  * every `.1` glyph is reduced to just that background reference, so it draws
    the plain shape with no spur.

The geometry is moved wholesale rather than edited contour by contour: the
spurred bowl is redrawn with different node coordinates and different anchor
positions, so it is not the plain bowl plus an appendable spur.

Run with --check to report what would change without writing anything.

Usage: python misc/tools/swap-g-spur.py [--check] [glyphspackage ...]
"""
import os
import re
import sys

# base glyph name -> True if its plain shape is stored as a ref in the
# background of the spurred glyph (the normal Glyphs arrangement).
PAIRS = [
    ("G", "G.1"),
    ("Gbar", "Gbar.1"),
    ("Ghook", "Ghook.1"),
    ("Gcircumflex", "Gcircumflex.1"),
    ("Gbreve", "Gbreve.1"),
    ("Gdotaccent", "Gdotaccent.1"),
    # Note the suffix order: the glyph is Gdotaccent.1.ss07, not
    # Gdotaccent.ss07.1, even though the plain pair reads Gdotaccent.ss07.
    ("Gdotaccent.ss07", "Gdotaccent.1.ss07"),
    ("Gcommaaccent", "Gcommaaccent.1"),
    ("Gcaron", "Gcaron.1"),
    ("Gacute", "Gacute.1"),
    ("Gmacron", "Gmacron.1"),
]


def find_files(glyphs_dir, wanted):
    """Map glyphname -> path for the given names, by reading glyphname."""
    found = {}
    for entry in os.listdir(glyphs_dir):
        if not entry.endswith(".glyph"):
            continue
        path = os.path.join(glyphs_dir, entry)
        with open(path, encoding="utf-8", errors="replace") as fp:
            head = fp.read(4096)
        m = re.search(r"glyphname = ([^;]+);", head)
        if m and m.group(1) in wanted:
            found[m.group(1)] = path
    return found


def split_layers(text):
    """Split a .glyph file into (prefix, [(layerId, body), ...], suffix).

    Bodies keep their trailing layer terminator so the file can be rebuilt
    byte-for-byte apart from the edits.
    """
    parts = re.split(r"(\{\n?anchors|)", text)  # placeholder, replaced below
    raise NotImplementedError


def main(argv):
    check = "--check" in argv
    pkgs = [a for a in argv[1:] if not a.startswith("--")] or sorted(
        os.path.join("src", d) for d in os.listdir("src")
        if d.endswith(".glyphspackage")
    )

    rc = 0
    for pkg in pkgs:
        glyphs_dir = os.path.join(pkg, "glyphs")
        if not os.path.isdir(glyphs_dir):
            print("%s: no glyphs dir, skipped" % pkg)
            rc = 1
            continue

        # The variants that can exist for a base glyph: the plain one, the
        # spurred .1, and -- only for Gdotaccent -- the ss07 forms. Do not
        # synthesise combinations like "G.1.ss07"; those do not exist and
        # would report as spurious missing glyphs.
        wanted = set()
        for base, alt in PAIRS:
            wanted.add(base)
            wanted.add(alt)
        found = find_files(glyphs_dir, wanted)

        print("=" * 68)
        print(pkg)
        missing = [w for w in sorted(wanted) if w not in found]
        for m in missing:
            print("  MISSING: %s" % m)
        if missing:
            print("  -> aborting, required glyphs missing")
            rc = 1
            continue

        for base_name, alt_name in PAIRS:
            base = found[base_name]
            alt = found[alt_name]
            print("  %-18s base=%-24s alt=%s" % (
                base_name, os.path.basename(base), os.path.basename(alt)))

    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))