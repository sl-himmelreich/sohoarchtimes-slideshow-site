# SohoArchTimes Telegram-faithful slideshow fix — report

Build version: 20260525T180915
Image policy: telegram_faithful_v2

## Root cause
`build_sohoarchtimes_catalog.py / merge_records()` previously preferred
`telegram_full_image_urls` (bot-API file URLs that EXPIRE) then
`source_image_urls` (original-publisher images, NOT in Telegram), and only fell
back to `telegram_preview_images`. Result: 68 of 69 rendered posts were showing
source images that do not exist in the Telegram channel, and the 1 telegram_full
post was serving already-expired `api.telegram.org/file/bot...` URLs.

## Fix
1. New helper `_sanitize_telegram_image_urls()` strips any
   `api.telegram.org/file/bot...` URLs (expiring) and accepts only URLs that
   start with http(s).
2. `merge_records()` now uses this strict order:
   - `telegram_preview_images` (public-channel scrape from t.me/s/SohoArchTimes,
     `cdn*.telesco.pe` / `cdn-telegram.org`) — primary source of truth.
   - Stable `telegram_full_images` (only if they happen to be telesco.pe URLs).
   - Otherwise the post is HIDDEN (`hidden_no_telegram_images`) — we never
     render `source_image_urls`.
3. `source_image_urls` is retained in `posts_catalog.json` for archival/debug
   purposes only; it is excluded from `slides_catalog.json`'s `image_url` and
   therefore from the public site.
4. Build emits a `build_version` (UTC-style timestamp) into:
   - `sohoarchtimes_site_data/stats.json`
   - `sohoarchtimes_site_data/build_version.txt`
   - the envelope of the compact `sohoarchtimes_slideshow_site/slides.json`
     (`{build_version, image_policy, total, slides:[...]}`)
5. `app.js / loadSlidesJson()`:
   - Now fetches `./slides.json?cb=<ts>` with `cache:'no-store'` so a stale JSON
     can never be served by a CDN/browser cache.
   - Accepts both the legacy flat array and the new versioned envelope.
   - `applyBuildVersion()` appends `?v=<build_version>` to every image URL so
     when the data is rebuilt the browser reloads imagery instead of serving a
     stale CDN copy.
6. `build_sohoarchtimes_catalog.py` now writes the compact
   `sohoarchtimes_slideshow_site/slides.json` itself, so every future rebuild
   keeps catalog and site in lock-step automatically.

## Telegram-faithful strategy chosen
The public Telegram preview at `https://t.me/s/SohoArchTimes` serves stable
`https://cdn4.telesco.pe/file/...jpg` URLs (verified: HTTP 200, image/jpeg). We
treat these as the canonical render source. They are exactly what visitors of
the public Telegram channel see, they do not expire on the Bot-API rotation
schedule, and they update whenever Telegram preview pagination is re-fetched.
The bot-API `api.telegram.org/file/bot...` URLs are explicitly blocked because
they rotate / expire.

## Result
- merged_posts_with_images: 69
- total_slides: 335
- telegram_preview_posts: 69
- telegram_full_stable_posts: 0
- source_full_posts_rendered: 0  (was 68 before fix)
- posts_hidden_no_telegram_images: 0
- pending_grace_posts (12-h delay): [946]
- 8 random slide URLs HEAD-checked: 8/8 returned HTTP 200 image/jpeg

## Files changed
- /home/user/workspace/build_sohoarchtimes_catalog.py (merge logic, build_version, writes site slides.json)
- /home/user/workspace/sohoarchtimes_slideshow_site/app.js (versioned envelope + cache-bust)
- /home/user/workspace/sohoarchtimes_slideshow_site/slides.json (regenerated, 335 slides, all telesco.pe)
- /home/user/workspace/sohoarchtimes_site_data/{slides_catalog,posts_catalog,stats,public_posts_raw,local_payload_posts,build_version.txt}.json (regenerated)

## Remaining risks
- `cdn4.telesco.pe` is a Telegram-operated CDN; if Telegram ever rotates these
  URLs, a fresh rebuild will pull the latest URLs from the public channel, so
  the cron that periodically reruns `build_sohoarchtimes_catalog.py` keeps the
  site in sync automatically.
- Three older posts (mids 396, 431, 746) only had 2-3 photos surfaced by the
  public scrape rather than 5; the site now shows exactly what the channel
  exposes (Telegram-faithful). If the user wants 5 per post for those, the
  preview-page scraper would need to follow per-photo `?single` permalinks.
- One post (mid 946) is within the 12-hour grace window and is correctly
  withheld until the review window elapses.
