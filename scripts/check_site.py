#!/usr/bin/env python3
"""Минимальные проверки статического сайта без сторонних зависимостей."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parents[1]
if len(sys.argv) > 2:
    print(f"usage: {Path(sys.argv[0]).name} [SITE_ROOT]", file=sys.stderr)
    raise SystemExit(2)

checking_artifact = len(sys.argv) == 2
ROOT = Path(sys.argv[1]).resolve() if checking_artifact else SOURCE_ROOT
if not ROOT.is_dir():
    print(f"error: каталог сайта не найден: {ROOT}", file=sys.stderr)
    raise SystemExit(1)
INDEX = ROOT / "index.html"


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


if not INDEX.is_file():
    fail("нет index.html")

html = INDEX.read_text(encoding="utf-8")
required_text = (
    "Большие игры.",
    "Windows-игры",
    "Мир танков",
    "Мир кораблей",
    "Tanks Blitz",
    "macOS 26+",
    "gametriathlon@yandex.com",
    "pay.cloudtips.ru/p/ef916df9",
    "0x27761afc6b5ac967888d84c2d5a612c50018a068",
    "bc1qhl3lvkcwkhywe4c87dkq8eklwwn3tvt4s2gnzc",
)
for text in required_text:
    if text not in html:
        fail(f"в index.html отсутствует обязательный текст: {text}")

for marker in ('role="tablist"', 'role="tab"', "data-support-panel", "data-copy", "aria-live"):
    if marker not in html:
        fail(f"в блоке поддержки отсутствует доступный элемент: {marker}")

section_positions = [html.find(f'id="{section_id}"') for section_id in ("top", "support", "games")]
if any(position < 0 for position in section_positions) or section_positions != sorted(section_positions):
    fail("секции должны идти в порядке: top → support → games")

for forbidden in (
    "игры Lesta на Mac",
    "Genshin",
    "Сбер · МИР",
    'data-support-tab="card"',
    'data-support-panel="card"',
):
    if forbidden.casefold() in html.casefold():
        fail(f"в index.html осталось неподтверждённое или старое позиционирование: {forbidden}")

if re.search(r"\b(?:\d{4}[\s-]*){3}\d{4}\b", html):
    fail("в index.html обнаружен 16-значный номер карты")

site_js = (ROOT / "assets/site.js").read_text(encoding="utf-8")
site_css = (ROOT / "assets/styles.css").read_text(encoding="utf-8")
if "releases/latest/download/GameTriathlon.dmg" not in site_js:
    fail("в site.js отсутствует постоянная ссылка на последний DMG")

for asset in ("assets/styles.css", "assets/site.js"):
    if not re.search(rf'(?:href|src)="{re.escape(asset)}\?v=[^"]+"', html):
        fail(f"ресурс {asset} подключён без версии для сброса кеша")

gameplay_markers = (
    '<video class="gameplay-video"',
    'poster="assets/media/gameplay-poster.webp"',
    'src="assets/media/gameplay.webm" type="video/webm"',
    'src="assets/media/gameplay.mp4" type="video/mp4"',
    'src="assets/media/hangar.webp"',
    'alt="Ангар «Мира танков» на Mac"',
    'data-lightbox-src="assets/media/hangar.webp"',
    'data-lightbox-src="assets/media/gameplay-poster.webp"',
    '<dialog class="media-lightbox"',
    'data-lightbox-image',
)
for marker in gameplay_markers:
    if marker not in html:
        fail(f"в секции геймплея отсутствует медиамаркер: {marker}")

if "data-gameplay-video" not in html or "IntersectionObserver" not in site_js:
    fail("видео геймплея не управляется с учётом видимости секции")
if "prefers-reduced-motion: reduce" not in site_js:
    fail("видео геймплея не учитывает настройку уменьшения движения")
for marker in ("showModal", "data-lightbox-trigger", "data-lightbox-close"):
    if marker not in site_js and marker not in html:
        fail(f"в увеличении изображений отсутствует маркер: {marker}")
if not re.search(r"\.gameplay-video\s*\{[^}]*object-fit:\s*contain", site_css):
    fail("видео геймплея должно показывать полный кадр без обрезки FPS")
if any((ROOT / "assets").rglob("*.mtreplay")):
    fail("исходный реплей не должен публиковаться в assets")

for relative, limit in {
    "assets/media/gameplay.mp4": 10_000_000,
    "assets/media/gameplay.webm": 10_000_000,
    "assets/media/gameplay-poster.webp": 1_000_000,
    "assets/media/hangar.webp": 1_000_000,
}.items():
    media = ROOT / relative
    if not media.is_file():
        fail(f"не найден медиаресурс: {relative}")
    if media.stat().st_size > limit:
        fail(f"медиаресурс слишком большой: {relative}")

if "http://" in html:
    fail("в index.html обнаружена небезопасная HTTP-ссылка")

for match in re.finditer(r'(?:src|href)="([^"]+)"', html):
    target = match.group(1)
    if target.startswith(("https://", "mailto:", "#")):
        continue
    local = ROOT / target.split("?", 1)[0].split("#", 1)[0]
    if not local.exists():
        fail(f"не найден локальный ресурс: {target}")

try:
    release = json.loads((ROOT / "release.json").read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as error:
    fail(f"release.json не читается: {error}")

required_release_keys = {"available", "version", "date", "size", "changes"}
if set(release) != required_release_keys:
    fail("release.json содержит неверный набор полей")
if not isinstance(release["available"], bool):
    fail("release.available должен быть boolean")
if not all(isinstance(release[key], str) for key in ("version", "date", "size")):
    fail("version, date и size должны быть строками")
if not isinstance(release["changes"], list) or not all(isinstance(item, str) for item in release["changes"]):
    fail("changes должен быть массивом строк")
if release["available"] and not all((release["version"], release["date"], release["size"], release["changes"])):
    fail("доступный релиз должен содержать все отображаемые данные")

public_text_files = (
    INDEX,
    ROOT / "licenses.html",
    ROOT / "styles.css",
    ROOT / "assets/styles.css",
    ROOT / "assets/site.js",
    ROOT / "release.json",
)
if not checking_artifact:
    public_text_files += (ROOT / "README.md",)
for forbidden in ("Sources/GameTriathlon", "Application Support/GameTriathlon", "git@github.com:frol555"):
    for path in public_text_files:
        content = path.read_text(encoding="utf-8")
        if forbidden in content:
            fail(f"публичный файл {path.relative_to(ROOT)} содержит закрытый маркер: {forbidden}")

print("site checks passed")
