#!/usr/bin/env bash
# seed-reminder.sh <pkg-root> <nightshift-home> — install/update $NS/reminder.txt.
#
# reminder.txt is user-editable on purpose, so we must never clobber local edits.
# But the original `cp -n` seed meant the opposite failure: shipped improvements to
# the working practices NEVER reached anyone who had already installed, and the
# reminder is the one file where an upstream fix has to propagate. So we keep a copy
# of what we last shipped ($NS/.reminder.shipped). If the installed file still matches
# it, the user never touched it and we can safely update in place. If it doesn't
# match — edited, or installed before this bookkeeping existed — we leave it alone
# and drop the new version next to it for the user to diff in.
set -euo pipefail
PKG="${1:?pkg root}"; NS="${2:?nightshift home}"
SRC="$PKG/share/reminder.txt"
DST="$NS/reminder.txt"
SHIPPED="$NS/.reminder.shipped"
mkdir -p "$NS/entries"
[ -f "$SRC" ] || exit 0

if [ ! -f "$DST" ]; then
  cp "$SRC" "$DST"; cp "$SRC" "$SHIPPED"
elif cmp -s "$DST" "$SRC"; then
  cp "$SRC" "$SHIPPED"                       # already current; just record it
elif [ -f "$SHIPPED" ] && cmp -s "$DST" "$SHIPPED"; then
  cp "$SRC" "$DST"; cp "$SRC" "$SHIPPED"
  echo "nightshift: updated $DST to the current shipped working practices."
else
  cp "$SRC" "$DST.new"
  echo "nightshift: $DST has local edits — left as-is. Newer version written to $DST.new (diff it in)."
fi
