> Адаптация 2026-08-19: файл перенесён из старой среды в репозиторий сайта. Пути заменены на относительные (ops/...).
> Инструменты browser_task / fetch_url — из старой среды; в Claude Code использовать WebFetch или curl.
> Токен бота больше нигде не хранится в файлах — только env-переменная TELEGRAM_BOT_TOKEN.

# SohoArchTimes daily runbook

Goal: publish exactly 5 new architecture objects to Telegram channel @SohoArchTimes every day, each as an album of exactly 5 images, with no repeats.

Source restriction:
- Only public pages from ArchDaily (archdaily.com) and Parametric Architecture (parametric-architecture.com)

Hard rules:
- Never repeat an object if its source URL, canonical source URL, title, or obvious title variant appears in `ops/published_objects.json`.
- Every published object must be an album of exactly 5 images.
- If an object does not have 5 reliably downloadable high-quality images, skip it.
- Caption must be only in Russian and must not mention or link the source.
- Caption format: title, location, architect(s), year if known, materials if and only if specific enough, short description.
- Materials must be detailed and specific. Do not use primitive generic material labels alone. Keep product, supplier, and brand names untranslated.
- Post counts only if Telegram confirms a successful media group of 5 items and the post is publicly visible on https://t.me/s/SohoArchTimes.

Reliable workflow:
1. Read registry `ops/published_objects.json`.
2. Find candidate projects from source archive pages or article pages.
3. Use `browser_task` on the actual project page, not `fetch_url`, to extract:
   - title
   - source_url
   - canonical article URL if visible
   - location
   - architects
   - year if stated
   - detailed materials only if explicit
   - concise factual English summary
   - exactly 5 direct image URLs that are likely downloadable
4. For ArchDaily, prefer direct `images.adsttc.com/.../large_jpg/...` URLs.
5. For Parametric Architecture, prefer direct `https://parametric-architecture.com/wp-content/uploads/...` image URLs.
6. Convert extracted data into a small local JSON object file with fields:
   - title
   - slug
   - source_url
   - canonical_source_url
   - caption_ru
   - image_urls (exactly 5)
7. Publish each object with:
   - `python ops/publish_album.py /path/to/object.json`
8. After each successful publish, verify the direct post URL and the public channel page using `browser_task`.
9. If a candidate fails at image extraction, image download, Telegram sending, or public visibility, skip it and take the next one.
10. Continue until exactly 5 new visible posts are confirmed.

Important implementation notes:
- Direct Telegram connector album sending is not reliable enough here. Use direct Telegram Bot API through the helper script.
- The helper script already uses:
  - bot token for @ArchTimesBot
  - chat id `-1003823260493`
  - local multipart upload to `sendMediaGroup`
  - registry updates on success
  - publisher proof updates on success (`ops/publisher_proof.json`) — the site
    builder uses it to render original-resolution images (proven_high_res)
- If Telegram returns 429, the helper script waits and retries automatically.
- If you get repeated extraction failures from a source, switch sources instead of retrying the same page family.

Current registry path:
- `ops/published_objects.json`

Current helper script:
- `ops/publish_album.py`
