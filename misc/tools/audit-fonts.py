#!/usr/bin/env python3
"""Audit shipped Neue Comet binaries for branding and metadata correctness.

Usage: python misc/tools/audit-fonts.py [dir]   (default: docs/font-files)
"""
import os, sys
from fontTools.ttLib import TTFont

ROOT = os.environ.get("COMET_FONT_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__)))), "docs", "font-files"))

# Attribution that MUST survive (OFL + provenance), per name ID.
INTENTIONAL = {
    0:  "The Inter Project Authors",
    7:  "Inter is a trademark of Rasmus Andersson",
    9:  "Zap, based on Inter by",
}

EXPECT_FAMILY = {
    "NeueCometDisplay-": "Neue Comet Display",
    "NeueComet-":        "Neue Comet",
}

# Script coverage actually advertised in README.md. Keep the two in sync:
# if you add a script, add it here AND update the README table.
COVERED = {
    "Latin":         [(0x0041, 0x024F), (0x1E00, 0x1EFF)],
    "Greek":         [(0x0370, 0x03FF), (0x1F00, 0x1FFF)],
    "Cyrillic":      [(0x0400, 0x052F), (0x2DE0, 0x2DFF)],
    "Punctuation":   [(0x2000, 0x206F)],
    "Sup/Subs":      [(0x2070, 0x209F)],
    "Currency":      [(0x20A0, 0x20CF)],
    "Numberforms":   [(0x2150, 0x218F)],
    "Arrows/Math":   [(0x2190, 0x22FF)],
    "Technical":     [(0x2300, 0x23FF)],
    "Geometric":     [(0x25A0, 0x25FF)],
    "Symbols":       [(0x2600, 0x27BF)],
}

# Scripts the README states are NOT covered. A non-zero count here means
# either the source gained glyphs (update README + COVERED) or something broke.
NOT_COVERED = {
    "Bengali":    (0x0980, 0x09FF),
    "Devanagari": (0x0900, 0x097F),
    "Gurmukhi":   (0x0A00, 0x0A7F),
    "Gujarati":   (0x0A80, 0x0AFF),
    "Tamil":      (0x0B80, 0x0BFF),
    "Thai":       (0x0E00, 0x0E7F),
    "Hebrew":     (0x0590, 0x05FF),
    "Arabic":     (0x0600, 0x06FF),
    "CJK":        (0x4E00, 0x9FFF),
    "Hangul":     (0xAC00, 0xD7AF),
}

# Codepoints that fall inside a NOT_COVERED range but are genuinely covered
# by another category. U+0E3F THAI CURRENCY SYMBOL BAHT sits in the Thai
# block but is a currency sign (counted under "Currency"); it does not
# constitute Thai support.
EXEMPT = {
    0x0E3F,
}


def check_coverage(cmap):
    """Return (errors, summary) for the script coverage claims."""
    errs, summary = [], []
    for name, ranges in COVERED.items():
        n = sum(1 for a, b in ranges for c in cmap if a <= c <= b)
        summary.append((name, n))
        if n == 0:
            errs.append("README claims %s coverage but 0 codepoints found" % name)
    for name, (lo, hi) in NOT_COVERED.items():
        n = sum(1 for c in cmap if lo <= c <= hi and c not in EXEMPT)
        if n:
            errs.append("README says %s is not covered, but %d codepoint(s) are "
                        "present - update README.md and COVERED" % (name, n))
    return errs, summary


def main():
    files = sorted(f for f in os.listdir(ROOT) if f.endswith(".woff2"))
    print("auditing %d files in %s\n" % (len(files), ROOT))
    bad = 0
    rows = []
    for fn in files:
        path = os.path.join(ROOT, fn)
        f = TTFont(path, lazy=True)
        stem = fn[:-6]
        is_vf = "Variable" in stem

        fam   = f["name"].getDebugName(1)
        sub   = f["name"].getDebugName(2)
        full  = f["name"].getDebugName(4)
        ps    = f["name"].getDebugName(6)
        vend  = f["OS/2"].achVendID
        wclass= f["OS/2"].usWeightClass
        italic= bool(f["OS/2"].fsSelection & 1)

        errs = []
        # 1. no stale "Inter" branding except the whitelisted attribution
        for nid in (0, 1, 2, 4, 6, 8, 9, 11, 12, 16, 17, 21, 22):
            v = f["name"].getDebugName(nid)
            if not v:
                continue
            if "Inter" in v and INTENTIONAL.get(nid) not in v:
                errs.append("name[%d] stale 'Inter': %r" % (nid, v))
        # 2. PostScript name must equal the filename stem (family convention).
        #    Variable fonts are the one exception: upstream ships
        #    InterVariable-Italic.woff2 with a ps name of InterVariableItalic.
        if not is_vf and ps != stem:
            errs.append("ps name %r != filename stem %r" % (ps, stem))
        if ps and " " in ps:
            errs.append("ps name has a space: %r" % ps)
        # 3. vendor ID
        if vend != "NONE":
            errs.append("achVendID=%r (expected NONE)" % vend)
        # 4. family expectation
        if is_vf:
            if fam != "Neue Comet Variable":
                errs.append("VF family=%r" % fam)
        else:
            exp = EXPECT_FAMILY["NeueCometDisplay-" if stem.startswith("NeueCometDisplay-") else "NeueComet-"]
            if not (fam or "").startswith(exp):
                errs.append("family=%r does not start with %r" % (fam, exp))
        # 5. style/weight consistency
        if not is_vf:
            stem_is_italic = stem.endswith("Italic")
            if italic != stem_is_italic:
                errs.append("fsSelection italic=%s but filename says %s" % (italic, stem_is_italic))
            if wclass % 100:
                errs.append("usWeightClass=%d not a multiple of 100" % wclass)

        rows.append((fn, fam, sub, ps, wclass, "VF" if is_vf else "", errs))
        bad += len(errs)
        f.close()

    print("%-44s %-30s %-34s %5s %-3s" % ("file", "name ID 1", "postScriptName", "wght", "vf"))
    print("-" * 122)
    for fn, fam, sub, ps, wclass, vf, errs in rows:
        print("%-44s %-30s %-34s %5s %-3s" % (fn, fam, ps, wclass, vf))
    print()
    for fn, fam, sub, ps, wclass, vf, errs in rows:
        for e in errs:
            print("FAIL %-44s %s" % (fn, e))

    # Script coverage is a whole-family claim, so check it once, against
    # the Regular. README.md documents exactly these scripts.
    ref = os.path.join(ROOT, "NeueComet-Regular.woff2")
    if os.path.exists(ref):
        f = TTFont(ref)
        cmap = set(f.getBestCmap().keys())
        cov_errs, summary = check_coverage(cmap)
        f.close()
        print("script coverage (from NeueComet-Regular, %d codepoints):"
              % len(cmap))
        for name, n in summary:
            print("  %-14s %5d" % (name, n))
        for e in cov_errs:
            print("FAIL %-44s %s" % ("<coverage>", e))
        bad += len(cov_errs)

    print("\n%s  (%d problem(s) across %d files)"
          % ("ALL PASS" if bad == 0 else "FAILURES", bad, len(files)))
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main())