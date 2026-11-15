#!/bin/sh
set -eu
cd "$(dirname "$0")"
if command -v python3 >/dev/null 2>&1; then
  exec python3 -m healthqualify.local_edition_v08
fi
echo "Python 3.10+ required" >&2
exit 1
