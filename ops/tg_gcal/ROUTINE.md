# Временный мост — Routine «SOHO Calendar Assistant — мост 21:10 МСК»

Постоянная система — GitHub Actions
(.github/workflows/calendar-assistant.yml, ежедневно 21:00 МСК, без
Claude-сессий). Мост выполняется в постоянной операционной Claude-сессии
и нужен ТОЛЬКО до тех пор, пока владелец не настроил секреты Actions
(ops/tg_gcal/SETUP.md): он подхватывает сообщения, чтобы они не протухли
в Telegram (~сутки), и самоликвидируется, когда Actions заработал.

Этот файл — операционная инструкция каждого запуска моста. При изменении —
синхронизировать с промптом Routine (update_trigger), и наоборот.

## Шаг 0 — передача дел GitHub Actions
Через GitHub MCP: `actions_list` → `list_workflow_runs` для
`calendar-assistant.yml` (последние ~5 завершённых). Если в каком-то запуске
шаг **«Run assistant»** завершился `success` (`list_workflow_jobs` → steps) —
Actions настроен и работает: удалить Routine моста (`list_triggers` →
`delete_trigger` по имени «SOHO Calendar Assistant — мост 21:10 МСК») и
закончить, не трогая Telegram. Запуски, где этот шаг `skipped`, означают
«секреты ещё не настроены» — мост продолжает работать.

## Шаги 1–7 — обработка (строго, из корня репозитория)
1. `python3 ops/tg_gcal/tg_pipeline.py fetch`
2. Если `messages` пуст: при `updates_total > 0` и безошибочном шаге 1
   выполнить `python3 ops/tg_gcal/tg_pipeline.py confirm --offset
   <max_update_id+1>`; закончить молча (пустой запуск — полная тишина,
   в Telegram ничего не отправлять).
3. Иначе прочитать ops/tg_gcal/PARSING_RULES.md и разобрать каждый text в
   события СТРОГО по правилам. База относительных дат — date_msk каждого
   сообщения, НЕ момент запуска.
4. Для каждого события — проверка дубля: Google Calendar MCP list_events на
   дату события (календарь primary); то же/почти то же название → пропустить
   (в Telegram об этом не сообщать).
5. Создать события: Google Calendar MCP create_event, календарь primary,
   timeZone Europe/Moscow, description по правилам, повторы — recurrenceData
   (RRULE).
6. Отправить подтверждения по форматам из правил:
   `python3 ops/tg_gcal/tg_pipeline.py send --text '…'`
   (⚠️-строку — на каждое нераспознанное сообщение).
7. ТОЛЬКО если ВЕСЬ запуск прошёл без единой ошибки:
   `python3 ops/tg_gcal/tg_pipeline.py confirm --offset <max_update_id+1>`.
   При любой ошибке offset НЕ подтверждать (сообщения придут повторно в
   следующий запуск) и закончить, коротко зафиксировав причину в сессии.

## Запреты
Канал SohoArchTimes, сайт, публикации и ops/published_objects.json не трогать
ни при каких условиях. Ничего не коммитить и не пушить. Владельцу писать
только в Telegram через скрипт и только по форматам из правил; вопросов ему
не задавать. Если TELEGRAM_BOT_TOKEN отсутствует или Google Calendar MCP
недоступен — это ошибка: остановиться без confirm.
