#!/bin/sh
# Uninstall git hook used by old toolchain
case "$0" in
  */.git/hooks/*) rm "$0";;
  *) echo "Neue Comet git hooks are no longer used"
esac
