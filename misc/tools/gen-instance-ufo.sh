#!/bin/bash
set -e
PROG=${0##*/}
DESIGNSPACE=$1
UFO=$2

INSTANCE_Light="Neue Comet Light"
INSTANCE_ExtraLight="Neue Comet ExtraLight"
INSTANCE_Medium="Neue Comet Medium"
INSTANCE_SemiBold="Neue Comet SemiBold"
INSTANCE_Bold="Neue Comet Bold"
INSTANCE_ExtraBold="Neue Comet ExtraBold"

INSTANCE_LightItalic="Neue Comet Light Italic"
INSTANCE_ExtraLightItalic="Neue Comet ExtraLight Italic"
INSTANCE_MediumItalic="Neue Comet Medium Italic"
INSTANCE_SemiBoldItalic="Neue Comet SemiBold Italic"
INSTANCE_BoldItalic="Neue Comet Bold Italic"
INSTANCE_ExtraBoldItalic="Neue Comet ExtraBold Italic"

INSTANCE_DisplayThin="Neue Comet Display Thin"
INSTANCE_DisplayLight="Neue Comet Display Light"
INSTANCE_DisplayExtraLight="Neue Comet Display ExtraLight"
INSTANCE_DisplayRegular="Neue Comet Display Regular"
INSTANCE_DisplayMedium="Neue Comet Display Medium"
INSTANCE_DisplaySemiBold="Neue Comet Display SemiBold"
INSTANCE_DisplayBold="Neue Comet Display Bold"
INSTANCE_DisplayExtraBold="Neue Comet Display ExtraBold"
INSTANCE_DisplayBlack="Neue Comet Display Black"

INSTANCE_DisplayThinItalic="Neue Comet Display Thin Italic"
INSTANCE_DisplayLightItalic="Neue Comet Display Light Italic"
INSTANCE_DisplayExtraLightItalic="Neue Comet Display ExtraLight Italic"
INSTANCE_DisplayItalic="Neue Comet Display Italic"
INSTANCE_DisplayMediumItalic="Neue Comet Display Medium Italic"
INSTANCE_DisplaySemiBoldItalic="Neue Comet Display SemiBold Italic"
INSTANCE_DisplayBoldItalic="Neue Comet Display Bold Italic"
INSTANCE_DisplayExtraBoldItalic="Neue Comet Display ExtraBold Italic"
INSTANCE_DisplayBlackItalic="Neue Comet Display Black Italic"

MASTER_Thin=1
MASTER_Regular=1
MASTER_Black=1
MASTER_ThinItalic=1
MASTER_Italic=1
MASTER_BlackItalic=1
MASTER_DisplayThin=1
MASTER_Display=1
MASTER_DisplayBlack=1
MASTER_DisplayThinItalic=1
MASTER_DisplayItalic=1
MASTER_DisplayBlackItalic=1

_err() { echo "$PROG: $@" >&2; exit 1; }

# build/ufo/NeueCometDisplay-ExtraBold.ufo -> DisplayExtraBold
UFO_NAME=$(basename "$UFO" .ufo)
case "$UFO_NAME" in
  NeueComet-*)        UFO_NAME=${UFO_NAME:10} ;;
  NeueCometDisplay-*) UFO_NAME=Display${UFO_NAME:17} ;;
esac

# DisplayExtraBold -> "Neue Comet Display ExtraBold"
INSTANCE=INSTANCE_${UFO_NAME} ; INSTANCE=${!INSTANCE}

# If UFO is not an instance, assume that it's a master (or else error)
# master UFOs are byproducts of building NeueComet-Roman.designspace, so we just update mtime.
if [ -z "$INSTANCE" ]; then
  MASTER=MASTER_${UFO_NAME}
  [ -n "${!MASTER}" ] || _err "Failed to map UFO name \"$UFO_NAME\" to instance"
  [ -d "$UFO" ] || _err "Cannot find master UFO: $UFO"
  echo "touch $UFO"
  touch "$UFO"
  exit
fi

set -x
fontmake -o ufo -m "$DESIGNSPACE" --output-path "$UFO" -i "$INSTANCE"
exec python misc/tools/postprocess_instance_ufo.py "$UFO"
