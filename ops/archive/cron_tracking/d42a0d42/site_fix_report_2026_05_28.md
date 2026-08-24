# SohoArchTimes Slideshow Site Fix Report — 2026-05-28

## Problem Summary
1. Live GitHub Pages site loading stale `app.js?v=20260518-early-preload-buffer`, missing no-upscale clamp logic
2. 230 slides using `cdn4.telesco.pe` URLs blocked by browser ORB (and also 404 from server)
3. Images were being stretched/upscaled above their natural resolution
4. 105 `url_fallback` entries pointed to dead telesco.pe URLs

## Changes Made

### Files Modified
| File | Change |
|------|--------|
| `slides.json` | Replaced 230 telesco.pe primary URLs with working source URLs (adsttc.com, parametric-architecture.com, etc.). Removed 105 dead telesco.pe `url_fallback` entries. Updated `build_version` to `20260528T080000`. |
| `app.js` | Added stale-clamp clearing: resets `maxWidth`/`maxHeight` on front layer before loading new slide, preventing previous image's clamp from constraining next image during load. No-upscale `clampToNatural()` logic was already present. |
| `index.html` | Updated script tag from `app.js?v=20260526-no-upscale` to `app.js?v=20260528-source-urls` to bust browser cache. |

### Files Added
| File | Purpose |
|------|---------|
| `.nojekyll` | Ensures GitHub Pages serves files directly without Jekyll processing. |

## Image Migration Details
- **230 slides** had their primary URL changed from `cdn4.telesco.pe` to original source URLs
- **105 slides** had dead `url_fallback` (telesco.pe) entries removed
- All 335 slides now have `src: "proven_high_res"`
- Source URLs retrieved from `recovered_source_payloads.json` (225 slides) and parametric-architecture.com scraping (5 slides for mid=911)

### Final URL Domain Breakdown
| Domain | Slide Count |
|--------|-------------|
| images.adsttc.com | 255 |
| parametric-architecture.com | 60 |
| a.storyblok.com | 10 |
| jmayerh.de | 5 |
| s3.amazonaws.com | 5 |
| **Total** | **335** |

## Validation Results
- Slide count: **335** (unchanged)
- Post count: **69** (unchanged)
- telesco.pe references in `url`: **0** (was 230)
- telesco.pe references in `url_fallback`: **0** (was 105)
- URL accessibility spot check: **35/35 passed** (15 across all domains + 20 random replacements)
- All slides have required fields (id, mid, idx, title, url)
- No empty URLs

## No-Upscale Implementation
- `clampToNatural(el)` sets `el.style.maxWidth` and `el.style.maxHeight` to `naturalWidth`/`naturalHeight` pixels
- Called after every image load in `runCurrent()`, before fade-in
- Stale clamp values cleared at start of each slide cycle
- CSS `object-fit: contain` preserves aspect ratio within clamped bounds

## How to Publish
1. Commit all changes to `main` branch
2. Push to GitHub: `git push origin main`
3. GitHub Pages will automatically deploy
4. Verify the live site loads `app.js?v=20260528-source-urls` (check DevTools Network tab)

## Remaining Risks
- **External CDN dependency**: All 335 slides still rely on external CDNs (adsttc.com, parametric-architecture.com, etc.). If any CDN blocks requests in the future, those slides will be skipped. The slideshow gracefully handles this (skips broken slides, retries after MAX_SKIPS).
- **No local image mirroring**: Images are not hosted in the repo. Full local mirroring would require downloading ~335 high-res images (potentially 500MB+), which may exceed GitHub Pages limits. The current approach uses proven, working source URLs.
- **adsttc.com hotlink policy**: Some adsttc.com URLs may eventually enforce referrer checks. The existing 100+ proven_high_res slides from adsttc.com have been working reliably.
