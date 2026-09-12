#!/usr/bin/env bash

set -euo pipefail

root="$(cd "$(dirname "$0")/.." && pwd)"
output="${1:-}"

fail() {
  printf 'error: %s\n' "$1" >&2
  exit 1
}

[ -n "$output" ] || fail "использование: scripts/build_site.sh OUTPUT_DIRECTORY"
case "$output" in
  /|.|..|"$root"|"$root"/) fail "небезопасный выходной каталог: $output" ;;
esac
[ ! -e "$output" ] || fail "выходной каталог уже существует: $output"

files=(
  index.html
  licenses.html
  styles.css
  release.json
  assets/styles.css
  assets/site.js
  assets/images/app-icon.png
  assets/media/gameplay.mp4
  assets/media/gameplay.webm
  assets/media/gameplay-poster.webp
  assets/media/hangar.webp
  assets/media/rf4-launcher.webp
  assets/media/rf4-gameplay.webp
)

mkdir -p "$output"
for relative in "${files[@]}"; do
  source_file="$root/$relative"
  [ -f "$source_file" ] || fail "отсутствует публичный файл: $relative"
  mkdir -p "$output/$(dirname "$relative")"
  cp "$source_file" "$output/$relative"
done

actual_count="$(find "$output" -type f | wc -l | tr -d ' ')"
[ "$actual_count" -eq "${#files[@]}" ] \
  || fail "в артефакте $actual_count файлов вместо ${#files[@]}"

printf 'site artifact ready: %s (%s files)\n' "$output" "$actual_count"
