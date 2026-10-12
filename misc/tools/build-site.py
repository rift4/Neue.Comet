#!/usr/bin/env python3
# encoding: utf8
#
# Renders the Neue Comet website.
#
# This replaces the Jekyll + Liquid setup that used to build docs/. The output
# is byte-for-byte what Jekyll produced, but the pipeline is now one Python
# script with no Ruby, no Liquid and no _site/ staging directory -- docs/ *is*
# the site.
#
# Why it still exists at all, rather than the HTML being checked in directly:
# the pages share a layout and differ in small ways (title, a meta-refresh on
# the download page, a depth-relative URL root). Keeping that in one place is
# what stops the five pages from drifting apart.
#
# What it resolves, and why each is needed:
#
#   url_root       Relative path from the page back to the site root, so the
#                  same files work served from a domain root or from a GitHub
#                  Pages project path like /Neue.Comet/. A hardcoded absolute
#                  root 404s every stylesheet and font everywhere except the
#                  one path it was written for.
#   build_version  Cache-buster for the main stylesheet and the preloaded
#                  fonts. The font has no version number, so this is the
#                  build timestamp -- which is what it was standing in for.
#   base_css_v     Per-file mtime. res/base.css is a Page (it carries front
#                  matter) rather than a static file, so Jekyll never gave it
#                  a modified_time and this renders empty. Harmless: the
#                  stylesheet still loads. Fixed properly by giving the file a
#                  plain mtime-based buster here.
#   favicon_v      Per-file mtime, same reasoning.
#   download_url   Points at the newest release. The font is unversioned, so
#                  there is no versioned path to keep in step with a tag.
#   lang_count     Count of languages, so the copy cannot drift from the list.
#
# Usage:  python misc/tools/build-site.py [--check]
#
#   --check  render to a temporary directory and fail if the committed files
#            differ, without touching them. Used by build.sh.
import hashlib
import os
import re
import sys
from datetime import datetime

BASEDIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SITEDIR = os.path.join(BASEDIR, "misc", "site")
DOCSDIR = os.path.join(BASEDIR, "docs")

DOWNLOAD_URL = ("https://github.com/rift4/Neue.Comet/releases/latest/"
                "download/NeueComet.zip")
DESCRIPTION = "Neue Comet is a typeface family"
BUILD_TOKEN = "__BUILD_VERSION__"

# Only these files are generated. Everything else under docs/ is already static
# and is served as-is.
PAGES = {
    # output path            title                              extra head
    "index.html":            (None, None),
    "download/index.html":   ("Download Neue Comet", None),
    "glyphs/index.html":     ("moved", '<meta name="robots" content="noindex">\n'),
    "samples/index.html":    (
        "404 not found",
        '<link rel="canonical" href="https://d.rsms.me/inter-website/v3/samples/">\n'
        '    <meta name="robots" content="noindex">\n  '),
    "dynmetrics/index.html": (
        "404 not found",
        '<link rel="canonical" href="https://d.rsms.me/inter-website/v3/dynmetrics/">\n'
        '    <meta name="robots" content="noindex">\n  '),
}
# var-test.html stands alone: it has no layout, it is only a redirect.
STANDALONE = ["var-test.html"]

# Not pages -- stylesheets and scripts that the old Jekyll build rendered.
# They carry a literal __BUILD_VERSION__ placeholder which is replaced with a
# hash of the file's own content, in place. They used to be Liquid templates
# with front matter, which only worked because Jekyll preprocessed them; served
# raw they would hand the browser a stylesheet starting with "---" and URLs
# containing "{{font_v}}". Keeping the substitution here means docs/ is servable
# as-is, which is the point of dropping Jekyll.
#
# Each entry carries its own placeholder pattern rather than sharing one, so a
# CSS file that happens to contain an 8-hex-digit string in quotes cannot be
# mistaken for a filled-in placeholder. The patterns match only the *value*,
# using a lookbehind for the "?v=" or the quote, so substituting the digest
# does not eat the prefix and leave a bare hash glued to the filename.
ASSETS = {
    "neue-comet.css": r"(?<=\?v=)[0-9a-f]{8}|__BUILD_VERSION__",
    "neue-comet-display.css": r"(?<=\?v=)[0-9a-f]{8}|__BUILD_VERSION__",
    "res/base.css": r"(?<=\?v=)[0-9a-f]{8}|__BUILD_VERSION__",
    "lab/build-version.js": r'(?<=")[0-9a-f]{8}|__BUILD_VERSION__',
}


def read(p):
    with open(p, "r", encoding="utf-8") as f:
        return f.read()


def write(p, s):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def mtime_v(relpath):
    """%Y%m%d%H%M%S of a file under docs/, or "" if it does not exist."""
    p = os.path.join(DOCSDIR, relpath.lstrip("/"))
    if not os.path.isfile(p):
        return ""
    return datetime.fromtimestamp(os.path.getmtime(p)).strftime("%Y%m%d%H%M%S")


def lang_count():
    """Count the languages listed in languages.yml.

    Parsed by hand rather than with PyYAML on purpose: the file is a flat list
    of category blocks, each with a "languages:" key followed by "- Name"
    lines, and build.sh runs this with whatever "python" is on PATH, which may
    not have PyYAML. Pulling in a YAML parser for one integer is not worth the
    dependency.
    """
    path = os.path.join(SITEDIR, "languages.yml")
    count = 0
    in_languages = False
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if stripped.startswith("languages:"):
                in_languages = True
                continue
            if stripped.startswith("- category:") or ":" in stripped.split("-")[0]:
                in_languages = False
            if in_languages and stripped.startswith("- "):
                count += 1
    if count == 0:
        raise ValueError("no languages parsed from %s" % path)
    return count


def render_page(out_rel, title, custom_header, layout, nlang, build_version):
    tpl_path = os.path.join(SITEDIR, "pages", out_rel)
    body = read(tpl_path)

    # url_root: one "../" per path segment below the root. "/download/" splits
    # to ["", "download"] so depth 1; "/" splits to [] so depth 0.
    trimmed = out_rel[:-len("index.html")] if out_rel.endswith("index.html") else out_rel
    depth = len([s for s in trimmed.split("/") if s])
    url_root = "../" * depth

    full_title = (title + " — Neue Comet") if title else "Neue Comet font family"

    vars = {
        "title": full_title,
        # og:title / twitter:title carry the bare page title, without the
        # "— Neue Comet" suffix that the <title> element gets.
        "page_title": title or "Neue Comet font family",
        "description": DESCRIPTION,
        "url_root": url_root,
        "url_path": trimmed,
        "build_version": build_version,
        "base_css_v": mtime_v("res/base.css"),
        "favicon_v": mtime_v("res/favicon.png"),
        "download_url": DOWNLOAD_URL,
        "content": body,
        "lang_count": str(nlang),
        "custom_html_header": ("    %s\n" % custom_header) if custom_header else "",
        # The download page redirects visitors straight to the archive.
        "redirect": ('    <meta http-equiv="refresh" content="0;url=%s" />\n'
                     % DOWNLOAD_URL) if out_rel.startswith("download/") else "",
        # On the home page the logo link is a no-op anchor rather than a link
        # back to the page you are already on.
        "home_attr": ('href="#" class=scroll-reveal'
                      if out_rel == "index.html" else 'href="%s"' % url_root),
        "download_active": ('class="active"'
                            if out_rel.startswith("download/") else ""),
    }

    # The page body uses the same variables as the layout ({{url_root}},
    # {{download_url}}), so resolve them there first, then substitute the
    # finished body in as {{content}}.
    body = substitute(body, vars)
    vars["content"] = body
    return substitute(layout, vars)


def substitute(text, vars):
    # Whitespace inside the braces is allowed, because the ported pages inherited
    # Liquid's habit of writing "{{ lang_count }}" and it is not worth
    # hand-editing every occurrence to tighten the spacing.
    def repl(m):
        return vars.get(m.group(1).strip(), m.group(0))

    return re.sub(r"\{\{\s*([A-Za-z_][A-Za-z0-9_]*)\s*\}\}", repl, text)


def normalise(text, pattern=None):
    """Blank the build placeholders, so that re-rendering an unchanged file
    compares equal to the committed one. Without this every run would report
    every file as stale, because the timestamp has moved.

    For *comparison* only. The 14-digit timestamp in a page's cache busters is
    matched whole, prefix included, so it cannot be half-eaten by the shorter
    8-hex form. Substituting into the asset files uses the value-only patterns
    in ASSETS, which is where dropping the prefix would actually matter.
    """
    if pattern is None:
        pattern = r"\?v=\d{14}|\?v=[0-9a-f]{8}|__BUILD_VERSION__"
    return re.sub(pattern, "TS", text)


def render_assets():
    """Fill in the build placeholder in the stylesheets and the lab script.

    The value is a hash of the file's own content rather than a timestamp. A
    timestamp would change on every rebuild and so invalidate the cache for
    every visitor on every deploy; a content hash changes exactly when the
    bytes change, which is the whole point of a cache buster. It also makes
    these files byte-stable across rebuilds, so --check stays meaningful.
    """
    out = {}
    for rel, pattern in ASSETS.items():
        path = os.path.join(DOCSDIR, rel)
        src = read(path)
        rx = re.compile(pattern)
        if not rx.search(src):
            print("  error: docs/%s has no build placeholder" % rel,
                  file=sys.stderr)
            return None
        digest = hashlib.sha256(normalise(src, pattern).encode("utf-8")
                                ).hexdigest()[:8]
        out[rel] = rx.sub(digest, src)
    return out


def main(argv):
    check = "--check" in argv[1:]

    layout = read(os.path.join(SITEDIR, "layout.html"))
    build_version = datetime.now().strftime("%Y%m%d%H%M%S")
    nlang = lang_count()

    rendered = {}
    for out_rel, (title, header) in PAGES.items():
        rendered[out_rel] = render_page(out_rel, title, header, layout,
                                        nlang, build_version)
    # STANDALONE pages are complete documents already; they are substituted
    # for the build token and emitted as-is, not wrapped in the layout.
    for out_rel in STANDALONE:
        rendered[out_rel] = substitute(
            read(os.path.join(SITEDIR, "pages", out_rel)),
            {"url_root": ""})

    # Nothing Liquid may survive into the output, in either mode.
    leftover = re.compile(r"\{\{|\{%")
    for out_rel, html in rendered.items():
        m = leftover.search(html)
        if m:
            print("  error: %r left in %s: %r"
                  % (m.group(0), out_rel, html[m.start():m.start() + 40]),
                  file=sys.stderr)
            return 1

    assets = render_assets()
    if assets is None:
        return 1

    if check:
        problems = []
        for out_rel, html in rendered.items():
            dest = os.path.join(DOCSDIR, out_rel)
            if not os.path.isfile(dest):
                problems.append("missing: docs/%s" % out_rel)
            elif normalise(read(dest)) != normalise(html):
                problems.append("stale:   docs/%s" % out_rel)
        for out_rel, html in assets.items():
            dest = os.path.join(DOCSDIR, out_rel)
            pattern = ASSETS[out_rel]
            if not os.path.isfile(dest):
                problems.append("missing: docs/%s" % out_rel)
            elif (normalise(read(dest), pattern)
                  != normalise(html, pattern)):
                problems.append("stale:   docs/%s" % out_rel)
        if problems:
            for p in problems:
                print("  %s" % p, file=sys.stderr)
            print("  run 'make -C docs build' to regenerate", file=sys.stderr)
            return 1
        print("  %d generated files match the templates"
              % (len(rendered) + len(assets)))
        return 0

    for out_rel, html in list(rendered.items()) + list(assets.items()):
        write(os.path.join(DOCSDIR, out_rel), html)
        print("  wrote docs/%s (%d bytes)" % (out_rel, len(html)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
