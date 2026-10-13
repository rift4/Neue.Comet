# Neue Comet

A variable grotesque for screens, descended from
[Inter](https://github.com/rsms/inter), with a vertical-legged capital R taken
from [Geist](https://github.com/vercel/geist-font).

New typefaces get new names. There is no version number — the most recent
release is always the current one.

**Get the files:** [releases/latest](https://github.com/rift4/Neue.Comet/releases/latest) ·
**Licence:** [SIL Open Font License 1.1](LICENSE.txt)

---

## What it is

- **2,987 glyphs** covering **2,852 codepoints** across Latin (core, Extended-A,
  Extended Additional), Greek and Cyrillic, plus a broad symbol set.
- **2048 units/em.** Cap height 1490, x-height 1118, ascender 1984, descender
  −494 — the tall x-height that reads well at UI sizes.
- **Two variable axes**, `wght` 100–900 and `opsz` 14–32.
- **Nine weights**, roman and italic, each in a text cut and a Display cut.

The Display cut is a second, separate set of masters, not a copy of the text
cut. It is spaced and drawn for large sizes, where a UI grotesque's tight
sidebearings and low contrast start to look thin and cramped.

### The variable axes

| Axis | Range | Default | What it does |
| --- | --- | --- | --- |
| `wght` | 100–900 | 400 | The nine weights. |
| `opsz` | 14–32 | 14 | Optical size. Interpolates the outlines — spacing, contrast and stroke weight — so the design tuned to stay legible at small text sizes opens up as the size grows. |

`opsz` is the whole point of shipping two cuts as one variable font rather than
two static families: the small-size masters and the display masters are the two
ends of a single axis, so an application can pick the right point on it without
loading two files.

```css
font-variation-settings: 'wght' 450, 'opsz' 22;
```

Applications with automatic optical sizing (`font-optical-sizing: auto`) drive
`opsz` for you from the computed font size. Otherwise set it explicitly.

### The weights

| Roman | Italic | `wght` |
| --- | --- | --- |
| Neue Comet Thin | Neue Comet Thin Italic | 100 |
| Neue Comet ExtraLight | Neue Comet ExtraLight Italic | 200 |
| Neue Comet Light | Neue Comet Light Italic | 300 |
| Neue Comet Regular | Neue Comet Italic | 400 |
| Neue Comet Medium | Neue Comet Medium Italic | 500 |
| Neue Comet SemiBold | Neue Comet SemiBold Italic | 600 |
| Neue Comet Bold | Neue Comet Bold Italic | 700 |
| Neue Comet ExtraBold | Neue Comet ExtraBold Italic | 800 |
| Neue Comet Black | Neue Comet Black Italic | 900 |

36 static instances in total: 9 weights × {roman, italic} × {text, Display}.

---

## Using it

### On the web — self-host

Copy `neue-comet.css` and the `font-files/` directory from this repo onto your
own server and link one stylesheet:

```html
<link rel="stylesheet" href="/fonts/neue-comet.css">
```

```css
body { font-family: 'Neue Comet', system-ui, sans-serif; }
```

One origin for the CSS and the WOFF2 files means no extra DNS lookup, no
third-party connection for a visitor's browser to block or fail, and it works
offline and behind a strict CSP.

There is no CDN build and no third-party font host. If you want one in front,
put one in front of *your* copy so the CSS and the font files still share an
origin — otherwise you get a second connection and a cross-origin fetch that
can fail independently of the stylesheet.

For the Display cut, link `neue-comet-display.css` and use the
`NeueCometDisplay` family name.

### On the desktop

| Format | File | For |
| --- | --- | --- |
| glyf | `NeueCometVariable.ttf` | the web, `@font-face`, any engine where variable-font support is uncertain |
| CFF2 | `NeueCometVariable.otf` | desktop installs — smaller file, better curve handling |
| hinted | `NeueComet.ttc` | a collection of all 36 statics, for applications that want discrete weights |

The CFF2 build is the one to install on a desktop. It is 36% smaller than the
glyf build (566 KB against 886 KB) and its outlines interpolate more cleanly.
The glyf build stays the default for the web, where broad support matters more
than size.

```sh
make install_var_otf   # the two CFF2 variable fonts
make install_ttf       # NeueComet.ttc, the hinted static collection
```

Note that `INSTALLDIR` in the `Makefile` is hardcoded to
`$(HOME)/Library/Fonts/NeueComet`, which is a macOS path. There is no platform
detection, so on Linux you want to override it:

```sh
make install_var_otf INSTALLDIR=~/.local/share/fonts/NeueComet
```

then run `fc-cache -f` if the system does not pick the fonts up on its own.

`NeueCometVariable-cff2.woff2` is also published if you want CFF2 on the web and
have confirmed your target browsers handle it.

### Not covered

No Bengali, Devanagari, Gurmukhi, Gujarati, Tamil, Thai, Arabic, Hebrew, CJK,
Hangul, or any other non-Latin/Greek/Cyrillic script. This is inherited from
the upstream design and is not a matter of adding a few glyphs.

**Set a fallback stack.** A missing glyph otherwise substitutes silently, which
is how a page ends up with a mix of two typefaces nobody chose:

```css
body {
  font-family: 'Neue Comet', 'Noto Sans Bengali', system-ui, sans-serif;
}
```

### OpenType features

43 GSUB features, 4 GPOS. The ones you are likely to reach for:

| Feature | Effect |
| --- | --- |
| `calt` | contextual alternates — punctuation adapts to its surroundings |
| `zero` | slashed zero, to distinguish `0` from `O` |
| `tnum` / `pnum` | tabular and proportional figures |
| `frac` / `numr` / `dnom` | fractions and their parts |
| `sups` / `subs` | super- and subscripts |
| `ss01`–`ss08` | stylistic sets |
| `cv01`–`cv16` | single-character variants |
| `case` | case-sensitive forms |
| `locl` | localised forms |

In GPOS: `kern` (pair kerning), `mark` and `mkmk` (mark positioning), and
`cpsp` (capital spacing).

`cv10` is worth knowing about: it *removes* the spur from the capital G. The
default G is spurred; `cv10` gives you the spurless form, which is what you
want in running text where the spur reads as a stray mark.

---

## Building from source

Everything is scripted. There is no manual step and no macOS-only tool in the
path — the sources are Glyphs packages, but they are compiled headlessly with
`fontmake`/`ufo2ft`, not opened in Glyphs.app.

```sh
./build.sh
```

One clean build with verification afterwards. It removes previous artefacts
first, builds everything, then checks: capital R geometry against the alphabet,
transformed components, `fontbakery check-universal` on three profiles, a
binary audit of every shipped file, that the site's `font-files/` match the
build, and that the site's pages still match their templates. It exits
non-zero if any check fails.

`ufo2ft` is memory-hungry — four parallel jobs can exhaust a small machine, and
the build dies with SIGTERM rather than an error. If that happens, lower the
count:

```sh
./build.sh -j2
```

Individual targets, if you want just one thing:

```sh
make var            # the glyf variable font
make var_otf        # the CFF2 variable font
make static         # the 36 static fonts
make web            # WOFF2 for the web
make all            # everything
```

### Building in a container

The toolchain is Python 3.8 plus a handful of system binaries, and the build is
self-contained enough to run in a container. `Containerfile` is that image;
`.devcontainer/` is the same thing wired up for a dev container.

```sh
misc/tools/podmanmake all      # build everything, in a container
misc/tools/podmanmake var      # just the variable font
misc/tools/podmanmake --shell  # a shell in the build environment
```

`podmanmake` is the Podman counterpart to `misc/tools/dockermake`, which is
hardcoded to Docker and points at a prebuilt upstream image. It builds the
local `Containerfile` on first use and caches it after that, then bind-mounts
the checkout, so artefacts land in `build/` on the host and no rebuild is
needed to see them. `--rebuild` forces a fresh image.

```sh
podman build -t neue-comet .
podman run --rm -it --userns=keep-id \
  -v "$PWD:/workspace:Z" -w /workspace neue-comet make all
```

Two things that are easy to get wrong when running this by hand:

- **`--userns=keep-id` is required under rootless Podman.** Without it the
  container's uid 1000 maps to a *subordinate* uid rather than to your host uid,
  so the non-root user cannot write the bind-mounted checkout and every target
  dies with `Permission denied` creating `build/`.
- **The Python version is the pinned one.** The image is `python:3.8-slim`,
  because `Pipfile` pins `python_version = "3.8"` and `pipenv` refuses to
  install that lock against anything else. The Debian release underneath is not
  pinned, and is free to move. Do not bump the tag to 3.9+ without updating
  `Pipfile` and `Pipfile.lock` together.

To build as a different uid — for a machine where your user is not 1000:

```sh
podman build --build-arg UID=1001 --build-arg GID=1001 -t neue-comet .
```

In VS Code or VSCodium, `Reopen in Container` builds the same `Containerfile`
and runs `make venv` once on create, so the extension host finds the
interpreter at `build/venv` without waiting for it on every start.

#### The venv stays out of the checkout

`build/` is bind-mounted, so compiled fonts land on the host — that is the
product, and it is meant to cross. `build/venv` deliberately does not: it is a
named volume mounted over that path, and the container builds its own.

That split is necessary because a venv is interpreter-specific. Absolute paths
to its base interpreter are baked into `pyvenv.cfg` and into the shebang of
every script it installs:

```text
# made on the host, run in the container
#!/home/zei/Projects/Neue.Comet/.venv/bin/python
cannot execute: required file not found
```

Because the volume shadows it, a host `build/venv` is invisible in the
container and a container venv never lands on the host. Both can coexist, and
each is built by the interpreter that will actually run it. `make venv` is a
no-op on the host when a valid venv is already there, so nothing is wasted.

```sh
misc/tools/podmanmake --fresh-venv var   # throw the volume away and rebuild
podman volume rm neue-comet-venv-py38    # or remove it directly
```

The volume name carries the Python version, because a venv made by 3.8 is not
reusable by 3.9. Bump it if the pin in `Pipfile` moves, or the stale volume
will be handed back silently.

### Checking a browser engine

`docs/vf-test.html` is a self-checking page. Open it in any browser and it
reports, per format, whether the font actually loaded rather than silently
falling back to a system default, whether `wght` and `opsz` interpolate, and
whether the glyf and CFF2 builds produce the same widths.

It runs 21 checks: four faces (glyf, CFF2, and the italic of each) each
checked for load, for actually applying rather than falling back, and for
`wght` and `opsz` interpolation — then five width comparisons between the
glyf and CFF2 roman builds. Note that the format-agreement comparison covers
the roman only; the italic pair is checked individually but not against each
other.

Reported passing on Chromium 153, Chrome 154 (Linux) and Firefox 155. Those
results are not recorded in this repository, and the reported count (22) is one
more than the 21 checks the page currently runs, so re-run it yourself rather
than taking the number on trust. Safari and Windows were also run by hand and
reported passing.

### Releasing

```sh
make zip_release
```

Produces `build/release/NeueComet.zip` — the archive the website links to. The
site points at `/releases/latest/download/NeueComet.zip`, so the asset name has
to stay `NeueComet.zip`; a versioned filename would have to be edited in step
with every tag by hand, which is exactly what used to break the download link.

CI builds and publishes on a `v*-*` tag. Note that this repository is a fork,
and GitHub disables Actions on forks by default, so that job does not currently
run — releases are made from the tag by hand.

---

## Project layout

```
src/
  NeueComet-Roman.glyphspackage/    roman masters, the bulk of the work
  NeueComet-Italic.glyphspackage/   italic masters
build.sh                            one clean build, with verification
Makefile                            per-target build rules
Containerfile                       build environment, for Podman/Docker
.devcontainer/                      the same image, wired up for a dev container
misc/site/                          templates for the pages that share a layout
misc/tools/                         build and audit scripts
docs/                               the website, and the fonts it serves
```

`docs/` is a plain static site — no Jekyll, no Ruby. `docs/` itself is what gets
published; there is no build step at deploy time. Five of the pages share a
layout and differ in small ways (title, a redirect, how deep they sit in the
tree), so they are generated from `misc/site/` by
`misc/tools/build-site.py`; a sixth is a standalone redirect.

```sh
make -C docs build    # regenerate the pages
make -C docs check    # fail if they have drifted from the templates
make -C docs serve    # serve docs/ on http://127.0.0.1:3002
```

`make -C docs check` also runs as part of `./build.sh`, so a page edited by
hand instead of through the templates fails the build rather than silently
disagreeing with them.

`docs/lab/` is an interactive glyph inspector; `docs/vf-test.html` is the
browser check above. `docs/font-files/` is generated from `build/` by
`make docs_fonts` and is what the site serves — never edit it by hand.

---

## Credits and licence

Neue Comet is licensed under the
[SIL Open Font License 1.1](LICENSE.txt). You may use, modify and bundle it,
including commercially, but you may not sell the font files on their own, and a
modified version may not use a Reserved Font Name. Please ship derivatives under
your own name, not "Neue Comet".

The OS/2 vendor ID is `NONE`, which means unregistered. That is deliberate —
registering implies a foundry identity that does not exist yet.

**Inter** © 2016 The Inter Project Authors, by
[Rasmus Andersson](https://rsms.me/). Neue Comet is a derivative. Inter is a
trademark of Rasmus Andersson; that trademark is not claimed here.

**Geist** © 2024 The Geist Project Authors. The capital R is Geist's.

Both upstream projects are under the same OFL 1.1, which requires their notices
to travel with the font. They are reproduced in `LICENSE.txt` and carried in
the font metadata.

What changed here: the family name and identity, the capital R, the CFF2
build, and the tooling to check all of it. The glyph designs, script coverage,
variable model and OpenType feature set originate with Inter.

For the upstream design rationale, see the
[Inter README](https://github.com/rsms/inter#readme).
