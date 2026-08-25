# SOHO Calendar Assistant — как включить автономный режим (без Claude)

Система уже работает через временный мост. Чтобы она стала полностью
автономной и бесплатной, есть два равнозначных варианта. **Рекомендуется
вариант А** — он не заходит в Google Cloud Console и потому не требует
включённой двухфакторки (с 09.04.2026 Google пускает в Cloud Console только
с MFA; Apps Script этой блокировке не подчиняется).

## Вариант А (рекомендуется): Google Apps Script — 4 действия

1. Открыть https://script.google.com/create (войдя в аккаунт календаря).
2. Стереть заглушку и вставить целиком файл
   [`ops/tg_gcal/apps_script/Code.gs`](https://raw.githubusercontent.com/sl-himmelreich/sohoarchtimes-slideshow-site/main/ops/tg_gcal/apps_script/Code.gs)
   (открыть ссылку → Ctrl+A → Ctrl+C → вставить в редактор).
3. В строке `TELEGRAM_BOT_TOKEN = '…'` вставить токен бота между кавычек.
4. Сохранить (Ctrl+S), выбрать в списке функций `setup`, нажать **Run**
   и разрешить доступ (Allow).

Всё: скрипт сразу разберёт накопившиеся сообщения, пришлёт ✅ в Telegram и
поставит себе ежедневный триггер ~21:00 МСК. Работает на серверах Google,
бесплатно, без ключей и без Claude. Мост в Claude отключится сам, как только
увидит в календаре событие с меткой планировщика.

- Выключить всё: в том же редакторе запустить функцию `disable`
  (или удалить проект скрипта).
- Лог: script.google.com → проект → «Выполнения» (Executions).
- Токен хранится только внутри вашего частного скрипта (никому не виден).
- Необязательно: в строку `ANTHROPIC_API_KEY` можно вставить ключ с
  https://console.anthropic.com — тогда разбор текста делает Claude API;
  без ключа работает встроенный парсер.

## Вариант Б (альтернатива): GitHub Actions + сервисный аккаунт Google

Требует зайти в Google Cloud Console — а туда с 09.04.2026 пускают только
с включённой двухфакторкой (кнопка «Enable MFA» на экране блокировки).
Если MFA включать не хотите — используйте вариант А.

1. Сервисный аккаунт: https://console.cloud.google.com/projectcreate →
   создать проект → включить
   https://console.cloud.google.com/apis/library/calendar-json.googleapis.com →
   https://console.cloud.google.com/iam-admin/serviceaccounts → Create service
   account (роли не нужны) → Manage keys → Add key → JSON (скачается файл) →
   в настройках календаря (calendar.google.com) расшарить основной календарь
   на email сервисного аккаунта с правом «Внесение изменений в мероприятия».
2. Секреты: https://github.com/sl-himmelreich/sohoarchtimes-slideshow-site/settings/secrets/actions →
   `TELEGRAM_BOT_TOKEN` (токен бота), `GOOGLE_SA_KEY` (всё содержимое
   скачанного JSON), `GCAL_CALENDAR_ID` (gmail-адрес аккаунта календаря),
   опционально `ANTHROPIC_API_KEY`.
3. Проверка: Actions → Calendar Assistant → Run workflow.

Пока не включён ни один из вариантов, ежедневные запуски Actions тихо
пропускаются, а обработку в 21:10 МСК выполняет временный мост.
