#!/bin/bash -e
cd "$(dirname "$0")/.."

OPT_HELP=false
OPT_TEXT=false
OPT_DISPLAY=false
OPT_REVEAL_IN_FINDER=false
OUTFILE=

# parse args
while [[ $# -gt 0 ]]; do
  case "$1" in
  -h*|--h*)
    OPT_HELP=true
    shift
    ;;
  -text|--text)
    OPT_TEXT=true
    shift
    ;;
  -display|--display)
    OPT_DISPLAY=true
    shift
    ;;
  -a*|--a*)
    OPT_TEXT=true
    OPT_DISPLAY=true
    shift
    ;;
  -reveal-in-finder)
    OPT_REVEAL_IN_FINDER=true
    shift
    ;;
  -*)
    echo "$0: Unknown option $1" >&2
    OPT_HELP=true
    shift
    ;;
  *)
    if [[ "$OUTFILE" != "" ]] && ! $OPT_HELP; then
      echo "$0: Extra unexpected argument(s) after <outfile>" >&2
      OPT_HELP=true
    fi
    OUTFILE=$1
    shift
    ;;
  esac
done
if (! $OPT_TEXT && ! $OPT_DISPLAY); then
  OPT_HELP=true
  echo "$0: Need at least one of: -all, -display, -text" >&2
fi
if $OPT_HELP; then
  echo "Usage: $0 [options] <outfile>"
  echo "Options:"
  echo "  -h, -help          Show help."
  echo "  -text              Include Neue Comet Text"
  echo "  -display           Include Neue Comet Display"
  echo "  -a, -all           Include all fonts"
  echo "  -reveal-in-finder  After creating the zip file, show it in Finder"
  exit 1
fi

# tmp dir
ZIPDIR=build/tmp/zip
FONTDIR=build/fonts

# convert relative path to absolute if needed
OUTFILE_ABS=$OUTFILE
if [[ "$OUTFILE_ABS" != /* ]]; then
  OUTFILE_ABS=$PWD/$OUTFILE_ABS
fi

# cleanup any previous build
rm -rf "$ZIPDIR"
rm -f  build/tmp/a.zip

# create directories
mkdir -p \
  "$ZIPDIR/Neue Comet Desktop" \
  "$ZIPDIR/Neue Comet Hinted for Windows/Desktop" \
  "$ZIPDIR/Neue Comet Hinted for Windows/Web" \
  "$ZIPDIR/Neue Comet Variable" \
  "$ZIPDIR/Neue Comet Variable/Single axis" \
  "$ZIPDIR/Neue Comet Web"

# copy font files
# ----------------------------------------------------------------------------
if $OPT_TEXT; then
  # Neue Comet Desktop
  cp $FONTDIR/const/NeueComet-*.otf          "$ZIPDIR/Neue Comet Desktop/" &
  cp $FONTDIR/var/NeueComet-V.var.ttf        "$ZIPDIR/Neue Comet Desktop/NeueComet-V.ttf" &

  # Neue Comet Hinted for Windows
  cp "misc/dist/about hinted fonts.txt"  "$ZIPDIR/Neue Comet Hinted for Windows/" &
  cp $FONTDIR/const-hinted/NeueComet-*.ttf   "$ZIPDIR/Neue Comet Hinted for Windows/Desktop/" &
  cp $FONTDIR/const-hinted/NeueComet-*.woff* "$ZIPDIR/Neue Comet Hinted for Windows/Web/" &
  cp misc/dist/neue-comet.css                 "$ZIPDIR/Neue Comet Hinted for Windows/Web/" &

  # Neue Comet Variable
  cp $FONTDIR/var/NeueComet.var.ttf          "$ZIPDIR/Neue Comet Variable/NeueComet.ttf" &
  cp $FONTDIR/var/NeueComet-roman.var.ttf    "$ZIPDIR/Neue Comet Variable/Single axis/NeueComet-roman.ttf" &
  cp $FONTDIR/var/NeueComet-italic.var.ttf   "$ZIPDIR/Neue Comet Variable/Single axis/NeueComet-italic.ttf" &

  # Neue Comet Web
  cp $FONTDIR/const/NeueComet-*.woff*        "$ZIPDIR/Neue Comet Web/" &
  cp $FONTDIR/var/NeueComet.var.woff2        "$ZIPDIR/Neue Comet Web/" &
  cp $FONTDIR/var/NeueComet-roman.var.woff2  "$ZIPDIR/Neue Comet Web/" &
  cp $FONTDIR/var/NeueComet-italic.var.woff2 "$ZIPDIR/Neue Comet Web/" &
  cp misc/dist/neue-comet.css                 "$ZIPDIR/Neue Comet Web/" &
fi
# ----------------------------------------------------------------------------
if $OPT_DISPLAY; then
  # Neue Comet Desktop
  cp $FONTDIR/const/NeueCometDisplay-*.otf          "$ZIPDIR/Neue Comet Desktop/" &
  cp $FONTDIR/var/NeueCometDisplay-V.var.ttf        "$ZIPDIR/Neue Comet Desktop/NeueCometDisplay-V.ttf" &

  # Neue Comet Hinted for Windows
  cp "misc/dist/about hinted fonts.txt"         "$ZIPDIR/Neue Comet Hinted for Windows/" &
  cp $FONTDIR/const-hinted/NeueCometDisplay-*.ttf   "$ZIPDIR/Neue Comet Hinted for Windows/Desktop/" &
  cp $FONTDIR/const-hinted/NeueCometDisplay-*.woff* "$ZIPDIR/Neue Comet Hinted for Windows/Web/" &
  cp misc/dist/neue-comet-display.css                "$ZIPDIR/Neue Comet Hinted for Windows/Web/" &

  # Neue Comet Variable
  cp $FONTDIR/var/NeueCometDisplay.var.ttf          "$ZIPDIR/Neue Comet Variable/NeueCometDisplay.ttf" &
  cp $FONTDIR/var/NeueCometDisplay-roman.var.ttf    "$ZIPDIR/Neue Comet Variable/Single axis/NeueCometDisplay-roman.ttf" &
  cp $FONTDIR/var/NeueCometDisplay-italic.var.ttf   "$ZIPDIR/Neue Comet Variable/Single axis/NeueCometDisplay-italic.ttf" &

  # Neue Comet Web
  cp $FONTDIR/const/NeueCometDisplay-*.woff*        "$ZIPDIR/Neue Comet Web/" &
  cp $FONTDIR/var/NeueCometDisplay.var.woff2        "$ZIPDIR/Neue Comet Web/" &
  cp $FONTDIR/var/NeueCometDisplay-roman.var.woff2  "$ZIPDIR/Neue Comet Web/" &
  cp $FONTDIR/var/NeueCometDisplay-italic.var.woff2 "$ZIPDIR/Neue Comet Web/" &
  cp misc/dist/neue-comet-display.css                "$ZIPDIR/Neue Comet Web/" &
fi
# ----------------------------------------------------------------------------

# copy misc stuff
cp misc/dist/install*.txt        "$ZIPDIR/"
cp LICENSE.txt                   "$ZIPDIR/"
mkdir -p "$(dirname "$OUTFILE_ABS")"

# wait for processes to finish
wait

# zip
pushd "$ZIPDIR" >/dev/null
zip -q -X -r "$OUTFILE_ABS" *
popd >/dev/null
rm -rf "$ZIPDIR"

echo "Created $OUTFILE"
if $OPT_REVEAL_IN_FINDER && [ -f /usr/bin/open ]; then
  /usr/bin/open --reveal "$OUTFILE"
fi
