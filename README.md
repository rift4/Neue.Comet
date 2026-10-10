# Neue Comet

Neue Comet is a variable typeface for screens: a tall x-height, a large character
set, and a wide weight range on two optical-size axes.

Version 4.2 · SIL Open Font License

[**Download the font files**](https://github.com/rift4/Neue.Comet/releases/latest)

## Quick questions

- **Where can I get it?** [Releases](https://github.com/rift4/Neue.Comet/releases/latest)
- **Can I use it commercially?** Yes — bundle it with whatever you like, but you
  may not sell the font itself. [Read the licence](LICENSE.txt).
- **Something looks wrong.** [Open an issue](https://github.com/rift4/Neue.Comet/issues/new?template=bug_report.md)
- **I have a question.** [Discussions Q&A](https://github.com/rift4/Neue.Comet/discussions/categories/q-a)

## Installing on the web

Self-host the stylesheet:

```html
<link rel="preconnect" href="https://your-font-file-host/">
<link rel="stylesheet" href="https://your-font-file-host/neue-comet.css">
```

```css
:root { font-family: 'Neue Comet', sans-serif; }
@supports (font-variation-settings: normal) {
  :root { font-family: 'Neue Comet var', sans-serif; }
}
```

Self-hosting is the recommended approach. Copy `neue-comet.css` and the
`font-files/` directory out of this repo into your own site:

```html
<link rel="stylesheet" href="/fonts/neue-comet.css">
```

Serving the CSS and the WOFF2 files from one origin means no extra DNS lookup,
no third-party connection to block, and it works offline and behind a firewall.

If you want a CDN in front, put one in front of *your own* copy — Cloudflare or
similar — rather than proxying a third-party host, so the CSS and fonts still
share an origin.

### Testing a browser engine

[`docs/vf-test.html`](docs/vf-test.html) is a self-checking page. Open it in
any browser and it reports, per format, whether the font loaded (rather than
silently falling back), whether `wght` and `opsz` interpolate, and whether the
glyf and CFF2 builds agree. It's how the CFF2 support claim below was checked,
and it's the quickest way to confirm a browser before shipping to it.

## Installing on the desktop

| Format | File | Use for |
| --- | --- | --- |
| glyf | `NeueCometVariable.ttf` | the web, `@font-face`, anywhere variable-font support is uncertain |
| CFF2 | `NeueCometVariable.otf` | desktop installs — smaller file, nicer curves |

The CFF2 build is verified in **Chromium** — both axes interpolate, and the
rendered output is indistinguishable from the glyf build at every weight and
optical size tested, roman and italic. It is **not yet verified in Firefox,
Safari, or on Windows**, where variable CFF2 has historically been weaker. So
**glyf stays the default for the web** until that testing is done.

`make install_var` installs the glyf version, `make install_var_otf` the CFF2 one.

`misc/tools/compare-vf-formats.py` rasterises both builds and compares them
pixel by pixel, which is how the equivalence above was established.

## What you get

**36 static fonts + 2 variable fonts**, in nine weights (Thin 100 → Black 900),
roman and italic, plus a Display cut tuned for large sizes.

| Roman | Italic | Weight |
| --- | --- | --- |
| Thin | Thin Italic | 100 |
| ExtraLight | ExtraLight Italic | 200 |
| Light | Light Italic | 300 |
| Regular | Italic | 400 |
| Medium | Medium Italic | 500 |
| SemiBold | SemiBold Italic | 600 |
| Bold | Bold Italic | 700 |
| ExtraBold | ExtraBold Italic | 800 |
| Black | Black Italic | 900 |

The variable font carries two axes:

| Axis | Range | Default |
| --- | --- | --- |
| `wght` | 100 – 900 | 400 |
| `opsz` | 14 – 32 | 14 |

`opsz` is the optical-size axis: it interpolates the outlines themselves, so
the cuts tuned to stay legible at small text sizes open up as the size grows.
Applications with automatic optical sizing (`font-optical-sizing: auto`) will
drive it for you; otherwise set it in `font-variation-settings`.

## Script coverage

2,852 encoded codepoints, 2,987 glyphs, 2048 units/em.

| Covered | |
| --- | --- |
| Latin | core, Extended-A, Extended Additional |
| Greek | and Greek Extended |
| Cyrillic | and Cyrillic Extended-A |
| Symbols | punctuation, super/subscripts, currency, arrows, math operators, geometric shapes, dingbats |

**Not covered:** Bengali/Bangla, Devanagari, Gurmukhi, Gujarati, Tamil, Thai,
Arabic, Hebrew, CJK, Hangul, or any other non-Latin/Greek/Cyrillic script.

If you need one of those, set a fallback stack — don't let the font silently
substitute. For example, for Bangla:

```css
body {
  font-family: 'Neue Comet', 'Noto Sans Bengali', system-ui, sans-serif;
}
```

This is a limitation inherited from the upstream design, not something that can
be patched by adding a few glyphs — see the note at the foot of this file.

## OpenType features

41 GSUB features and 4 GPOS features. The ones you'll actually reach for:

| Feature | What it does |
| --- | --- |
| `calt` | contextual alternates — punctuation adapts to its surroundings |
| `zero` | slashed zero, to tell `0` from `O` |
| `tnum` / `pnum` | tabular and proportional figures |
| `frac` / `dnom` / `numr` | fractions, denominators, numerators |
| `sups` / `subs` | super- and subscripts |
| `ss01` – `ss08` | stylistic sets |
| `cv01` – `cv16` | single character variants |
| `case` | case-sensitive forms |
| `locl` | localised forms |

Kerning (`kern`), mark positioning (`mark`/`mkmk`) and capital spacing
(`cpsp`) are in GPOS.

## Working on the source

The Glyphs sources live in `src/`. See [CONTRIBUTING.md](CONTRIBUTING.md) for
how to build.

```sh
make var          # the glyf variable font
make var_otf      # the CFF2 variable font
make all          # everything
make test         # fontbakery
```

There's also an interactive glyph lab in `docs/`:

```sh
make -j web && make -C docs serve
```

Two tools worth knowing about, both in `misc/tools/`:

- `audit-fonts.py` — checks every shipped binary for stale branding, PostScript
  name/filename agreement, vendor ID and style/weight consistency:

  ```sh
  python misc/tools/audit-fonts.py docs/font-files
  ```

- `normalize-static-names.py` — enforces the `NeueComet[-Display]-<Style>`
  PostScript naming convention on the static builds. It runs automatically as
  part of `make static`.

## Derivative fonts

Neue Comet is licensed under the **SIL Open Font License 1.1**. You may modify
it, bundle it and sell it as part of something else — you may not sell the font
files themselves, and derivatives must stay under the same licence. [Full terms.](LICENSE.txt)

Please don't ship derivative works under the name "Neue Comet". Use your own.

## Licence and credits

Neue Comet is licensed under the [SIL Open Font License 1.1](LICENSE.txt).

The OS/2 `achVendID` is currently `NONE`, meaning "unregistered". To set your
own, register a four-character vendor ID with Microsoft first, then update
`vendorID` in `src/NeueComet-Roman.glyphspackage/fontinfo.plist` and
`src/NeueComet-Italic.glyphspackage/fontinfo.plist`:

> Email <mstwsite@microsoft.com> with the vendor ID you want, the foundry name,
> an email address and a link to the foundry website. See
> [Register a font vendor ID](https://learn.microsoft.com/en-us/typography/vendors/register).

`fontbakery`'s `vendor_id` check warns while the value is unregistered or
doesn't match the manufacturer in name ID 8.

---

### Based on Inter

Neue Comet is derived from [Inter](https://github.com/rsms/inter) by
[Rasmus Andersson](https://rsms.me/), which is licensed under the
[SIL Open Font License 1.1](LICENSE.txt). The original copyright notice,
licence and design credit are retained in `LICENSE.txt` and in the font
metadata, as the licence requires.

"Inter" is a trademark of Rasmus Andersson (RSMS). Script coverage, the
two-axis variable model, the OpenType feature set and the underlying glyph
design all originate with Inter; the changes made here are the family rename,
the identity and licensing metadata, the CFF2 build, and the build tooling
updates that came with it.

This README describes Neue Comet only. For the upstream design rationale and
project history, see the [Inter README](https://github.com/rsms/inter#readme).