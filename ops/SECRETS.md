# Где лежат ключи и доступы (карта, без самих секретов)

Секреты в этом публичном репозитории не хранятся. Резервная копия — в
приватной папке на Google Drive владельца; управление идёт через Claude
(коннектор Google Drive). В рабочей сессии ключи лежат в `.secrets/`
(под .gitignore, в git не попадают).

## Источник истины: Google Drive
- Папка: **SohoArchTimes-Secrets**
  https://drive.google.com/drive/folders/1LvYLQOC6iOcFJL_QoU-JXgJnmXQAvYmq
- Файлы:
  - `yc_sa_key.json` — авторизованный ключ сервисного аккаунта Yandex Cloud
    (SA `ajeoog1i1k5di9467kj8`, каталог `b1gb3dbv6atsou7hqe62`). Главный доступ.
  - `soho_vm_ed25519` — приватный SSH-ключ к VM `soho-ai` (111.88.252.7,
    пользователь `soho-deployer`).
  - `credentials.env` — Hoster.Ru, GitHub-токен кнопки ⟳, ArchDaily, реквизиты
    YC, id инфраструктуры (бакет/CDN/сертификат).
  - `README.md` — та же карта плюс процедура восстановления.
  - S3-ключ бакета отдельно НЕ хранится: генерируется из `yc_sa_key.json`
    по требованию (IAM aws-compatibility accessKeys).

## Как восстановить в новой сессии (для Claude)
1. Google Drive → `search_files` по `title = 'SohoArchTimes-Secrets'` → взять
   fileId нужных файлов (`read_file_content`).
2. Разложить в `.secrets/` рабочей сессии (папка уже в .gitignore).
3. IAM-токен: JWT (PS256, kid = key id) → POST
   `https://iam.api.cloud.yandex.net/iam/v1/tokens`; далее управление
   бакетом `soho-archtimes-site`, CDN `bc8ru4nyb63phwwwkcbx`, сертификатом
   `fpqm81dspf0apj7tf40a`.
4. S3-ключ для заливки в бакет — создать при необходимости через
   IAM `accessKeys` от SA, затем boto3 к `https://storage.yandexcloud.net`.
5. DNS-правки — панель Hoster.Ru (логин/пароль в credentials.env),
   зона `sohoai.ru`, endpoint `/control/domains/sohoai.ru/dns/save`.

## Безопасность
- Никогда не коммитить содержимое `.secrets/` и значения ключей в этот
  публичный репозиторий. При утечке ключа — отозвать, заменить, обновить
  файлы в папке на Drive.
