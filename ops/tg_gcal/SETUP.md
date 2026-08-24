# SOHO Calendar Assistant — настройка секретов (≈5 минут, один раз)

Система уже развёрнута и работает через временный мост. Чтобы она стала
полностью автономной (GitHub Actions, без Claude-сессий), нужны секреты,
которые может добавить только владелец репозитория.

## Шаг 1. Сервисный аккаунт Google (доступ к календарю без браузера)

1. Открыть https://console.cloud.google.com/projectcreate — создать проект
   (имя любое, например `tg-gcal`), войдя в нужный Google-аккаунт.
2. Открыть https://console.cloud.google.com/apis/library/calendar-json.googleapis.com
   — нажать **Enable** (в этом проекте).
3. Открыть https://console.cloud.google.com/iam-admin/serviceaccounts —
   **Create service account**, имя `tg-gcal-bot`, роли не нужны → **Done**.
4. В списке аккаунтов: ⋮ → **Manage keys** → **Add key** → **Create new key**
   → **JSON** → скачается файл ключа.
5. Скопировать email сервисного аккаунта (вида
   `tg-gcal-bot@…iam.gserviceaccount.com`).
6. Открыть https://calendar.google.com → настройки основного календаря →
   **Доступ для отдельных пользователей** → добавить этот email с правом
   **«Внесение изменений в мероприятия»**.

## Шаг 2. Секреты репозитория

Открыть
https://github.com/sl-himmelreich/sohoarchtimes-slideshow-site/settings/secrets/actions
и создать (New repository secret):

| Имя | Значение |
| --- | --- |
| `TELEGRAM_BOT_TOKEN` | токен бота @ArchTimesBot |
| `GOOGLE_SA_KEY` | полное содержимое скачанного JSON-файла ключа |
| `GCAL_CALENDAR_ID` | gmail-адрес аккаунта, чей календарь ведём (id основного календаря) |
| `ANTHROPIC_API_KEY` | *необязательно*: ключ с https://console.anthropic.com — тогда разбор текста делает Claude API; без ключа работает встроенный парсер |

## Шаг 3. Проверка (по желанию)

Actions → **Calendar Assistant** → **Run workflow**. Успешный запуск создаст
события из накопившихся сообщений и пришлёт ✅ в Telegram (если очередь пуста —
завершится тихо). Дальше всё срабатывает само ежедневно в 21:00 МСК; временный
мост в Claude отключится автоматически после первого успешного запуска.

Пока секреты не добавлены, ежедневные запуски Actions тихо пропускаются
(без ошибок), а обработку выполняет временный мост.
