#!/usr/bin/env bash
#
# One clean build of Neue Comet, with verification afterwards.
#
# `make all` covers both variable flavours, the 36 statics, the hinted TTFs,
# the .ttc and the web output. The build artefacts are removed first because
# a previous interrupted run leaves a partial build/fonts that make will
# otherwise treat as up to date.
#
# Nothing here publishes anything. It builds, checks, and reports.
#
# Usage:
#   ./build.sh              build and verify
#   ./build.sh -j4          limit parallelism (memory-bound: ufo2ft is hungry)
#   ./build.sh --no-verify  build only
set -uo pipefail

cd "$(dirname "$0")" || exit 1

JOBS="$(nproc 2>/dev/null || echo 4)"
VERIFY=1
for arg in "$@"; do
  case "$arg" in
    -j*) JOBS="${arg#-j}" ;;
    --no-verify) VERIFY=0 ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

say() { printf '\n\033[1m== %s\033[0m\n' "$1"; }
fail=0

say "build (make clean && make -j${JOBS} all)"
make clean >/dev/null 2>&1
if make -j"$JOBS" all 2>&1 | tee /tmp/neue-build.log; then
  echo "build ok"
else
  echo "BUILD FAILED - see /tmp/neue-build.log" >&2
  exit 1
fi

[ "$VERIFY" = 1 ] || exit 0

PY=.venv/bin/python

say "what got built"
printf '  statics        %s\n' "$(ls build/fonts/static/*.ttf 2>/dev/null | wc -l)"
printf '  hinted         %s\n' "$(ls build/fonts/static-hinted/*.ttf 2>/dev/null | wc -l)"
printf '  variable       %s\n' "$(ls build/fonts/var/*.ttf build/fonts/var/*.otf 2>/dev/null | wc -l)"

# --------------------------------------------------------------- R check --
# The capital R came from Geist. Confirm the compiled variable font still has
# that shape: the vertical leg means two contours, and the cap must land on the
# same line as the rest of the alphabet.
say "capital R"
"$PY" - <<'PY'
import sys
from fontTools.ttLib import TTFont
from fontTools.pens.boundsPen import BoundsPen

f = TTFont("build/fonts/var/NeueCometVariable.ttf")
gs = f.getGlyphSet()
fail = 0

def bounds(g):
    bp = BoundsPen(gs); gs[g].draw(bp)
    x0, y0, x1, y1 = bp.bounds
    return x0, y0, x1, y1

rx0, ry0, rx1, ry1 = bounds("R")
hx0, hy0, hx1, hy1 = bounds("H")
print("  R  x %d..%d  y %d..%d" % (rx0, rx1, ry0, ry1))
print("  H  x %d..%d  y %d..%d" % (hx0, hx1, hy0, hy1))
if ry1 != hy1:
    print("  FAIL: R cap %d != H cap %d" % (ry1, hy1)); fail = 1
else:
    print("  ok: cap height matches the alphabet")

n = f["glyf"]["R"].numberOfContours
print("  R contours: %d" % n)
if n != 2:
    print("  FAIL: expected 2 (outer + counter)"); fail = 1
else:
    print("  ok: outer + counter")

if rx0 != 180:
    print("  note: R lsb is %d, other capitals use 180" % rx0)
sys.exit(fail)
PY
[ $? -eq 0 ] || fail=1

# ------------------------------------------------- transformed components --
# Roman draws 'd' as a mirrored 'b'; the decompose filter must strip those,
# or fontbakery's transformed_components check fails again.
say "transformed components"
if "$PY" - <<'PY'
import sys
from fontTools.ttLib import TTFont
import glob
bad = 0
for p in sorted(glob.glob("build/fonts/var/*.ttf")) + \
         sorted(glob.glob("build/fonts/static/*.ttf")):
    f = TTFont(p)
    if "glyf" not in f:
        continue
    n = sum(1 for gn in f.getGlyphOrder() if f["glyf"][gn].isComposite()
            for c in f["glyf"][gn].components
            if c.getComponentInfo()[1][0] * c.getComponentInfo()[1][3] < 0)
    if n:
        print("  %-40s flipped=%d" % (p.split("/")[-1], n))
        bad += n
print("  total flipped components: %d" % bad)
sys.exit(1 if bad else 0)
PY
then echo "  ok: none"
else echo "  FAIL"; fail=1; fi

# ------------------------------------------------------------- fontbakery --
# Each report is built as its own target rather than via `make test`.
# `make test` runs test_var first, and fontbakery exits non-zero on the
# babelfont ERRORs even when the font is clean -- which aborts the run before
# test_static ever executes. The static reports then survive from an earlier
# build and look authoritative while being stale. Building them separately,
# after deleting any old ones, is the only way to actually check them.
say "fontbakery"
rm -f build/fontbakery-report-var.txt \
      build/fontbakery-report-text.txt \
      build/fontbakery-report-display.txt
for t in build/fontbakery-report-var.txt \
         build/fontbakery-report-text.txt \
         build/fontbakery-report-display.txt; do
  make "$t" > "/tmp/neue-$(basename "$t").log" 2>&1 || true
done

REPORTS=0
for r in build/fontbakery-report-*.txt; do
  [ -e "$r" ] || continue
  REPORTS=$((REPORTS + 1))
  # Count "Result: FAIL" lines, not the "FAIL: 0" summary line -- the summary
  # matches ^\s+FAIL: and made a clean report look like a failure.
  nf=$(grep -c 'Result: FAIL' "$r")
  ne=$(grep -c 'Result: ERROR' "$r")
  nw=$(grep -c 'Result: WARN' "$r")
  np=$(grep -c 'Result: PASS' "$r")
  printf '  %-38s FAIL:%s ERROR:%s WARN:%s PASS:%s\n' \
    "$(basename "$r")" "$nf" "$ne" "$nw" "$np"
  if [ "$nf" -gt 0 ]; then
    echo "     failing checks:"
    # Attribute a FAIL to its check. A fixed -B window is not enough: the
    # blocks run together, so looking back N lines reaches into the previous
    # check's ERROR section and reports the wrong name. Walk forward from each
    # ">> Check:" instead and pair it with the next Result: line.
    awk '
      /^>> Check:/   { check = $0 }
      /Result: FAIL/ { print check; check = "" }
    ' "$r" | sort -u | sed 's/^/       /'
    fail=1
  fi
  # These are babelfont tripping over py3.8 typing; fontbakery itself is
  # broken there, not the font. Surfaced rather than hidden, because a new
  # kind of internal error would mean a different problem.
  unknown=$(grep -oE "Failed with [A-Za-z]+Error" "$r" | sort -u | tr '\n' ' ')
  if [ -n "$unknown" ]; then
    echo "     fontbakery internal (not the font):$unknown"
  fi
done
[ "$REPORTS" = 3 ] || { echo "  FAIL: expected 3 reports, got $REPORTS"; fail=1; }

# ------------------------------------------------------------------ audit --
say "audit"
if "$PY" misc/tools/audit-fonts.py 2>&1 | tail -3; then :; else fail=1; fi

# --------------------------------------------------------- served fonts --
# docs/font-files is what the site actually serves. It was refreshed by hand
# for a long time and drifted: the CFF2 pair went missing and the statics went
# stale while the build looked fine.
say "docs/font-files"
if "$PY" - <<'PY'
import glob, hashlib, os, sys
def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()
bad = []
n = 0
for served in sorted(glob.glob("docs/font-files/*.woff2")):
    b = os.path.basename(served)
    src = None
    for cand in ("build/fonts/static-hinted/" + b, "build/fonts/var/" + b):
        if os.path.exists(cand):
            src = cand
            break
    if not src:
        bad.append("%s has no built counterpart" % b)
        continue
    n += 1
    if md5(served) != md5(src):
        bad.append("%s is stale" % b)
want = len(glob.glob("build/fonts/static-hinted/*.woff2")) + \
       len(glob.glob("build/fonts/var/*.woff2"))
print("  %d served files, %d expected" % (n, want))
for b in bad:
    print("  %s" % b)
if len(bad):
    print("  -> run: make docs_fonts_clean")
    sys.exit(1)
PY
then echo "  ok: served fonts match the build"
else echo "  FAIL: run 'make docs_fonts_clean'"; fail=1; fi

# ------------------------------------------------------------------ docs --
if [ -d docs ]; then
  say "docs build"
  # jekyll installed via `gem install` is not on a login PATH here
  JEKYLL="$(command -v jekyll || true)"
  if [ -z "$JEKYLL" ]; then
    for c in "$HOME"/.local/share/gem/ruby/*/bin/jekyll /usr/local/bin/jekyll; do
      [ -x "$c" ] && JEKYLL="$c" && break
    done
  fi
  if [ -n "$JEKYLL" ]; then
    if "$JEKYLL" build -s docs -d /tmp/neue-site --quiet 2>&1 | tail -3; then
      echo "  ok"
    else
      echo "  FAIL: jekyll build"; fail=1
    fi
  else
    echo "  jekyll not found - skipped"
  fi
fi

say "result"
if [ "$fail" = 0 ]; then
  echo "all checks passed"
else
  echo "SOMETHING FAILED - see above"
fi
exit "$fail"