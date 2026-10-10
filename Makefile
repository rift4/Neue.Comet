ifeq ($(findstring Darwin./Applications/,$(shell uname -s).$(MAKE)),Darwin./Applications/)
$(error Use "gmake" (not "make") on macos. Install with "brew install make")
endif

SRCDIR   := $(abspath $(lastword $(MAKEFILE_LIST))/..)
FONTDIR  := build/fonts
UFODIR   := build/ufo
VENVDIR  := $(SRCDIR)/build/venv
VERSION  := $(shell cat version.txt)
MAKEFILE := $(lastword $(MAKEFILE_LIST))

export PATH := $(VENVDIR)/bin:$(PATH)
export VIRTUAL_ENV := $(VENVDIR)

default: all

# arguments to fontmake
FM_ARGS :=
ifndef DEBUG
	FM_ARGS += --verbose WARNING
endif

# ---------------------------------------------------------------------------------
# intermediate sources

$(UFODIR)/%.glyphs: src/%.glyphspackage | $(UFODIR) venv
	glyphspkg -o $(dir $@) $^

# features
build/features_data: $(UFODIR)/features $(wildcard src/features/*)
	touch "$@"
$(UFODIR)/features:
	@mkdir -p $(UFODIR)
	@rm -f $(UFODIR)/features
	@ln -s ../../src/features $(UFODIR)/features

# designspace & master UFOs
$(UFODIR)/%.var.designspace: $(UFODIR)/%.designspace misc/tools/gen-var-designspace.py | venv
	python misc/tools/gen-var-designspace.py $< $@

$(UFODIR)/%.designspace: $(UFODIR)/%.glyphs $(UFODIR)/features misc/tools/postprocess-designspace.py | venv
	fontmake $(FM_ARGS) -o ufo -g $< --designspace-path $@ \
		  --master-dir $(UFODIR) --instance-dir $(UFODIR)
	python misc/tools/postprocess-designspace.py $@

# instance UFOs from designspace
$(UFODIR)/NeueComet%Italic.ufo: $(UFODIR)/NeueComet-Italic.designspace misc/tools/gen-instance-ufo.sh | venv
	bash misc/tools/gen-instance-ufo.sh $< $@
$(UFODIR)/NeueComet%.ufo: $(UFODIR)/NeueComet-Roman.designspace misc/tools/gen-instance-ufo.sh | venv
	bash misc/tools/gen-instance-ufo.sh $< $@

# designspace & master UFOs (for editing)
build/ufo-editable/%.designspace: $(UFODIR)/%.glyphs $(UFODIR)/features misc/tools/postprocess-designspace.py | venv
	@mkdir -p $(dir $@)
	fontmake $(FM_ARGS) -o ufo -g $< --designspace-path $@ \
		  --master-dir $(dir $@) --instance-dir $(dir $@)
	python misc/tools/postprocess-designspace.py --editable $@

# instance UFOs from designspace (for editing)
build/ufo-editable/NeueComet%Italic.ufo: build/ufo-editable/NeueComet-Italic.designspace misc/tools/gen-instance-ufo.sh | venv
	bash misc/tools/gen-instance-ufo.sh $< $@
build/ufo-editable/NeueComet%.ufo: build/ufo-editable/NeueComet-Roman.designspace misc/tools/gen-instance-ufo.sh | venv
	bash misc/tools/gen-instance-ufo.sh $< $@

editable-ufos: build/ufo-editable/.ok
	@echo "Editable designspace & UFOs can be found here:"
	@echo "  $(PWD)/build/ufo-editable"

build/ufo-editable/.ok: build/ufo-editable/NeueComet-Roman.designspace build/ufo-editable/NeueComet-Italic.designspace
	@rm -f build/ufo-editable/features
	@ln -s ../../src/features build/ufo-editable/features
	$(MAKE) \
		build/ufo-editable/NeueComet-Light.ufo \
		build/ufo-editable/NeueComet-ExtraLight.ufo \
		build/ufo-editable/NeueComet-Medium.ufo \
		build/ufo-editable/NeueComet-SemiBold.ufo \
		build/ufo-editable/NeueComet-Bold.ufo \
		build/ufo-editable/NeueComet-ExtraBold.ufo \
		\
		build/ufo-editable/NeueComet-LightItalic.ufo \
		build/ufo-editable/NeueComet-ExtraLightItalic.ufo \
		build/ufo-editable/NeueComet-MediumItalic.ufo \
		build/ufo-editable/NeueComet-SemiBoldItalic.ufo \
		build/ufo-editable/NeueComet-BoldItalic.ufo \
		build/ufo-editable/NeueComet-ExtraBoldItalic.ufo \
		\
		build/ufo-editable/NeueCometDisplay-Light.ufo \
		build/ufo-editable/NeueCometDisplay-ExtraLight.ufo \
		build/ufo-editable/NeueCometDisplay-Medium.ufo \
		build/ufo-editable/NeueCometDisplay-SemiBold.ufo \
		build/ufo-editable/NeueCometDisplay-Bold.ufo \
		build/ufo-editable/NeueCometDisplay-ExtraBold.ufo \
		\
		build/ufo-editable/NeueCometDisplay-LightItalic.ufo \
		build/ufo-editable/NeueCometDisplay-ExtraLightItalic.ufo \
		build/ufo-editable/NeueCometDisplay-MediumItalic.ufo \
		build/ufo-editable/NeueCometDisplay-SemiBoldItalic.ufo \
		build/ufo-editable/NeueCometDisplay-BoldItalic.ufo \
		build/ufo-editable/NeueCometDisplay-ExtraBoldItalic.ufo
	@touch $@
	@echo ""

# make sure intermediate files are not rm'd by make
.PRECIOUS: \
	$(UFODIR)/NeueComet-Black.ufo \
	$(UFODIR)/NeueComet-Regular.ufo \
	$(UFODIR)/NeueComet-Thin.ufo \
	$(UFODIR)/NeueComet-Light.ufo \
	$(UFODIR)/NeueComet-ExtraLight.ufo \
	$(UFODIR)/NeueComet-Medium.ufo \
	$(UFODIR)/NeueComet-SemiBold.ufo \
	$(UFODIR)/NeueComet-Bold.ufo \
	$(UFODIR)/NeueComet-ExtraBold.ufo \
	\
	$(UFODIR)/NeueComet-BlackItalic.ufo \
	$(UFODIR)/NeueComet-Italic.ufo \
	$(UFODIR)/NeueComet-ThinItalic.ufo \
	$(UFODIR)/NeueComet-LightItalic.ufo \
	$(UFODIR)/NeueComet-ExtraLightItalic.ufo \
	$(UFODIR)/NeueComet-MediumItalic.ufo \
	$(UFODIR)/NeueComet-SemiBoldItalic.ufo \
	$(UFODIR)/NeueComet-BoldItalic.ufo \
	$(UFODIR)/NeueComet-ExtraBoldItalic.ufo \
	\
	$(UFODIR)/NeueCometDisplay-Black.ufo \
	$(UFODIR)/NeueCometDisplay-Regular.ufo \
	$(UFODIR)/NeueCometDisplay-Thin.ufo \
	$(UFODIR)/NeueCometDisplay-Light.ufo \
	$(UFODIR)/NeueCometDisplay-ExtraLight.ufo \
	$(UFODIR)/NeueCometDisplay-Medium.ufo \
	$(UFODIR)/NeueCometDisplay-SemiBold.ufo \
	$(UFODIR)/NeueCometDisplay-Bold.ufo \
	$(UFODIR)/NeueCometDisplay-ExtraBold.ufo \
	\
	$(UFODIR)/NeueCometDisplay-BlackItalic.ufo \
	$(UFODIR)/NeueCometDisplay-Italic.ufo \
	$(UFODIR)/NeueCometDisplay-ThinItalic.ufo \
	$(UFODIR)/NeueCometDisplay-LightItalic.ufo \
	$(UFODIR)/NeueCometDisplay-ExtraLightItalic.ufo \
	$(UFODIR)/NeueCometDisplay-MediumItalic.ufo \
	$(UFODIR)/NeueCometDisplay-SemiBoldItalic.ufo \
	$(UFODIR)/NeueCometDisplay-BoldItalic.ufo \
	$(UFODIR)/NeueCometDisplay-ExtraBoldItalic.ufo \
	\
	$(UFODIR)/NeueComet-Roman.glyphs \
	$(UFODIR)/NeueComet-Italic.glyphs \
	$(UFODIR)/NeueComet-Roman.designspace \
	$(UFODIR)/NeueComet-Italic.designspace \
	$(UFODIR)/NeueComet-Roman.var.designspace \
	$(UFODIR)/NeueComet-Italic.var.designspace

# ---------------------------------------------------------------------------------
# products

# arguments to fontmake
FM_ARGS_2 := $(FM_ARGS) \
	--overlaps-backend pathops \
	--flatten-components \
	--no-autohint
ifndef DEBUG
	FM_ARGS_2 += --production-names
else
	FM_ARGS_2 += --no-production-names
endif


$(FONTDIR)/static/%.otf: $(UFODIR)/%.ufo build/features_data misc/tools/normalize-static-names.py | $(FONTDIR)/static venv
	fontmake -u $< -o otf --output-path $@.tmp.otf $(FM_ARGS_2)
	psautohint -o $@ $@.tmp.otf
	@rm $@.tmp.otf
	python misc/tools/normalize-static-names.py $@

$(FONTDIR)/static/%.ttf: $(UFODIR)/%.ufo build/features_data | $(FONTDIR)/static venv
	fontmake -u $< -o ttf --output-path $@ $(FM_ARGS_2)


AUTOHINT_ARGS := --stem-width-mode=qqq --no-info

$(FONTDIR)/static-hinted/NeueComet-Regular.ttf: $(FONTDIR)/static/NeueComet-Regular.ttf | $(FONTDIR)/static-hinted venv
	python -m ttfautohint $(AUTOHINT_ARGS) "$<" "$@"

$(FONTDIR)/static-hinted/NeueCometDisplay-Regular.ttf: $(FONTDIR)/static/NeueCometDisplay-Regular.ttf | $(FONTDIR)/static-hinted venv
	python -m ttfautohint $(AUTOHINT_ARGS) "$<" "$@"

$(FONTDIR)/static-hinted/NeueComet-Italic.ttf: $(FONTDIR)/static/NeueComet-Italic.ttf | $(FONTDIR)/static-hinted venv
	python -m ttfautohint $(AUTOHINT_ARGS) "$<" "$@"

$(FONTDIR)/static-hinted/NeueCometDisplay-Italic.ttf: $(FONTDIR)/static/NeueCometDisplay-Italic.ttf | $(FONTDIR)/static-hinted venv
	python -m ttfautohint $(AUTOHINT_ARGS) "$<" "$@"

$(FONTDIR)/static-hinted/NeueCometDisplay-%Italic.ttf: $(FONTDIR)/static/NeueCometDisplay-%Italic.ttf | $(FONTDIR)/static-hinted/NeueCometDisplay-Italic.ttf $(FONTDIR)/static-hinted venv
	python -m ttfautohint $(AUTOHINT_ARGS) \
	  --reference $(FONTDIR)/static-hinted/NeueCometDisplay-Italic.ttf "$<" "$@"

$(FONTDIR)/static-hinted/NeueCometDisplay-%.ttf: $(FONTDIR)/static/NeueCometDisplay-%.ttf | $(FONTDIR)/static-hinted/NeueCometDisplay-Regular.ttf $(FONTDIR)/static-hinted venv
	python -m ttfautohint $(AUTOHINT_ARGS) \
	  --reference $(FONTDIR)/static-hinted/NeueCometDisplay-Regular.ttf "$<" "$@"

$(FONTDIR)/static-hinted/NeueComet-%Italic.ttf: $(FONTDIR)/static/NeueComet-%Italic.ttf | $(FONTDIR)/static-hinted/NeueComet-Italic.ttf $(FONTDIR)/static-hinted venv
	python -m ttfautohint $(AUTOHINT_ARGS) \
	  --reference $(FONTDIR)/static-hinted/NeueComet-Italic.ttf "$<" "$@"

$(FONTDIR)/static-hinted/NeueComet-%.ttf: $(FONTDIR)/static/NeueComet-%.ttf | $(FONTDIR)/static-hinted/NeueComet-Regular.ttf $(FONTDIR)/static-hinted venv
	python -m ttfautohint $(AUTOHINT_ARGS) \
	  --reference $(FONTDIR)/static-hinted/NeueComet-Regular.ttf "$<" "$@"


$(FONTDIR)/var/.%.var.ttf: $(UFODIR)/%.var.designspace build/features_data | $(FONTDIR)/var venv
	fontmake -o variable -m $< --output-path $@ $(FM_ARGS_2)

$(FONTDIR)/var/.%.var.otf: $(UFODIR)/%.var.designspace build/features_data | $(FONTDIR)/var venv
	fontmake -o variable-cff2 -m $< --output-path $@ $(FM_ARGS_2)


# NOTE: the var/ woff2 files are named after the ttf (they are served to the
# web), so they are given an explicit rule to pin the glyf source rather than
# matching the generic %.woff2: %.otf pattern rule.
$(FONTDIR)/var/NeueCometVariable.woff2: $(FONTDIR)/var/NeueCometVariable.ttf | venv
	misc/tools/woff2 compress -o "$@" "$<"

$(FONTDIR)/var/NeueCometVariable-Italic.woff2: $(FONTDIR)/var/NeueCometVariable-Italic.ttf | venv
	misc/tools/woff2 compress -o "$@" "$<"

$(FONTDIR)/var/NeueCometVariable-cff2.woff2: $(FONTDIR)/var/NeueCometVariable.otf | venv
	misc/tools/woff2 compress -o "$@" "$<"

$(FONTDIR)/var/NeueCometVariable-Italic-cff2.woff2: $(FONTDIR)/var/NeueCometVariable-Italic.otf | venv
	misc/tools/woff2 compress -o "$@" "$<"

%.woff2: %.ttf | venv
	misc/tools/woff2 compress -o "$@" "$<"

# Unhinted static webfonts are built from the CFF2 .otf sources (see
# $(FONTDIR)/static/%.otf above), so they need their own rule. Note this must
# NOT be a second "%.woff2: %.otf" pattern rule: make picks the first matching
# pattern rule for a target and will not fall back to the other, which breaks
# the .ttf-derived woff2 files.
$(FONTDIR)/static/%.woff2: $(FONTDIR)/static/%.otf | venv
	misc/tools/woff2 compress -o "$@" "$<"


$(FONTDIR)/var/NeueCometVariable.otf: $(FONTDIR)/var/.NeueComet-Roman.var.otf misc/tools/bake-vf.py
	python misc/tools/bake-vf.py $< -o $@

$(FONTDIR)/var/NeueCometVariable-Italic.otf: $(FONTDIR)/var/.NeueComet-Italic.var.otf misc/tools/bake-vf.py
	python misc/tools/bake-vf.py $< -o $@

$(FONTDIR)/var/NeueCometVariable.ttf: $(FONTDIR)/var/.NeueComet-Roman.var.ttf misc/tools/bake-vf.py
	python misc/tools/bake-vf.py $< -o $@

$(FONTDIR)/var/NeueCometVariable-Italic.ttf: $(FONTDIR)/var/.NeueComet-Italic.var.ttf misc/tools/bake-vf.py
	python misc/tools/bake-vf.py $< -o $@


# The variable font ships in two flavours:
#   glyf (.ttf) -- the default, for the web (docs/, CDN, @font-face)
#   CFF2 (.otf) -- smaller with nicer curves, for desktop installs
# CFF2 VFs have patchy support on older Windows/DirectWrite and some Linux
# stacks, so glyf stays the default for web distribution.
VAR_GLYF := \
	$(FONTDIR)/var/NeueCometVariable.ttf \
	$(FONTDIR)/var/NeueCometVariable-Italic.ttf

VAR_CFF2 := \
	$(FONTDIR)/var/NeueCometVariable.otf \
	$(FONTDIR)/var/NeueCometVariable-Italic.otf

VAR_GLYF_WEB  := $(VAR_GLYF:%.ttf=%.woff2)
VAR_CFF2_WEB := \
	$(FONTDIR)/var/NeueCometVariable-cff2.woff2 \
	$(FONTDIR)/var/NeueCometVariable-Italic-cff2.woff2


$(FONTDIR)/static:
	mkdir -p $@
$(FONTDIR)/static-hinted:
	mkdir -p $@
$(FONTDIR)/var:
	mkdir -p $@
$(UFODIR):
	mkdir -p $@


var: $(VAR_GLYF)

var_otf: $(VAR_CFF2)

var_web: $(VAR_GLYF_WEB)
var_otf_web: $(VAR_CFF2_WEB)

web: var_web static_web static_web_hinted

static: \
	$(FONTDIR)/static-hinted/NeueComet.ttc

STATIC_TEXT_FONTS := \
	NeueComet-Regular \
	NeueComet-Black \
	NeueComet-BlackItalic \
	NeueComet-Italic \
	NeueComet-Thin \
	NeueComet-ThinItalic \
	NeueComet-Light \
	NeueComet-LightItalic \
	NeueComet-ExtraLight \
	NeueComet-ExtraLightItalic \
	NeueComet-Medium \
	NeueComet-MediumItalic \
	NeueComet-SemiBold \
	NeueComet-SemiBoldItalic \
	NeueComet-Bold \
	NeueComet-BoldItalic \
	NeueComet-ExtraBold \
	NeueComet-ExtraBoldItalic

STATIC_DISPLAY_FONTS := \
	NeueCometDisplay-Black \
	NeueCometDisplay-BlackItalic \
	NeueCometDisplay-Regular \
	NeueCometDisplay-Italic \
	NeueCometDisplay-Thin \
	NeueCometDisplay-ThinItalic \
	NeueCometDisplay-Light \
	NeueCometDisplay-LightItalic \
	NeueCometDisplay-ExtraLight \
	NeueCometDisplay-ExtraLightItalic \
	NeueCometDisplay-Medium \
	NeueCometDisplay-MediumItalic \
	NeueCometDisplay-SemiBold \
	NeueCometDisplay-SemiBoldItalic \
	NeueCometDisplay-Bold \
	NeueCometDisplay-BoldItalic \
	NeueCometDisplay-ExtraBold \
	NeueCometDisplay-ExtraBoldItalic

STATIC_FONTS := $(STATIC_TEXT_FONTS) $(STATIC_DISPLAY_FONTS)
STATIC_FONTS_OTF := $(patsubst %,$(FONTDIR)/static/%.otf,$(STATIC_FONTS))
STATIC_FONTS_TTF := $(patsubst %,$(FONTDIR)/static-hinted/%.ttf,$(STATIC_FONTS))
STATIC_FONTS_WEB := $(patsubst %,$(FONTDIR)/static/%.woff2,$(STATIC_FONTS))
STATIC_FONTS_WEB_HINTED := $(patsubst %,$(FONTDIR)/static-hinted/%.woff2,$(STATIC_FONTS))

$(FONTDIR)/static/NeueComet.otc: $(STATIC_FONTS_OTF)
	python -m fontTools.ttLib.__main__ -o $@ $^

$(FONTDIR)/static-hinted/NeueComet.ttc: $(STATIC_FONTS_TTF)
	python -m fontTools.ttLib.__main__ -o $@ $^

static_otf: $(STATIC_FONTS_OTF)
static_ttf: $(STATIC_FONTS_TTF)
static_web: $(STATIC_FONTS_WEB)
static_web_hinted: $(STATIC_FONTS_WEB_HINTED)

all: var var_otf static web static_otf

.PHONY: \
	all var var_otf var_web var_otf_web web \
	static static_otf static_ttf static_web static_web_hinted

# ---------------------------------------------------------------------------------
# testing

test: test_var test_static
test_var: \
	build/fontbakery-report-var.txt
test_static: \
	build/fontbakery-report-text.txt \
  build/fontbakery-report-display.txt

# disabled fontbakery tests:
FBAKE_DISABLED =
FBAKE_DISABLED_STATIC =

FBAKE_DISABLED += com.google.fonts/check/fontbakery_version
# Calls a server to see if there's a newer version of fontbakery and
# FAILs if there is. This breaks reproducible builds.

FBAKE_DISABLED += com.google.fonts/check/family/win_ascent_and_descent
# "FAIL OS/2.usWinAscent value should be equal or greater than 2269,
#  but got 1984 instead"
# "FAIL OS/2.usWinDescent value should be equal or greater than 660,
#  but got 494 instead"


FBAKE_DISABLED_STATIC += com.google.fonts/check/family/underline_thickness
# "Fonts have consistent underline thickness"
# Neue Comet explicitly have varying underline thickness, matching wght

FBAKE_DISABLED_STATIC += com.google.fonts/check/contour_count
# This test is pedantic; generates warnings when the number of contours are different
# than what is usually seen in other fonts. No real world impact.

# The following test are minor issues, left enabled for the var tests
# but disabled for the static tests to reduce noise

FBAKE_DISABLED_STATIC += com.google.fonts/check/legacy_accents
# "Glyph <NAME> has a legacy accent component (hungarumlaut)"
# TODO: improve the design of Hungar* composite glyphs to use marks

FBAKE_DISABLED_STATIC += com.google.fonts/check/gdef_mark_chars
# "Check mark characters are in GDEF mark glyph class"
# "WARN The following mark characters could be in the GDEF mark glyph
#  class: uni0488 (U+0488), uni0489 (U+0489), uni20DD (U+20DD), uni20DE (U+20DE)"

FBAKE_DISABLED_STATIC += com.google.fonts/check/gdef_spacing_marks
# "Check glyphs in mark glyph class are non-spacing"
# "WARN The following spacing glyphs may be in the GDEF mark glyph class by mistake:
#  dotbelow (U+0323)

# FBAKE_ARGS are common args for all fontbakery targets
FBAKE_ARGS = \
	check-universal \
	--no-colors \
	--no-progress \
	--loglevel WARN \
	--succinct \
	--full-lists \
	-j \
	$(patsubst %,-x %,$(FBAKE_DISABLED))

FBAKE_ARGS_STATIC = $(FBAKE_ARGS) $(patsubst %,-x %,$(FBAKE_DISABLED_STATIC))

STATIC_TEXT_FONTS_TTF = $(patsubst %,$(FONTDIR)/static-hinted/%.ttf,$(STATIC_TEXT_FONTS))
STATIC_DISPLAY_FONTS_TTF = $(patsubst %,$(FONTDIR)/static-hinted/%.ttf,$(STATIC_DISPLAY_FONTS))

build/fontbakery-report-var.txt: $(VAR_GLYF) | venv
	@echo "fontbakery NeueCometVariable -> $(@) ..."
	@fontbakery $(FBAKE_ARGS) $^ > $@ \
		|| (cat $@; echo "report at $@"; touch -m -t 199001010000 $@; exit 1)
	@echo "fontbakery NeueCometVariable: PASS"
	@grep -E -A7 '^Total:' $@ | tail -6 | sed -E 's/^ +/  /g'

build/fontbakery-report-text.txt: $(STATIC_TEXT_FONTS_TTF) | venv
	@echo "fontbakery Neue Comet -> $@ ..."
	@fontbakery $(FBAKE_ARGS_STATIC) $^ > $@ \
		|| (cat $@; echo "report at $@"; touch -m -t 199001010000 $@; exit 1)
	@echo "fontbakery Neue Comet: PASS"
	@grep -E -A7 '^Total:' $@ | tail -6 | sed -E 's/^ +/  /g'

build/fontbakery-report-display.txt: $(STATIC_DISPLAY_FONTS_TTF) | venv
	@echo "fontbakery NeueCometDisplay -> $@ ..."
	@fontbakery $(FBAKE_ARGS_STATIC) $^ > $@ \
		|| (cat $@; echo "report at $@"; touch -m -t 199001010000 $@; exit 1)
	@echo "fontbakery NeueCometDisplay: PASS"
	@grep -E -A7 '^Total:' $@ | tail -6 | sed -E 's/^ +/  /g'

.PHONY: test test_var

# ---------------------------------------------------------------------------------
# zip

zip: all
	bash misc/makezip2.sh -reveal-in-finder \
		"build/release/NeueComet-$(VERSION)-$(shell git rev-parse --short=10 HEAD).zip"

zip_beta: $(VAR_GLYF) $(VAR_GLYF_WEB)
	mkdir -p build/release
	zip -j -q -X "build/release/NeueComet_beta-$(VERSION)-$(shell date '+%Y%m%d_%H%M')-$(shell git rev-parse --short=10 HEAD).zip" $^

.PHONY: zip zip_beta

# ---------------------------------------------------------------------------------
# distribution
# - preflight checks for existing version archive and dirty git state.
# - step1 rebuilds from scratch, since font version & ID is based on git hash.
# - step2 runs tests, then makes a zip archive and updates the website (docs/ dir.)

DIST_ZIP = build/release/NeueComet-${VERSION}.zip

dist:
	@echo "——————————————————————————————————————————————————————————————————"
	@echo "Creating distribution for version ${VERSION}"
	@echo "——————————————————————————————————————————————————————————————————"
	@# check for existing version archive
	@if [ -f "${DIST_ZIP}" ]; then \
		echo "${DIST_ZIP} already exists. Bump version or rm zip file to continue." >&2; \
		exit 1; \
	fi
	@# check for uncommitted changes
	@git status --short | grep -qv '??' && (\
		echo "Warning: uncommitted changes:" >&2; git status --short | grep -v '??' ;\
		[ -t 1 ] || exit 1 ; \
		printf "Press ENTER to continue or ^C to cancel " ; read X) || true
	@#
	$(MAKE) -f $(MAKEFILE) -j$(nproc) clean
	$(MAKE) -f $(MAKEFILE) -j$(nproc) all
	$(MAKE) -f $(MAKEFILE) -j$(nproc) test
	$(MAKE) -f $(MAKEFILE) -j$(nproc) dist_zip dist_docs
	$(MAKE) -f $(MAKEFILE) dist_postflight

dist_zip: | venv
	bash misc/makezip2.sh -reveal-in-finder "$(DIST_ZIP)"

dist_docs:
	$(MAKE) -C docs -j$(nproc) dist

dist_postflight:
	@echo "——————————————————————————————————————————————————————————————————"
	@echo ""
	@echo "Next steps:"
	@echo ""
	@echo "1) Commit & push changes"
	@echo ""
	@echo "2) Create new release with ${DIST_ZIP} at"
	@echo "   https://github.com/rsms/inter/releases/new?tag=v${VERSION}"
	@echo ""
	@echo "3) Bump version in version.txt (to the next future version)"
	@echo "   and commit & push changes"
	@echo ""
	@echo "——————————————————————————————————————————————————————————————————"

.PHONY: dist dist_preflight dist_step1 dist_step2 dist_zip dist_docs dist_postflight


# ---------------------------------------------------------------------------------
# install

INSTALLDIR := $(HOME)/Library/Fonts/NeueComet

install: install_var install_ttf

install_var: \
	$(INSTALLDIR)/NeueCometVariable.ttf \
	$(INSTALLDIR)/NeueCometVariable-Italic.ttf

install_ttf: $(INSTALLDIR)/NeueComet.ttc
install_otf: $(INSTALLDIR)/NeueComet.otc

$(INSTALLDIR)/%.ttc: $(FONTDIR)/static-hinted/%.ttc | $(INSTALLDIR)
	@# remove conflicting OTF fonts
	rm -f $(INSTALLDIR)/NeueComet*.otf $(INSTALLDIR)/NeueComet*.otc
	cp -a $^ $@

$(INSTALLDIR)/%.otc: $(FONTDIR)/static/%.otc | $(INSTALLDIR)
	@# remove conflicting TTF fonts
	@rm -fv $(INSTALLDIR)/NeueComet*.ttc
	cp -a $^ $@

$(INSTALLDIR)/NeueCometVariable.ttf: $(FONTDIR)/var/NeueCometVariable.ttf | $(INSTALLDIR)
	@# force a fresh copy
	@rm -fv $(INSTALLDIR)/NeueCometVariable.ttf
	cp -a $^ $@

$(INSTALLDIR)/NeueCometVariable-Italic.ttf: $(FONTDIR)/var/NeueCometVariable-Italic.ttf | $(INSTALLDIR)
	@# force a fresh copy
	@rm -fv $(INSTALLDIR)/NeueCometVariable-Italic.ttf
	cp -a $^ $@

# Desktop installs get the CFF2 variable font: smaller, nicer curves.
install_var_otf: \
	$(INSTALLDIR)/NeueCometVariable.otf \
	$(INSTALLDIR)/NeueCometVariable-Italic.otf

$(INSTALLDIR)/NeueCometVariable.otf: $(FONTDIR)/var/NeueCometVariable.otf | $(INSTALLDIR)
	@# force a fresh copy
	@rm -fv $(INSTALLDIR)/NeueCometVariable.otf
	cp -a $^ $@

$(INSTALLDIR)/NeueCometVariable-Italic.otf: $(FONTDIR)/var/NeueCometVariable-Italic.otf | $(INSTALLDIR)
	@# force a fresh copy
	@rm -fv $(INSTALLDIR)/NeueCometVariable-Italic.otf
	cp -a $^ $@

$(INSTALLDIR)/%.otf: $(FONTDIR)/static/%.otf | $(INSTALLDIR)
	@# remove conflicting TTF fonts
	rm -f $(INSTALLDIR)/{NeueComet,NeueCometDisplay}-*.ttf
	cp -a $^ $@

$(INSTALLDIR):
	mkdir -p $@

.PHONY: install install_var install_var_otf install_ttf install_otf

# ---------------------------------------------------------------------------------
# debug

build/ttx/NeueComet-Var%: $(FONTDIR)/var/NeueComet-Var%.ttf
	rm -rf "build/ttx/$(basename $(notdir $^))"
	mkdir -p "build/ttx/$(basename $(notdir $^))"
	cp $^ "build/ttx/$(basename $(notdir $^))/$(notdir $^)"
	ttx -x glyf -x GPOS -x GSUB -x gvar -i -f -s \
		"build/ttx/$(basename $(notdir $^))/$(notdir $^)"
	@echo "Dumped $(notdir $^) to build/ttx/$(basename $(notdir $^))/"

build/ttx/%: $(FONTDIR)/static/%.ttf
	rm -rf "build/ttx/$(basename $(notdir $^))"
	mkdir -p "build/ttx/$(basename $(notdir $^))"
	cp $^ "build/ttx/$(basename $(notdir $^))/$(notdir $^)"
	ttx -x glyf -x GPOS -x GSUB -i -f -s "build/ttx/$(basename $(notdir $^))/$(notdir $^)"
	@echo "Dumped $(notdir $^) to build/ttx/$(basename $(notdir $^))/"

ttx_var_roman: build/ttx/NeueCometVariable
ttx_var_italic: build/ttx/NeueCometVariable-Italic
ttx_var: ttx_var_roman ttx_var_italic
ttx_static: $(patsubst %,build/ttx/%,$(STATIC_FONTS))

.PHONY: ttx_var ttx_var_roman ttx_var_italic ttx_static

# ---------------------------------------------------------------------------------
# misc

clean:
	@for f in build/tmp build/fonts build/ufo build/ttx; do \
		[ ! -e $$f ] || echo "rm -rf $$f"; (rm -rf $$f; rm -rf $$f) & \
	done; wait

docs:
	$(MAKE) -C docs serve

# update_ucd downloads the latest Unicode data (Nothing depends on this target)
ucd_version := 12.1.0
update_ucd:
	@echo "# Unicode $(ucd_version)" > misc/UnicodeData.txt
	curl '-#' "https://www.unicode.org/Public/$(ucd_version)/ucd/UnicodeData.txt" \
	>> misc/UnicodeData.txt

.PHONY: clean docs update_ucd

# ---------------------------------------------------------------------------------
# list make targets
#
# We copy the Makefile (first in MAKEFILE_LIST) and disable the include to only list
# primary targets, avoiding the generated targets.
list:
	@mkdir -p build/etc \
	&& cat $(MAKEFILE) \
	 | sed 's/include /#include /g' > build/etc/Makefile-list \
	&& $(MAKE) -pRrq -f build/etc/Makefile-list : 2>/dev/null \
	 | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' \
	 | sort \
	 | egrep -v -e '^_|/' \
	 | egrep -v -e '^[^[:alnum:]]' -e '^$@$$'

.PHONY: list

# ---------------------------------------------------------------------------------
# initialize toolchain

venv: $(VENVDIR)/config2.stamp

$(VENVDIR)/config2.stamp: Pipfile.lock Pipfile
	@mkdir -p build
	[ ! -f "$(VENVDIR)/config.stamp" ] || rm -rf "$(VENVDIR)"
	[ -d "$(VENVDIR)" ] || python3 -m venv "$(VENVDIR)"
	pip install pipenv==2023.8.28
	pipenv install
	touch $@

venv-update:
	pipenv update

reset: clean
	rm -rf "$(VENVDIR)"

.PHONY: venv venv-update reset
