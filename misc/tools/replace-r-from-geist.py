#!/usr/bin/env python3
"""Replace Neue Comet's capital R with Geist's, fitted to our metrics.

Geist's R has a vertical leg where Inter's slants. This installs Geist's
outline as the R, then puts it back on our own metrics so it does not disturb
the surrounding text.

The outline is read from the Geist Glyphs sources, not reconstructed from a
compiled binary. Reconstructing from pen output means inventing Glyphs node
types -- and an invented 's' forces a smooth tangent that pulls corners round
and drags stems out of straight, which is what produced a spiked, unreadable R
on an earlier attempt. Reading the real nodes means every type is carried
across unchanged.

Both fonts are under the SIL Open Font License 1.1; the notices are in
LICENSE.txt.

Fitting, per master:

  scale   = our cap height / Geist's, so the R sits on the same cap line as
            the rest of the alphabet instead of 36 units below it.
  x       = translated so the left sidebearing matches the R's own previous
            value; every straight-sided capital in this family sits at 180.
  advance = lsb + new ink width + the R's previous right sidebearing, keeping
            the letter's spacing character and the text rhythm unchanged.
  kerning = pairs where R is the first glyph are reduced by the advance
            delta, since a wider R pushes what follows further away.

Geist has three masters (Thin/Regular/Black) and no optical-size axis, so a
weight's outline serves both its text and display master here.

Usage: python misc/tools/replace-r-from-geist.py [--check] [pkg ...]
"""
import os
import re
import sys

from glyphsLib import GSFont

GEIST_SRC = "/home/zei/Projects/geist-font/sources"
GEIST_PKG = {
    "Roman": os.path.join(GEIST_SRC, "Geist.glyphspackage"),
    "Italic": os.path.join(GEIST_SRC, "Geist-Italic.glyphspackage"),
}
WEIGHT_OF = {"Thin": 100, "Regular": 400, "Italic": 400, "Black": 900}
# glyphsLib node types -> Glyphs .glyph suffixes
SUFFIX = {
    "line": "l", "corner": "l", "smooth": "s",
    "offcurve": "o", "curve": "c", "qcurve": "c",
    "hcurve": "hc", "vcurve": "vo", "hcorner": "hc", "vcorner": "vo",
}


# ---------------------------------------------------------------- our source

def match_paren(text, i):
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


def parse_nodes(block):
    m = re.search(r"nodes = \(", block)
    if not m:
        return None
    op = m.end() - 1
    inner = block[op + 1: match_paren(block, op) - 1]
    out = []
    for item in split_top_level(inner):
        mm = re.match(r"\(\s*(-?\d+)\s*,\s*(-?\d+)\s*(?:,\s*([a-z]+)\s*)?\)", item.strip())
        if mm:
            out.append((int(mm.group(1)), int(mm.group(2)), mm.group(3) or "l"))
    return out


def find_layers(text):
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


def foreground(block):
    """(offset_of_foreground, [(start, end, nodes)]) for one layer."""
    p = block.find("layerId")
    fg = block[p:] if p != -1 else block
    spans = []
    for m in re.finditer(r"\{\s*closed = 1;", fg):
        d, j = 0, m.start()
        while j < len(fg):
            if fg[j] == "{":
                d += 1
            elif fg[j] == "}":
                d -= 1
                if d == 0:
                    break
            j += 1
        end = j + 1
        if fg[end:end + 1] == ",":
            end += 1
        n = parse_nodes(fg[m.start():j + 1])
        if n:
            spans.append((m.start(), end, n))
    return p, spans


def named_masters(pkg):
    """{layer_id: (weight, master_name)} for the three weight masters."""
    f = GSFont(pkg)
    out = {}
    for m in f.masters:
        word = m.name.split()[0]
        if word in WEIGHT_OF:
            out[m.id] = (WEIGHT_OF[word], word)
    return out


def is_master(lid, named):
    return lid in named or bool(re.fullmatch(r"m\d+", lid))


# ------------------------------------------------------------- geist source

_cache = {}


def geist_paths(which, master_name):
    """[[ (x, y, type), ... ], ...] for Geist's R at the named master."""
    key = (which, master_name)
    if key in _cache:
        return _cache[key]
    f = GSFont(GEIST_PKG[which])
    g = f.glyphs["R"]
    for l in g.layers:
        if l.name and l.name.split()[0] == master_name and l.layerId != "9EE13298":
            paths = []
            for s in l.shapes:
                paths.append([(n.position.x, n.position.y,
                                SUFFIX.get(n.type, "l") + ("s" if n.smooth else ""))
                               for n in s.nodes])
            _cache[key] = paths
            return paths
    raise SystemExit("Geist %s R: no layer named %s" % (which, master_name))


def render(paths):
    parts = []
    for p in paths:
        body = ",\n".join("(%d,%d,%s)" % (x, y, k) for x, y, k in p)
        parts.append("{\nclosed = 1;\nnodes = (\n%s\n);\n}" % body)
    return ",\n".join(parts)


# ------------------------------------------------------------------ kerning

def adjust_kerning(path, deltas):
    text = open(path, encoding="utf-8").read()
    changed = 0
    for uuid, delta in deltas.items():
        if not delta:
            continue
        um = re.search(r'"%s" = \{' % re.escape(uuid), text)
        if not um:
            continue
        depth, i = 0, um.end() - 1
        while i < len(text):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        master = text[um.end():i]
        for lm in reversed(list(re.finditer(r'"@MMK_L_R" = \{', master))):
            depth, j = 0, lm.end() - 1
            while j < len(master):
                if master[j] == "{":
                    depth += 1
                elif master[j] == "}":
                    depth -= 1
                    if depth == 0:
                        break
                j += 1
            block = master[lm.end():j]

            def sub(m):
                nonlocal changed
                changed += 1
                return "%s = %d;" % (m.group(1), int(m.group(2)) - delta)

            master = master[:lm.end()] + re.sub(r'("[^"]+") = (-?\d+);', sub, block) + master[j:]
        text = text[:um.end()] + master + text[i:]
    if changed:
        open(path, "w", encoding="utf-8").write(text)
    return changed


# --------------------------------------------------------------------- main

def main(argv):
    dry = "--check" in argv
    pkgs = [a for a in argv[1:] if not a.startswith("--")] or sorted(
        os.path.join("src", d) for d in os.listdir("src")
        if d.endswith(".glyphspackage"))

    for pkg in pkgs:
        which = "Roman" if pkg.endswith("Roman.glyphspackage") else "Italic"
        if not os.path.isdir(GEIST_PKG[which]):
            print("MISSING Geist sources: %s" % GEIST_PKG[which], file=sys.stderr)
            print("This script needs a checkout of https://github.com/vercel/geist-font",
                  file=sys.stderr)
            print("(sources/Geist.glyphspackage and sources/Geist-Italic.glyphspackage)",
                  file=sys.stderr)
            print("It cannot reconstruct the outline from a compiled binary: doing so",
                  file=sys.stderr)
            print("means inventing Glyphs node types, which distorts the curves.",
                  file=sys.stderr)
            return 1
        glyph = os.path.join(pkg, "glyphs", "R_.glyph")
        text = open(glyph, encoding="utf-8").read()
        named = named_masters(pkg)
        print("=" * 72)
        print("%s  <-  %s%s" % (pkg, GEIST_PKG[which], "   (--check)" if dry else ""))

        layers = list(find_layers(text))
        metrics = {}
        for lid, s, e in layers:
            if not is_master(lid, named):
                continue
            blk = text[s:e]
            _, spans = foreground(blk)
            if not spans:
                continue
            every = [n for sp in spans for n in sp[2]]
            adv = re.search(r"width = (\d+);", blk)
            base = sorted(n[0] for n in every if n[1] == 0)
            metrics[lid] = {
                "cap": max(n[1] for n in every),
                "lsb": min(n[0] for n in every),
                "adv": int(adv.group(1)) if adv else 0,
                "rsb": (int(adv.group(1)) if adv else 0) - max(n[0] for n in every),
                "stem": base[1] - base[0] if len(base) >= 2 else 0,
                "uuid": lid if lid in named else None,
                "w": named[lid][0] if lid in named else None,
            }
        ref = {k: v for k, v in metrics.items() if v["uuid"]}
        if len({v["w"] for v in ref.values()}) != 3:
            print("  could not resolve the three weights: %s" % ref)
            return 1
        by_stem = sorted(ref.items(), key=lambda kv: kv[1]["stem"])
        print("  masters %s" % {k[:8]: v["w"] for k, v in ref.items()})

        edits, kern = [], {}
        for lid, s, e in layers:
            if not is_master(lid, named):
                continue
            blk = text[s:e]
            off, spans = foreground(blk)
            if not spans:
                continue
            m = metrics[lid]
            # Carry the master's own name, not just its weight: Geist names
            # the roman middle master "Regular" and the italic one "Italic",
            # and looking the label up by weight picks the wrong one.
            if m["uuid"]:
                wlabel = named[lid][1]
            else:
                near = min(by_stem, key=lambda kv: abs(kv[1]["stem"] - m["stem"]))[0]
                wlabel = named[near][1]

            paths = geist_paths(which, wlabel)
            gcap = max(y for p in paths for _, y, _ in p)
            gminx = min(x for p in paths for x, _, _ in p)
            gmaxx = max(x for p in paths for x, _, _ in p)
            scale = m["cap"] / gcap
            dx = m["lsb"] - round(gminx * scale)
            new = [[(int(round(x * scale)) + dx, int(round(y * scale)), k)
                    for x, y, k in p] for p in paths]
            ink = round((gmaxx - gminx) * scale)
            adv = m["lsb"] + ink + m["rsb"]
            delta = adv - m["adv"]
            newcap = max(y for p in new for _, y, _ in p)
            print("  %-12s %-8s scale=%.4f cap %d->%d adv %d->%d (%+d) lsb->%d"
                  % (lid[:12], wlabel, scale, m["cap"], newcap, m["adv"], adv,
                     delta, min(x for p in new for x, _, _ in p)))
            edits.append((s + off + spans[0][0], s + off + spans[-1][1], render(new)))
            wm = re.search(r"width = \d+;", blk)
            if wm:
                edits.append((s + wm.start(), s + wm.end(), "width = %d;" % adv))
            if delta and m["uuid"]:
                kern.setdefault(m["uuid"], delta)

        for a, b, rep in sorted(edits, reverse=True):
            text = text[:a] + rep + text[b:]
        if not dry:
            open(glyph, "w", encoding="utf-8").write(text)
            n = adjust_kerning(os.path.join(pkg, "fontinfo.plist"), kern)
            print("  wrote %d edits, adjusted %d kerning values" % (len(edits), n))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))