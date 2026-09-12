#!/usr/bin/env bash

set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
work="$(mktemp -d "${TMPDIR:-/tmp}/game-triathlon-site.XXXXXX")"
trap 'rm -rf "$work"' EXIT
site="$work/_site"

"$root/scripts/build_site.sh" "$site"

cat > "$work/expected" <<'EOF'
assets/images/app-icon.png
assets/media/gameplay-poster.webp
assets/media/gameplay.mp4
assets/media/gameplay.webm
assets/media/hangar.webp
assets/media/rf4-gameplay.webp
assets/media/rf4-launcher.webp
assets/site.js
assets/styles.css
index.html
licenses.html
release.json
styles.css
EOF

(cd "$site" && find . -type f -print | sed 's|^./||' | LC_ALL=C sort) \
  > "$work/actual"
diff -u "$work/expected" "$work/actual"

if find "$site" \( -name '.DS_Store' -o -name '.git' -o -name '.github' \
  -o -name '*.mtreplay' \) -print -quit | grep -q .; then
  printf 'error: в артефакт попал служебный или исходный файл\n' >&2
  exit 1
fi

python3 "$root/scripts/check_site.py" "$site"
printf 'site artifact test passed\n'
