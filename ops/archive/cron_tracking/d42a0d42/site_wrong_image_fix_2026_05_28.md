# Wrong Image Fix for mid 406 — 2026-05-28

## Problem
The public slideshow site displayed a **non-architectural fashion photograph** (Harper's Bazaar fashion shoot) for Telegram post https://t.me/SohoArchTimes/406 (Metropol Parasol, Seville). The image showed a model in a white coat posing inside the structure — not an architectural photograph.

## Root Cause
**Data source:** `slides.json` (manually curated, no build pipeline — committed directly as a static file).

**Offending URL:** `https://jmayerh.de/files/2020/05/01-shop-harpersbazaar-com-feb-2019-walking-on-sunshine-sev-beige006.jpg`

**How it was introduced:** Commit `527ce38` (2026-05-16, "replace slideshow previews with full-size source images") upgraded Telegram CDN URLs to source-quality images from jmayerh.de (the architect's website). The fashion image was on the same jmayerh.de domain as the legitimate architectural photos, so it was picked up during the upgrade. It was then carried forward through subsequent whole-file rewrites (`bd60c8b`, `af01dca`, `0551d69`) and finally committed with distinct filenames in `2b665c3` (2026-05-28) as `proven_high_res`.

**Why it wasn't caught:** The image is hosted on the architect's own domain (jmayerh.de), making it appear legitimate. The filename contains "harpersbazaar" but this was not flagged during data curation.

## Fix Applied
- **Removed** slide entry `406-1` containing the fashion image URL
- **Re-indexed** remaining 4 slides from `406-1` through `406-4` (previously `406-2` through `406-5`)
- All 4 remaining images are legitimate architectural photographs of the Metropol Parasol:
  1. `parasoles-fernandoalda-30-66.jpg` — street-level view
  2. `parasol-franck0866.jpg` — interior underside view
  3. `parasoles-fernandoalda-22-m-2-2560x1707.jpg` — aerial view
  4. `huftoncrow-metropol-parasol-35-2560x2389.jpg` — exterior plaza view

## No-Upscale Behavior
**Preserved.** The no-upscale/native-size clamping is implemented in:
- `app.js:160-166` — `clampToNatural()` sets `maxWidth`/`maxHeight` to `naturalWidth`/`naturalHeight`
- `styles.css:67-69` — `max-width: 100%; object-fit: contain`

These are CSS/JS logic, untouched by the `slides.json` data fix.

## Deployment
- **Commit:** `5201012` on `main` branch
- **Pushed** to `origin/main` — no CI/CD pipeline; GitHub Pages serves directly from `main`
- GitHub Pages CDN cache may take a few minutes to propagate

## Verification
- Local `slides.json`: confirmed **0 matches** for `harpersbazaar`, `walking-on-sunshine`, `beige006`
- Mid 406 now has **4 slides** (down from 5), all architectural, properly indexed 1-4
- Total slide count: **334** (down from 335)
- JSON validity: confirmed via `json.load()`

## Files Changed
- `slides.json` — removed 1 slide entry (12 lines removed, re-indexed 4 entries)
