#!/usr/bin/env python3
"""Make the spurred capital G the default and the spurless G the cv10 alternate.

Inter stores two capital G shapes:

  G    spurless  -- one contour
  G.1  spurred   -- two contours (a redrawn bowl plus the spur)

and cv10 switches between them with `sub G by G.1;`.

This script makes the spurred shape the default by exchanging the geometry of
those two glyphs, so afterwards:

  G    spurred   -- what you get with no features applied
  G.1  spurless  -- what cv10 now substitutes in, i.e. cv10 turns the spur OFF

Only these two glyphs need editing. Every other G glyph (Gbar, Gacute, Gcaron,
...) is a pure composite that references either G or G.1 plus a mark, so it
follows automatically. That includes the ss05/ss06 alternates: G.circled and
G.squared reference G and become spurred, G.1.squared references G.1 and
becomes spurless.

The cv10 feature file is deliberately NOT edited: `sub G by G.1;` already means
"swap to the other G", and after the swap the other G is the spurless one.

Only the layers that both glyphs share are exchanged. Those are the design
masters that actually compile; each glyph also carries a few extra layers that
belong to no shipped font, and those are left untouched rather than guessed at.

Usage: python misc/tools/swap-g-spur.py [--check] [src/*.glyphspackage ...]
"""
import os
import re
import sys

BASE = "G"
ALT = "G.1"
FILES = {"G": "G_.glyph", "G.1": "G_.1.glyph"}


def find_layer_blocks(text):
    """Return (start, end) offsets of each top-level layer block in `layers = (...)`."""
    m = re.search(r"layers = \(", text)
    if not m:
        raise ValueError("no layers = ( ... ) found")
    i = m.end()
    blocks = []
    depth = 0
    start = None
    while i < len(text):
        c = text[i]
        if c == "{":
            if depth == 0:
                start = i
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0 and start is not None:
                blocks.append((start, i + 1))
                start = None
        elif c == ")" and depth == 0:
            break
        i += 1
    return blocks


def layer_id(block):
    m = re.search(r"layerId = ([^;]+);", block)
    return m.group(1).strip() if m else None


def split_body(block):
    """Return (everything_before_layerId, layerId_stmt, everything_after)."""
    m = re.search(r"layerId = ([^;]+);", block)
    if not m:
        return block, "", ""
    return block[: m.start()], m.group(0), block[m.end():]


def read_glyph(path):
    with open(path, encoding="utf-8") as fp:
        text = fp.read()
    blocks = find_layer_blocks(text)
    layers = {}
    for s, e in blocks:
        lid = layer_id(text[s:e])
        if lid:
            layers[lid] = text[s:e]
    return text, layers


def swap_file(base_path, alt_path, dry_run):
    base_text, base_layers = read_glyph(base_path)
    alt_text, alt_layers = read_glyph(alt_path)

    shared = [l for l in base_layers if l in alt_layers]
    only_base = [l for l in base_layers if l not in alt_layers]
    only_alt = [l for l in alt_layers if l not in base_layers]

    print("  %s / %s: %d shared layers, %d base-only, %d alt-only"
          % (os.path.basename(base_path), os.path.basename(alt_path),
             len(shared), len(only_base), len(only_alt)))
    for l in only_base:
        print("      base-only layer (left alone): %s" % l[:40])
    for l in only_alt:
        print("      alt-only  layer (left alone): %s" % l[:40])
    if not shared:
        print("      !! no shared layers, refusing to touch")
        return 1

    def rebuild(text, layers, replacements):
        """Re-emit `text` with each layer block replaced by its new body."""
        blocks = find_layer_blocks(text)
        out = []
        pos = 0
        for s, e in blocks:
            lid = layer_id(text[s:e])
            out.append(text[pos:s])
            out.append(replacements[lid] if lid in replacements else text[s:e])
            pos = e
        out.append(text[pos:])
        return "".join(out)

    new_base = {}
    new_alt = {}
    for lid in shared:
        b_pre, b_id, b_post = split_body(base_layers[lid])
        a_pre, a_id, a_post = split_body(alt_layers[lid])
        # Each file keeps its own layerId statement; only the shape/anchor/width
        # payload is exchanged.
        new_base[lid] = a_pre + b_id + a_post
        new_alt[lid] = b_pre + a_id + b_post

    if dry_run:
        print("      would exchange %d layer payloads" % len(shared))
        return 0

    with open(base_path, "w", encoding="utf-8") as fp:
        fp.write(rebuild(base_text, base_layers, new_base))
    with open(alt_path, "w", encoding="utf-8") as fp:
        fp.write(rebuild(alt_text, alt_layers, new_alt))
    print("      exchanged %d layer payloads" % len(shared))
    return 0


def main(argv):
    dry = "--check" in argv
    pkgs = [a for a in argv[1:] if not a.startswith("--")] or sorted(
        os.path.join("src", d) for d in os.listdir("src")
        if d.endswith(".glyphspackage"))
    rc = 0
    for pkg in pkgs:
        print("=" * 70)
        print(pkg + ("   (--check, nothing written)" if dry else ""))
        gdir = os.path.join(pkg, "glyphs")
        base_path = os.path.join(gdir, FILES[BASE])
        alt_path = os.path.join(gdir, FILES[ALT])
        for p in (base_path, alt_path):
            if not os.path.exists(p):
                print("  MISSING %s" % p)
                rc = 1
        if rc:
            continue
        rc |= swap_file(base_path, alt_path, dry)
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))