#!/usr/bin/env python3
"""Минимальные проверки статического сайта без сторонних зависимостей."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
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
    "0x1fb78e0ff7c89656a00cd696e1b5ce9c070e50da",
    "1NEGf85SvXb1PGvRmXdgd9F5bgiXCj26Am",
)
for text in required_text:
    if text not in html:
        fail(f"в index.html отсутствует обязательный текст: {text}")

site_js = (ROOT / "assets/site.js").read_text(encoding="utf-8")
if "releases/latest/download/GameTriathlon.dmg" not in site_js:
    fail("в site.js отсутствует постоянная ссылка на последний DMG")

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
    ROOT / "README.md",
)
for forbidden in ("Sources/GameTriathlon", "Application Support/GameTriathlon", "git@github.com:frol555"):
    for path in public_text_files:
        content = path.read_text(encoding="utf-8")
        if forbidden in content:
            fail(f"публичный файл {path.relative_to(ROOT)} содержит закрытый маркер: {forbidden}")

print("site checks passed")
