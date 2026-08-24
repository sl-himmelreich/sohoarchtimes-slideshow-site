# SOHO Calendar Assistant (Telegram → Google Календарь)

Личный ассистент владельца: раз в сутки в 21:00 МСК забирает новые сообщения
из личного чата с @ArchTimesBot, превращает русский свободный текст в события
Google Календаря и присылает подтверждение в Telegram. Перенос работавшей
системы (142 запуска, 194 события). К публикациям канала SohoArchTimes и к
сайту отношения НЕ имеет и не касается их.

## Архитектура

**Постоянная система — GitHub Actions, полностью без Claude-сессий:**
`.github/workflows/calendar-assistant.yml`, cron ежедневно 18:00 UTC
(= 21:00 Europe/Moscow; у Москвы нет сезонного перевода часов) + ручной
запуск кнопкой Run workflow.

Конвейер (`run_assistant.py`):
1. `tg_pipeline.fetch_data()` — getWebhookInfo/deleteWebhook, getUpdates БЕЗ
   offset (timeout=0, limit=100), фильтр: только личный чат владельца,
   только текст, без команд «/», последняя редакция каждого message_id.
2. Разбор текста в события — `claude_parser.py` (Claude API, модель
   claude-opus-5, системный промпт — дословно PARSING_RULES.md; вызывается
   только при наличии новых сообщений). Нет ключа или сбой — аварийный
   fallback `ru_parser.py` (детерминированные правила, всё сомнительное → ⚠️).
3. Дубликаты — `gcal.py.has_duplicate`: события той же даты с тем же/почти
   тем же названием пропускаются.
4. Создание — Google Calendar API от сервисного аккаунта (scope
   calendar.events), календарь владельца, timeZone Europe/Moscow, повторы —
   recurrence/RRULE.
5. Подтверждения ✅/⚠️ владельцу — sendMessage (форматы в PARSING_RULES.md).
   Пустой запуск — полная тишина.
6. Подтверждение offset — СТРОГО в конце и только при безошибочном запуске;
   любая ошибка валит запуск без confirm, сообщения приходят повторно завтра.

Состояние живёт на стороне Telegram (offset); файлов состояния нет.

**Секреты** — только в GitHub Actions secrets (репозиторий публичный, в коде
секретов нет): `TELEGRAM_BOT_TOKEN`, `GOOGLE_SA_KEY`, `GCAL_CALENDAR_ID`,
опционально `ANTHROPIC_API_KEY`. Настройка — ops/tg_gcal/SETUP.md. Пока
секреты не добавлены, запуски Actions тихо пропускаются.

**Временный мост** — Routine «SOHO Calendar Assistant — мост 21:10 МСК» в
постоянной Claude-сессии: обрабатывает очередь, пока Actions не настроен
(сообщения живут в Telegram ~сутки и иначе протухли бы), и сам удаляет себя
после первого успешного запуска Actions. Протокол — ops/tg_gcal/ROUTINE.md.
Мост установлен по прямому указанию владельца (24.08.2026) и является
единственным разрешённым исключением из правила «никакой автоматики»
CLAUDE.md (сам Actions-workflow автоматикой Claude не является — он не
запускает Claude-сессий; расписаний в других workflow это не разрешает).

## Файлы
- `tg_pipeline.py` — механика Bot API: fetch / send / confirm (библиотека + CLI).
- `run_assistant.py` — автономный конвейер для GitHub Actions.
- `claude_parser.py` — основной разбор (Claude API), `ru_parser.py` —
  аварийный fallback, `tests_ru_parser.py` — его тесты.
- `gcal.py` — Google Calendar через сервисный аккаунт.
- `PARSING_RULES.md` — правила «текст → события» и форматы подтверждений
  (не менять без прямого указания владельца).
- `SETUP.md` — какие секреты добавить владельцу (один раз, ≈5 минут).
- `ROUTINE.md` — протокол временного моста.

## Управление
- Выключить всё: удалить/выключить workflow **Calendar Assistant** (GitHub →
  Actions → Calendar Assistant → ⋯ → Disable workflow) — и, если мост ещё
  жив, сказать Claude «выключи календарный ассистент» (удалит Routine).
- Ручной запуск: GitHub → Actions → Calendar Assistant → Run workflow.
- Лог постоянной системы: история запусков в GitHub Actions (что пришло,
  что создано, что отправлено — без секретов). Лог моста — сессия
  «SOHO Calendar Assistant — операционная сессия» в claude.ai/code.
