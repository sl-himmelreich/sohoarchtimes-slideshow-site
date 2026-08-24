# Claude Code handoff — SohoArchTimes — 2026-08-19

> **Адаптация 2026-08-19 (перенос в Claude Code; всё живёт в этом репозитории):**
> - `/home/user/workspace/cron_tracking/3f016dc2/publish_album.py` → `ops/publish_album.py` (токен теперь только из env TELEGRAM_BOT_TOKEN)
> - `/home/user/workspace/cron_tracking/3f016dc2/published_objects.json` → `ops/published_objects.json`
> - `/home/user/workspace/cron_tracking/3f016dc2/runbook.md` → `ops/runbook.md`
> - `/home/user/workspace/build_sohoarchtimes_catalog.py` → `ops/build_sohoarchtimes_catalog.py`
> - `/home/user/workspace/sohoarchtimes_site_data/` → `ops/site_data/`
> - `/home/user/workspace/sohoarchtimes_slideshow_site/` → корень этого репозитория
> - остальная история старой среды → `ops/archive/` (только справочно)
>
> Ниже — оригинальный handoff без изменений, кроме удалённого из текста токена.

1. Что это
- Проект: Telegram-канал SohoArchTimes + сайт-слайдшоу.
- Канал: https://t.me/SohoArchTimes
- Публичная лента: https://t.me/s/SohoArchTimes
- Публичный сайт: https://sl-himmelreich.github.io/sohoarchtimes-slideshow-site/
- Публичный slides.json: https://sl-himmelreich.github.io/sohoarchtimes-slideshow-site/slides.json
- GitHub repo сайта: sl-himmelreich/sohoarchtimes-slideshow-site
- Локальный repo сайта: /home/user/workspace/sohoarchtimes_slideshow_site

2. Главное постоянное правило
- Никаких автоматических обновлений.
- Никаких scheduled tasks.
- И публикации в канал, и обновления сайта запускать только по прямой команде пользователя.
- Сейчас активных scheduled tasks: 0.

3. Какие объекты искать
- Искать только built / completed projects.
- Искать только объекты площадью не менее 1 000 кв.м.
- Если площадь на странице проекта не указана и нельзя надёжно подтвердить порог 1 000 кв.м. по разрешённому источнику, объект пропускать.
- Приоритет тематики:
  - parametric architecture
  - computational design
  - digital fabrication
  - robotic fabrication
  - advanced material systems
  - responsive facades
  - computational envelopes
  - data-driven structures
- Не ограничиваться павильонами.
- Активно включать капитальные объекты: headquarters, музеи, культурные здания, кампусы, research centers, transport hubs, towers, high-rise, mid-rise, крупные общественные и mixed-use объекты.
- Публиковать только объекты, которые действительно относятся к параметрической архитектуре, вычислительному проектированию или цифровому производству.
- Если связь с этой парадигмой слабая или натянутая, объект пропускать.

4. Разрешённые источники поиска
- Только ArchDaily
- Только Parametric Architecture
- Никаких других источников для подбора объектов.

5. Правила отбора кандидата
- Объект должен быть построенным.
- Площадь должна проходить порог 1 000 кв.м.
- Должно быть ровно 5 надёжно скачиваемых качественных изображений.
- Если нет 5 качественных изображений, объект пропускать.
- Для ArchDaily предпочитать прямые images.adsttc.com large_jpg URL.
- Для Parametric Architecture предпочитать прямые wp-content/uploads URL.
- Если на одной семье страниц повторяются сбои, не долбить тот же путь, а брать другой объект.

6. Запрет на дубли
- Дубли абсолютно запрещены.
- Нельзя публиковать объект, если уже публиковались:
  - source_url
  - canonical_source_url
  - title
  - очевидный вариант того же названия
- Проверять не только точное совпадение, но и кросс-источниковые/вариативные дубли.
- Реестр публикаций:
  /home/user/workspace/cron_tracking/3f016dc2/published_objects.json

7. Публикация в Telegram
- Публиковать только через:
  /home/user/workspace/cron_tracking/3f016dc2/publish_album.py
- Не использовать Telegram connector.
- Runbook:
  /home/user/workspace/cron_tracking/3f016dc2/runbook.md
- Канал: @SohoArchTimes
- Bot: @ArchTimesBot
- Chat id: -1003823260493

8. Локально найденные доступы
- В publish_album.py найден Telegram bot token:
  [токен удалён из всех файлов — теперь существует только в env-переменной TELEGRAM_BOT_TOKEN]
- Chat id:
  -1003823260493
- Других явных паролей/ключей именно для SohoArchTimes в локальных файлах не найдено.
- GitHub PAT в локальных файлах не найден; для commit/push из Claude Code потребуется отдельная GitHub-авторизация в той среде.

9. Формат подписи
- Подпись только на русском.
- Без ссылки на источник.
- Без упоминания источника.
- Формат строго такой:
  - название
  - локация
  - архитектор
  - год реализации если известен
  - материалы если известны
  - краткое описание
- Материалы расписывать содержательно и конкретно.
- Не использовать пустые общие слова типа стекло, бетон, сталь, дерево как единственное описание.
- Если материалы на странице указаны слишком общо и без конкретики, строку Материалы лучше опустить.

10. Качество текста
- Качество текста должно быть на уровне хорошего поста V on Shenton.
- Перед публикацией подпись обязательно проверять на:
  - логическую консистентность
  - фактическую корректность
  - корректность описания конструкций и самого объекта
- Никаких выдумок.
- Никаких слабых формулировок.
- Если есть сомнение в факте, не писать его.

11. Что считается успешной публикацией
- После отправки обязательно проверить публичную видимость:
  - в https://t.me/s/SohoArchTimes
  - по прямому post URL
- Пост считается успешным только если он реально публично виден.
- Если пост не виден публично, считать публикацию неуспешной и брать следующий кандидат.
- Если задача на публикацию одного объекта, продолжать, пока не будет подтверждённо виден ровно 1 новый пост.

12. Текущее состояние публикаций
- Последний опубликованный post: 1181
- URL: https://t.me/SohoArchTimes/1181
- Объект: Tokyu Kabukicho Tower
- Этот пост был подтверждён как публичный grouped album ровно из 5 изображений.
- Автоматическая 12-часовая синхронизация для него была отменена по просьбе пользователя.
- Значит сайт не обновлялся автоматически по 1181.

13. Правила обновления сайта
- Сайт обновлять только вручную по прямой команде пользователя.
- Telegram public visibility — источник истины.
- Если пользователь удалил пост из публичного канала, этот пост должен исчезнуть с сайта.
- Если пост младше 12 часов, он не должен появляться на сайте.
- Если у публичного поста стало меньше изображений, сайт должен это повторить.
- На сайте не должно быть изображений, которых нет в Telegram.

14. Ручной workflow обновления сайта
- Сначала проверить публичную видимость нужного поста в:
  - https://t.me/s/SohoArchTimes
  - прямом post URL
- Если пост публичный и прошли 12 часов, запустить:
  python /home/user/workspace/build_sohoarchtimes_catalog.py
- Затем пересобрать:
  /home/user/workspace/sohoarchtimes_slideshow_site/slides.json
  из:
  /home/user/workspace/sohoarchtimes_site_data/slides_catalog.json
- Формат slides.json должен быть компактным и содержать поля:
  id, mid, idx, title, arch, year, loc, url, post, src
- Сортировка:
  newest first по message_id,
  внутри поста — по порядку изображений.
- Затем в /home/user/workspace/sohoarchtimes_slideshow_site:
  git status
  git add slides.json
  git commit -m "<короткое описание>"
  git push
- После push проверить:
  - живой сайт
  - публичный slides.json
- Если сайт показывает старую версию, подождать распространение и перепроверить.
- Задача завершена только когда живой сайт реально отдает актуальные данные.

15. Дополнительные правила сайта
- Не тянуть на сайт картинки, которых нет в Telegram.
- Не полагаться на случайный кэш как на источник истины.
- Если живой сайт или публичный slides.json ещё старые после push, проверять повторно до фактического обновления.

16. Последние важные публикации
- 1166 — Shenzhen Capital Plaza
- 1176 — Central Embassy
- 1181 — Tokyu Kabukicho Tower

17. Ключевые пути
- Publisher:
  /home/user/workspace/cron_tracking/3f016dc2/publish_album.py
- Registry:
  /home/user/workspace/cron_tracking/3f016dc2/published_objects.json
- Runbook:
  /home/user/workspace/cron_tracking/3f016dc2/runbook.md
- Site builder:
  /home/user/workspace/build_sohoarchtimes_catalog.py
- Site repo:
  /home/user/workspace/sohoarchtimes_slideshow_site
- Site data:
  /home/user/workspace/sohoarchtimes_site_data/slides_catalog.json

18. Минимальный промпт для нового окна Claude Code
- Работаем только с SohoArchTimes.
- Автоматические обновления запрещены; всё только вручную по моей команде.
- Искать только built projects от 1 000 кв.м. только на ArchDaily и Parametric Architecture.
- Приоритет: parametric / computational / digital fabrication / advanced envelope objects.
- Никаких дублей, включая варианты названий.
- Публикация только через local publish_album.py.
- Сайт обновлять только после ручной проверки Telegram и правила 12 часов.
