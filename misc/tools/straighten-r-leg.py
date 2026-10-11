#!/usr/bin/env python3
"""Replace the diagonal R leg with a vertical one.

Inter's capital R has a leg that slants down and to the right. This rewrites
it as a vertical stem dropping straight to the baseline, matching the reference
the designer supplied.

The leg is a simple 4-node contour in every design master, so only that
contour is touched. The bowl and stem are left completely alone.

Geometry, derived per master rather than hard-coded, so the result still
interpolates across the weight axis:

  leg width   = the stem width at the baseline, i.e. the horizontal distance
                between the first and last node at y=0. The reference design
                has a leg exactly as wide as the stem.
  leg right   = the rightmost point of the bowl's bottom bar. That is the
                largest x among the bowl's nodes at or below the leg's current
                top y. Hanging the leg from the end of that bar is what keeps
                it attached: the bar spans y=bar_top..bar_bottom and the leg's
                top sits inside it, so the joint is unchanged.
  leg top     = the leg's existing top y (unchanged, so it stays buried in
                the bar)
  leg bottom  = 0, as before

Only the 6 masters that the variable font actually interpolates are rewritten.
Layers belonging to no shipped font are left alone and reported.

Usage: python misc/tools/straighten-r-leg.py [--check] [src/*.glyphspackage ...]
"""
import os
import re
import sys

def master_ids(pkg):
    """Layer ids of the masters this build actually interpolates.

    The three weight masters are named in fontinfo.plist; the optical-size
    partners are the layers named mNNN. Both are needed, and the ids differ
    between Roman and Italic, so they are read rather than hard-coded.
    """
    fi = os.path.join(pkg, "fontinfo.plist")
    ids = set()
    if os.path.exists(fi):
        txt = open(fi, encoding="utf-8", errors="replace").read()
        for m in re.finditer(r'id = "([0-9A-Fa-f-]{36})"', txt):
            ids.add(m.group(1))
    return ids


def layer_is_master(lid, ids):
    """True for a named weight master or an mNNN optical-size master."""
    if lid in ids:
        return True
    return bool(re.fullmatch(r"m\d+", lid))


def match_paren(text, i):
    """Given index of '(', return index just past the matching ')'."""
    depth = 0
    while i < len(text):
        if text[i] == "(":
            depth += 1
        elif text[i] == ")":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    raise ValueError("unbalanced parentheses")


def split_top_level(body):
    """Split a Glyphs list body on top-level commas, respecting parens."""
    parts, depth, cur = [], 0, ""
    for ch in body:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
        if ch == "," and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += ch
    if cur.strip():
        parts.append(cur)
    return parts


def find_layers(text):
    """Yield (layer_id, start, end) for each *layer* block in a .glyph file.

    A layer looks like

        {
        anchors = ( ... );
        shapes = ( {closed = 1; nodes = (...);}, ... );
        layerId = "XXXX";
        width = 1260;
        },

    Naively taking the nearest "{" before layerId picks up an anchor or a
    component block instead. The layer's own opening brace is the one whose
    match closes the block, so walk backwards from layerId counting braces and
    take the start that brings the depth to zero.
    """
    out = []
    for m in re.finditer(r"layerId = (\"[^\"]+\"|[^;]+);", text):
        i = m.start() - 1
        depth = 0
        while i >= 0:
            if text[i] == "}":
                depth += 1
            elif text[i] == "{":
                if depth == 0:
                    break
                depth -= 1
            i -= 1
        start = i
        # forward to this brace's match
        depth, j = 0, start
        while j < len(text):
            if text[j] == "{":
                depth += 1
            elif text[j] == "}":
                depth -= 1
                if depth == 0:
                    break
            j += 1
        out.append((m.group(1).strip().strip('"'), start, j + 1))
    return out


def parse_nodes(block):
    """Return list of (x, y, kind) from a Glyphs `nodes = (...)` list."""
    m = re.search(r"nodes = \(", block)
    if not m:
        return None
    open_paren = m.end() - 1
    close = match_paren(block, open_paren)
    inner = block[open_paren + 1: close - 1]
    nodes = []
    for item in split_top_level(inner):
        item = item.strip()
        if not item:
            continue
        mm = re.match(r"\(\s*(-?\d+)\s*,\s*(-?\d+)\s*(?:,\s*([a-z]+)\s*)?\)", item)
        if mm:
            nodes.append((int(mm.group(1)), int(mm.group(2)), mm.group(3) or "l"))
    return nodes


def render_nodes(nodes):
    """Re-emit a whole contour: the opening brace and closed flag included.

    Replacing only the "nodes = (...)" payload silently drops the enclosing
    "{ closed = 1;" and the contour's closing "}", which leaves a .glyph file
    that still looks plausible in a diff but no longer parses.
    """
    body = ",\n".join("(%d,%d,%s)" % (x, y, k) for x, y, k in nodes)
    return "{\nclosed = 1;\nnodes = (\n%s\n);\n}" % body


def main(argv):
    dry = "--check" in argv
    pkgs = [a for a in argv[1:] if not a.startswith("--")] or sorted(
        os.path.join("src", d) for d in os.listdir("src")
        if d.endswith(".glyphspackage"))
    rc = 0
    for pkg in pkgs:
        path = os.path.join(pkg, "glyphs", "R_.glyph")
        if not os.path.exists(path):
            print("%s: no R_.glyph, skipped" % pkg)
            rc = 1
            continue
        text = open(path, encoding="utf-8").read()
        print("=" * 70)
        print(pkg + ("   (--check, nothing written)" if dry else ""))

        edits = []
        masters = master_ids(pkg)
        for lid, start, end in find_layers(text):
            key = lid[:12]
            if not layer_is_master(lid, masters):
                continue
            block = text[start:end]
            # Only the foreground shapes count. A master may also carry a
            # background holding a merged copy of the outline (Regular does),
            # and that copy spans the leg too -- parsing it yields a stem
            # width of ~1000 units and a bogus bar end. In a .glyph layer the
            # foreground shapes are everything after layerId.
            lid_pos = block.find("layerId")
            fg = block[lid_pos:] if lid_pos != -1 else block
            contours = []
            for m in re.finditer(r"\{\s*closed = 1;", fg):
                cstart = m.start()
                # the contour's braces wrap the whole shape, including the
                # node list's own parentheses; match on braces, not on "\n};"
                depth, j = 0, cstart
                while j < len(fg):
                    if fg[j] == "{":
                        depth += 1
                    elif fg[j] == "}":
                        depth -= 1
                        if depth == 0:
                            break
                    j += 1
                cend = j + 1
                contours.append((cstart, cend, parse_nodes(fg[cstart:cend])))
            contours = [c for c in contours if c[2]]
            if not contours:
                print("  %s: no foreground contours found" % key)
                rc = 1
                continue
            leg = next((c for c in contours if len(c[2]) == 4), None)
            # The bowl is the stem+bowl outline: the largest non-4-node contour
            # that reaches the cap height. Picking "the first one that is not
            # the leg" is wrong: some masters also carry a merged copy of the
            # outline in their background, which spans the leg as well and
            # would report a stem width of ~1000 units.
            bowl = None
            for c in contours:
                if len(c[2]) == 4:
                    continue
                if bowl is None or len(c[2]) > len(bowl[2]):
                    bowl = c
            if leg is None or bowl is None:
                print("  %s: could not identify leg(4 nodes)/bowl" % key)
                rc = 1
                continue

            lnodes, bnodes = leg[2], bowl[2]
            top_y = max(n[1] for n in lnodes)

            # Stem width from the baseline. Use the leftmost two baseline
            # nodes: the stem is the leftmost element there, so the span
            # between the two smallest x is the stem and nothing else. Using
            # min/max would also catch the leg's own baseline nodes on masters
            # where the two share a contour.
            base = sorted(n[0] for n in bnodes if n[1] == 0)
            if len(base) < 2:
                print("  %s: no baseline nodes in bowl" % key)
                rc = 1
                continue
            stem_w = base[1] - base[0]

            # right end of the bowl's bottom bar
            low = [n[0] for n in bnodes if n[1] <= top_y]
            bar_end = max(low) if low else max(n[0] for n in bnodes)

            right = bar_end
            left = bar_end - stem_w
            new = [(left, 0, "l"), (right, 0, "l"), (right, top_y, "l"), (left, top_y, "l")]

            print("  %s leg %s -> x %d..%d (w=%d, stem=%d, bar_end=%d, top_y=%d)"
                  % (key, lnodes, left, right, stem_w, stem_w, bar_end, top_y))
            # contour offsets are relative to `fg`, which itself starts
            # lid_pos into the layer block
            edits.append((start + lid_pos + leg[0],
                          start + lid_pos + leg[1],
                          render_nodes(new)))

        for cstart, cend, repl in sorted(edits, reverse=True):
            text = text[:cstart] + repl + text[cend:]
        if not dry and edits:
            open(path, "w", encoding="utf-8").write(text)
            print("  wrote %d masters" % len(edits))
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))