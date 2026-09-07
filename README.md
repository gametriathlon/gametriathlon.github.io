# Game Triathlon — официальный сайт

Публичный лендинг и релизы Game Triathlon: приложения для запуска совместимых
Windows-игр на Mac с Apple Silicon. Сейчас проверены «Мир танков»,
«Мир кораблей» и Tanks Blitz.

- Сайт: <https://gametriathlon.github.io>
- Релизы: <https://github.com/gametriathlon/gametriathlon.github.io/releases>
- Обратная связь: <gametriathlon@yandex.com>

Исходный код приложения находится в отдельном закрытом репозитории и не входит
в этот проект. Условия сторонних компонентов и порядок получения их исходных
текстов опубликованы на странице `licenses.html`.

## Локальный просмотр

```bash
python3 -m http.server 8000
```

Затем откройте <http://localhost:8000>.

## Проверка

```bash
python3 scripts/check_site.py
```

## Публикация релиза

Создайте GitHub Release с тегом `vX.Y.Z` и загрузите DMG под неизменным именем
`GameTriathlon.dmg`. Затем обновите `release.json`: установите `available` в
`true`, укажите версию, дату, размер и краткий список изменений.
