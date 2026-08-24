# SohoArchTimes slideshow fix — 2026-06-05

## Summary
The live slideshow showed black frames and appeared to repeat only a small
subset of projects. Both symptoms traced to a single root cause in the data
layer. Fixed by localizing all Telegram imagery into the repo and removing
every dead `cdn4.telesco.pe` link, while preserving complete coverage of all
64 currently-public posts.

## Root cause
- `slides.json` had 306 slides across exactly the required 64 message_ids, so
  object coverage was already complete (no objects were missing).
- 221 of those slides pointed at `cdn4.telesco.pe/file/<token>.jpg` URLs. Those
  tokens had **expired**, so the host now returns **HTTP 404** for them
  (verified live). This produced the black frames.
- These 221 broken slides belonged to **47 of the 64** posts (each post was
  entirely one host: 47 posts all-cdn4, 17 posts all-`images.adsttc.com`).
- `app.js` skips images that fail to load (`ensureSlideLoaded` -> `advance` ->
  skip). With 47/64 posts fully broken, only the **17** posts backed by working
  `images.adsttc.com` images ever rendered. That is why the show looked like it
  cycled a limited subset — not a shuffle/loop bug. The randomizer
  (`buildRandomizedSlides` shuffles all 64 object groups and flattens; `advance`
  reshuffles on wrap) was inspected and is correct; it was left unchanged so as
  not to break working behavior.

## Fix applied
- Re-fetched fresh imagery for **all 64** posts from the public Telegram web
  preview (`t.me/SohoArchTimes/<id>?embed=1&mode=tme`), which yielded exactly
  **306** images — a 1:1 match with the 306 existing slides, in order, per post.
- Downloaded the **221** cdn4-sourced images and committed them to the repo
  under `img/{mid}_{idx}.jpg` (~24 MB, 221 valid JPEGs, all verified > 1 KB and
  `image/jpeg`). Repointed those slides at relative `./img/{mid}_{idx}.jpg`
  paths and set `"src": "local_telegram"`.
- Left the **85** `images.adsttc.com` slides untouched — those are stable,
  high-res CloudFront URLs that return 206/`image/jpeg` (verified live) and are
  not on the dead host.
- This removes all runtime dependence on `cdn4.telesco.pe`; images are now
  served by the same static host (GitHub Pages; `.nojekyll` present).
- Updated `README.md` to reflect the new architecture and the correct
  306-slide / 64-post counts (it previously claimed 448/92).

## Files changed
- `slides.json` — 221 URLs repointed from cdn4 to local `./img/...`; `src`
  field updated to `local_telegram` for those entries.
- `img/` — **new**, 221 committed JPEGs (the localized Telegram images).
- `README.md` — counts and network-dependency notes corrected.
- `app.js` — **not changed** (logic verified sound; root cause was data).

## Verification (local + after push)
- Total slides: **306**
- Distinct message_ids: **64**, exactly matching the required list (verified
  set-equal, no missing, no extra).
- `cdn4.telesco.pe` URLs remaining: **0** (also `git grep` finds none in
  slides.json / app.js / index.html).
- Missing local image files referenced by slides.json: **0**.
- Served locally via `python3 -m http.server`; `slides.json` loads with 306
  entries; random sample of 10 local images returned HTTP 200 with valid JPEG
  bodies.

## Commit / push
- Commit: **b12e85af6a41deb804ff9cdd3750805730282fec** (`b12e85a`)
- Pushed: `050b475..b12e85a  main -> main` (origin/main).

## Caveats / notes
- The localized images are at Telegram **public-preview resolution** (the only
  resolution the public web preview exposes); typically ~700–800 px on the long
  edge. This is the same imagery the site already used for those posts — no
  quality regression versus before — but it is lower-res than the adsttc
  sources. If higher-res is ever desired, original sources would need to be
  located per post.
- The 85 `images.adsttc.com` slides remain external. They are currently stable,
  but if long-term zero external dependency is desired, they could be localized
  the same way in a follow-up.
- Because images are now committed to the repo, future channel updates require
  re-running the fetch/download step and committing new files rather than just
  refreshing URLs. The naming scheme `img/{mid}_{idx}.jpg` makes this
  deterministic.
- GitHub Pages must redeploy after the push for the live site to pick up the new
  `img/` assets and `slides.json`; allow the normal Pages build to complete.
