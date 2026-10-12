SRCDIR  := $(abspath $(lastword $(MAKEFILE_LIST))/../..)
FONTDIR := ../build/fonts
BIN     := $(SRCDIR)/build/venv/bin
VENV    := ../build/venv/bin/activate
Q = $(if $(filter 1,$(V) $(VERBOSE)),,@)  # make V=1 for verbose mode
export PATH := $(BIN):$(PATH)

HTTP_SERVER_BIND_ADDR ?= 127.0.0.1
HTTP_SERVER_PORT       ?= 3002

default:
	@echo "Please specify a target: build, serve, check" >&2

# The site is plain HTML now. There is no Ruby, no Liquid and no _site/
# staging directory: docs/ is the site, and these rules regenerate the few
# pages that share a layout. See misc/tools/build-site.py.
build:
	$(Q). $(VENV); python ../misc/tools/build-site.py

# Fail if the committed HTML has drifted from the templates, without
# rewriting it. Used by the root build.sh.
check:
	$(Q). $(VENV); python ../misc/tools/build-site.py --check

# A plain static server over docs/. There is no live-reload any more; re-run
# `make build` after editing a template and refresh.
serve: build
	@echo "Serving http://$(HTTP_SERVER_BIND_ADDR):$(HTTP_SERVER_PORT)/ from $(CURDIR)"
	@# The lab symlinks its font directory from the build tree, so the glyph
	@# inspector works without a separate web build.
	@rm -f lab/fonts && ln -s ../../../build/fonts lab/fonts
	$(Q)python -m http.server $(HTTP_SERVER_PORT) --bind $(HTTP_SERVER_BIND_ADDR)

serve-pub:
	exec $(MAKE) HTTP_SERVER_BIND_ADDR=0.0.0.0 serve

optimize-images:
	$(Q)for f $$(find . -type f -name \*.png); do \
		echo optipng "$$f"; \
		optipng -quiet "$$f" & \
	done ; \
	wait

# -----------------------------------------------------------------------

# Copy the built web fonts into the directory the site serves them from.
# The root Makefile has an equivalent `docs_fonts` target; this one is here so
# `make -C docs` is useful on its own.
fonts: font-files/NeueComet-Regular.woff2

FONTS_SRC := \
	$(FONTDIR)/static/NeueComet-Black.woff2 \
	$(FONTDIR)/static/NeueComet-BlackItalic.woff2 \
	$(FONTDIR)/static/NeueComet-Bold.woff2 \
	$(FONTDIR)/static/NeueComet-BoldItalic.woff2 \
	$(FONTDIR)/static/NeueComet-ExtraBold.woff2 \
	$(FONTDIR)/static/NeueComet-ExtraBoldItalic.woff2 \
	$(FONTDIR)/static/NeueComet-ExtraLight.woff2 \
	$(FONTDIR)/static/NeueComet-ExtraLightItalic.woff2 \
	$(FONTDIR)/static/NeueComet-Italic.woff2 \
	$(FONTDIR)/static/NeueComet-Light.woff2 \
	$(FONTDIR)/static/NeueComet-LightItalic.woff2 \
	$(FONTDIR)/static/NeueComet-Medium.woff2 \
	$(FONTDIR)/static/NeueComet-MediumItalic.woff2 \
	$(FONTDIR)/static/NeueComet-Regular.woff2 \
	$(FONTDIR)/static/NeueComet-SemiBold.woff2 \
	$(FONTDIR)/static/NeueComet-SemiBoldItalic.woff2 \
	$(FONTDIR)/static/NeueComet-Thin.woff2 \
	$(FONTDIR)/static/NeueComet-ThinItalic.woff2 \
	$(FONTDIR)/static/NeueCometDisplay-Black.woff2 \
	$(FONTDIR)/static/NeueCometDisplay-BlackItalic.woff2 \
	$(FONTDIR)/static/NeueCometDisplay-Bold.woff2 \
	$(FONTDIR)/static/NeueCometDisplay-BoldItalic.woff2 \
	$(FONTDIR)/static/NeueCometDisplay-ExtraBold.woff2 \
	$(FONTDIR)/static/NeueCometDisplay-ExtraBoldItalic.woff2 \
	$(FONTDIR)/static/NeueCometDisplay-ExtraLight.woff2 \
	$(FONTDIR)/static/NeueCometDisplay-ExtraLightItalic.woff2 \
	$(FONTDIR)/static/NeueCometDisplay-Italic.woff2 \
	$(FONTDIR)/static/NeueCometDisplay-Light.woff2 \
	$(FONTDIR)/static/NeueCometDisplay-LightItalic.woff2 \
	$(FONTDIR)/static/NeueCometDisplay-Medium.woff2 \
	$(FONTDIR)/static/NeueCometDisplay-MediumItalic.woff2 \
	$(FONTDIR)/static/NeueCometDisplay-Regular.woff2 \
	$(FONTDIR)/static/NeueCometDisplay-SemiBold.woff2 \
	$(FONTDIR)/static/NeueCometDisplay-SemiBoldItalic.woff2 \
	$(FONTDIR)/static/NeueCometDisplay-Thin.woff2 \
	$(FONTDIR)/static/NeueCometDisplay-ThinItalic.woff2 \
	$(FONTDIR)/var/NeueCometVariable.woff2 \
	$(FONTDIR)/var/NeueCometVariable-Italic.woff2 \
	$(FONTDIR)/var/NeueCometVariable.ttf

font-files/NeueComet-Regular.woff2: $(FONTS_SRC)
	rm -rf font-files/NeueComet*
	mkdir -p font-files
	cp -a $^ font-files/
	$(Q)touch $@

$(FONTS_SRC):
	@echo "Missing fonts in $(FONTDIR)" >&2
	@echo "Did you forget to 'make web' in the repository root?" >&2
	@exit 1

lab/glyphinfo.json: ../misc/tools/gen-glyphinfo.py ../misc/UnicodeData.txt
lab/glyphinfo.json: ../build/ufo/NeueComet-Regular.ufo
	. $(VENV); python ../misc/tools/gen-glyphinfo.py -ucd ../misc/UnicodeData.txt $< > $@
../build/ufo/NeueComet-Regular.ufo: $(wildcard ../build/ufo/NeueComet-Regular.ufo/*.plist)
	touch $@

.PHONY: default build check serve serve-pub fonts optimize-images
