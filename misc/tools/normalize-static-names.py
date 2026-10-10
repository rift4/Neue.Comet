"""Normalize static instance name records to the family convention.

`postprocess_instance_ufo.py` derives `postscriptFontName` from the UFO's
familyName + styleName. For some Display instances the familyName already
contains the style, which yields PostScript names like

    NeueCometDisplayThin-Italic
    NeueCometDisplayExtraLight-Regular

These break the `NeueCometDisplay-<Style>` convention used by every sibling,
which in turn breaks family/style grouping in Windows and in font managers.

This pass recomputes name IDs 3, 4, 6 (and 16/17 for the Display family) from
the output filename, which is the authoritative style spec. It is idempotent:
already-correct fonts are left untouched.

Usage:  python misc/tools/normalize-static-names.py build/fonts/static/*.otf
"""
import os
import re
import sys

from fontTools.ttLib import TTFont

FAMILY_TEXT = "Neue Comet"
FAMILY_DISPLAY = "Neue Comet Display"

STYLES = ("Thin", "ExtraLight", "Light", "Regular", "Medium",
          "SemiBold", "Bold", "ExtraBold", "Black")

# name IDs: 3 uniqueID, 4 fullName, 6 postScriptName, 16/17 typographic
WIN = (3, 1, 0x409)
MAC = (1, 0, 0)


def split_style(stem):
    """'NeueCometDisplay-SemiBoldItalic' -> (is_display, base, italic).

    The Regular italic instance ships as 'NeueComet-Italic' (the word
    "Regular" is dropped), so `base` may be empty for a plain 'Italic'.
    """
    for prefix, is_display in (("NeueCometDisplay-", True), ("NeueComet-", False)):
        if stem.startswith(prefix):
            tail = stem[len(prefix):]
            italic = tail.endswith("Italic")
            base = tail[:-len("Italic")] if italic else tail
            if base and base not in STYLES:
                raise ValueError("unknown style %r in %r" % (base, stem))
            return is_display, base, italic
    raise ValueError("unrecognised font name: %r" % stem)


def normalize(path):
    stem = os.path.splitext(os.path.basename(path))[0]
    is_display, base, italic = split_style(stem)

    font = TTFont(path, recalcBBoxes=False, recalcTimestamp=False)
    name = font["name"]

    family = FAMILY_DISPLAY if is_display else FAMILY_TEXT

    # The PostScript name mirrors the filename, which already encodes the
    # family separator correctly ("Regular" is dropped for the plain Italic).
    ps = stem

    # Legacy/full names: family, plus the style words when there are any.
    full = family
    if base:
        full += " " + base
    if italic:
        full += " Italic"

    # Weight-class members of a style-linked group keep their weight in the
    # legacy subfamily name (name ID 2), e.g. "Bold", "Bold Italic". The
    # default Regular of a family is just "Regular"/"Italic". This is what
    # lets Windows group the fonts into one family.
    LINKED = ("Regular", "Bold", "Italic", "Bold Italic")
    if is_display:
        # Display statics are always grouped under the Display family, so
        # name ID 2 is only ever Regular or Italic.
        subfamily = "Italic" if italic else "Regular"
    elif italic:
        subfamily = (base + " Italic") if base else "Italic"
    elif base in ("", "Regular"):
        subfamily = "Regular"
    else:
        subfamily = base

    # name ID 1 (legacy family): the text family's linked styles drop the
    # weight, so that they group together; everything else keeps it.
    if is_display:
        legacy_family = family + (" " + base if base else "")
    elif subfamily in LINKED:
        legacy_family = family
    else:
        legacy_family = family + " " + subfamily

    version = name.getDebugName(5) or ""
    ver = version.replace("Version ", "") if version else "0.000"

    changes = []

    def setn(nid, value, label):
        cur = name.getDebugName(nid)
        if cur != value:
            changes.append("  [%d] %-22s %r -> %r" % (nid, label, cur, value))
            name.setName(value, nid, *WIN)
            name.setName(value, nid, *MAC)

    setn(1, legacy_family, "familyName")
    setn(2, subfamily, "subfamilyName")
    setn(4, full, "fullName")
    setn(6, ps, "postScriptName")
    setn(3, "%s;%s;%s" % (ver, font["OS/2"].achVendID, ps), "uniqueID")

    # Only non-Default weights carry typographic (WWS) names upstream: the
    # Regular/Italic pair is expressed via the legacy names instead.
    if is_display and base not in ("", "Regular"):
        sub = base + (" Italic" if italic else "")
        setn(16, family, "typographicFamily")
        setn(17, sub, "typographicSubfamily")
    else:
        for nid in (16, 17):
            for plat in (WIN, MAC):
                rec = name.getName(nameID=nid, platformID=plat[0],
                                   platEncID=plat[1], langID=plat[2])
                if rec is not None:
                    changes.append("  [%d] %-22s %r -> (removed)"
                                   % (nid, "typographic", rec.toUnicode()))
                    name.removeNames(nameID=nid, platformID=plat[0],
                                     platEncID=plat[1], langID=plat[2])

    font.save(path)
    font.close()

    if changes:
        print("%s" % stem)
        print("\n".join(changes))
    return len(changes)


def main(argv):
    files = argv[1:]
    if not files:
        print(__doc__)
        return 1
    total = sum(normalize(f) for f in files)
    print("\n%d record(s) corrected across %d file(s)" % (total, len(files)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))