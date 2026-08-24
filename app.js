/* SohoArchTimes — Slideshow engine
   - Loops slides forever
   - ALL slides are shuffled into a fresh random order on every page load
     and reshuffled again after each full pass
   - 30s hold per slide, then a 3s CROSSFADE: the next image fades in ON TOP
     of the current one — the current slide never disappears (and the screen
     never goes black) until the next has fully faded in
   - Preloads next image; skips broken images automatically while keeping
     the current image on screen
   - Resilient to slow loads; never leaves a blank white screen
*/

(() => {
  'use strict';

  // ---- Timing (ms) ---------------------------------------------------------
  const FADE_MS  = 3000;        // crossfade duration in normal auto-play
  const MANUAL_FADE_MS = 450;   // snappier crossfade for prev/next buttons
  const HOLD_MS  = 30_000;
  const LOAD_TIMEOUT_MS = 25_000;               // give a slow image this long to load
  const CONTROLS_IDLE_MS = 2500;                // hide controls after idle
  const PRELOAD_LOOKAHEAD = 3;                  // warm the next few slide images immediately
  const IMAGE_CACHE_LIMIT = 24;                 // keep only a modest hot cache in memory

  // ---- DOM -----------------------------------------------------------------
  const $ = (id) => document.getElementById(id);
  const stage   = $('stage');
  const frame   = $('frame');
  const imgA    = $('imgA');
  const imgB    = $('imgB');
  const loader  = $('loader');
  const caption = $('caption');
  const capTitle = $('capTitle');
  const capArch  = $('capArch');
  const capYear  = $('capYear');
  const capLoc   = $('capLoc');
  const hud      = $('hud');
  const hudCount = $('hudCount');
  const controls = $('controls');
  const hint     = $('hint');

  // ---- State ---------------------------------------------------------------
  let slides = [];
  let allSlides = [];      // canonical slide list; `slides` is its shuffled view
  let idx = 0;             // current index into slides[]
  // Defensive: ensure neither image layer is hidden via the HTML `hidden`
  // attribute. If it is, the element becomes display:none and the swap
  // mechanism would show a blank black stage after the first preload swap.
  if (imgA) imgA.hidden = false;
  if (imgB) imgB.hidden = false;
  let frontEl = imgA;      // currently visible <img>
  let backEl  = imgB;      // preloading <img>
  let isPaused = false;
  let timer = null;        // setTimeout handle for the next phase
  let phase = 'idle';      // 'hold' | 'transition' | 'idle'
  let phaseStart = 0;
  let phaseDur = 0;
  let phaseRemainAtPause = 0;
  let consecutiveSkips = 0;
  let transitionGeneration = 0;  // cancels stale async transitions/preloads
  const warmCache = new Map();
  const MAX_SKIPS = 12;    // safety: avoid infinite skip loops

  // ---- Helpers -------------------------------------------------------------
  const setText = (el, v) => { el.textContent = (v == null ? '' : String(v).trim()); };

  function formatCaption(s) {
    setText(capTitle, s.title);
    setText(capArch,  s.arch);
    setText(capYear,  s.year);
    setText(capLoc,   s.loc);
  }

  function updateHud() {
    if (!slides.length || idx < 0) { setText(hudCount, ''); return; }
    const n = String(idx + 1).padStart(3, '0');
    const N = String(slides.length).padStart(3, '0');
    setText(hudCount, `${n} / ${N}`);
  }

  function updateLetterboxLayout() {
    if (!frame) return;
    const frameStyle = getComputedStyle(frame);
    const bandPad = parseFloat(frameStyle.getPropertyValue('--letterbox-pad')) || 10;
    const captionHeight = Math.ceil(caption.getBoundingClientRect().height || 0);
    const hudVisible = getComputedStyle(hud).display !== 'none';
    const hudHeight = hudVisible ? Math.ceil(hud.getBoundingClientRect().height || 0) : 0;
    const requiredBand = Math.max(24, captionHeight + bandPad * 2, hudHeight ? hudHeight + bandPad * 2 : 0);
    const captionBottom = Math.max(bandPad, Math.round((requiredBand - captionHeight) / 2));
    const hudBottom = hudVisible ? Math.max(bandPad, Math.round((requiredBand - hudHeight) / 2)) : bandPad;
    frame.style.setProperty('--letterbox-band', `${requiredBand}px`);
    frame.style.setProperty('--caption-bottom', `${captionBottom}px`);
    frame.style.setProperty('--hud-bottom', `${hudBottom}px`);
  }

  function clearTimers() {
    if (timer) { clearTimeout(timer); timer = null; }
  }

  function randomInt(maxExclusive) {
    if (maxExclusive <= 0) return 0;
    if (window.crypto && typeof window.crypto.getRandomValues === 'function') {
      const arr = new Uint32Array(1);
      window.crypto.getRandomValues(arr);
      return arr[0] % maxExclusive;
    }
    return Math.floor(Math.random() * maxExclusive);
  }

  function shuffleArray(arr) {
    const copy = arr.slice();
    for (let i = copy.length - 1; i > 0; i--) {
      const j = randomInt(i + 1);
      [copy[i], copy[j]] = [copy[j], copy[i]];
    }
    return copy;
  }

  function buildRandomizedSlides() {
    return shuffleArray(allSlides);
  }

  /** Raise `el` above its sibling layer: incoming slides fade in on top. */
  function setTop(el) {
    imgA.toggleAttribute('data-top', el === imgA);
    imgB.toggleAttribute('data-top', el === imgB);
  }

  /** Override the CSS crossfade duration for this element's next fade. */
  function setImgFadeDuration(el, ms) {
    el.style.transitionDuration = `${ms}ms`;
  }

  /** Show/hide with no animation (used for layers hidden beneath the top one). */
  function showImageInstant(el, visible) {
    const prev = el.style.transitionDuration;
    el.style.transitionDuration = '0ms';
    void el.offsetWidth;
    showImage(el, visible);
    void el.offsetWidth;
    el.style.transitionDuration = prev || '';
  }

  /** Prevent upscaling: clamp element to its natural pixel dimensions */
  function clampToNatural(el) {
    if (el.naturalWidth) {
      el.style.maxWidth  = el.naturalWidth  + 'px';
      el.style.maxHeight = el.naturalHeight + 'px';
    }
  }

  function showImage(el, visible) {
    if (visible) el.setAttribute('data-state', 'visible');
    else         el.removeAttribute('data-state');
  }

  function setLoading(on) {
    if (on) loader.setAttribute('data-state', 'on');
    else    loader.removeAttribute('data-state');
  }

  function showCaption(on) {
    caption.setAttribute('data-state', on ? 'in' : '');
    hud.setAttribute('data-state',     on ? 'in' : '');
  }

  function trimWarmCache() {
    while (warmCache.size > IMAGE_CACHE_LIMIT) {
      const oldestKey = warmCache.keys().next().value;
      if (oldestKey == null) break;
      warmCache.delete(oldestKey);
    }
  }

  function isElementReady(el, url) {
    if (!el || !url) return false;
    const current = el.currentSrc || el.src || '';
    return current === url && el.complete && el.naturalWidth > 0;
  }

  function warmImage(url) {
    if (!url) return Promise.resolve(false);
    const existing = warmCache.get(url);
    if (existing) {
      warmCache.delete(url);
      warmCache.set(url, existing);
      if (existing.status === 'loaded') return Promise.resolve(true);
      if (existing.status === 'error') return Promise.resolve(false);
      return existing.promise;
    }

    const img = new Image();
    img.decoding = 'async';
    try { img.fetchPriority = 'high'; } catch (_) {}

    const record = { status: 'loading', img, promise: null };
    const promise = new Promise((resolve) => {
      let settled = false;
      const cleanup = () => {
        img.onload = null;
        img.onerror = null;
        clearTimeout(timeoutId);
      };
      const finish = (ok) => {
        if (settled) return;
        settled = true;
        record.status = ok ? 'loaded' : 'error';
        cleanup();
        resolve(ok);
      };
      const timeoutId = setTimeout(() => finish(false), LOAD_TIMEOUT_MS);
      img.onload = async () => {
        try {
          if (typeof img.decode === 'function') await img.decode();
        } catch (_) {}
        finish(true);
      };
      img.onerror = () => finish(false);
    });

    record.promise = promise;
    warmCache.set(url, record);
    trimWarmCache();
    img.src = url;
    return promise;
  }

  function loadIntoElement(el, url) {
    return new Promise((resolve) => {
      if (!url) { resolve(false); return; }
      if (isElementReady(el, url)) { resolve(true); return; }

      let settled = false;
      const cleanup = () => {
        el.onload = null;
        el.onerror = null;
        clearTimeout(timeoutId);
      };
      const finish = (ok) => {
        if (settled) return;
        settled = true;
        cleanup();
        resolve(ok && el.naturalWidth > 0);
      };
      const timeoutId = setTimeout(() => finish(isElementReady(el, url)), LOAD_TIMEOUT_MS);

      el.onload = () => finish(true);
      el.onerror = () => finish(false);
      if ((el.currentSrc || el.src || '') !== url) el.src = url;
      if (isElementReady(el, url)) finish(true);
    });
  }

  async function ensureLayerReady(el, url) {
    const warmed = await warmImage(url);
    if (!warmed) return false;
    return loadIntoElement(el, url);
  }

  // Try the slide's primary URL; if that fails, transparently retry with
  // the Telegram preview fallback URL (only present on proven_high_res
  // slides). This lets a transient images.adsttc.com hiccup degrade to
  // the t.me/s preview rather than producing a black slide.
  // `generation` (when given) aborts the attempt if a newer transition has
  // started, so a stale load never touches the layer that is now on screen.
  async function ensureSlideLoaded(el, slide, generation = null) {
    if (!slide || !slide.url) return false;
    const ok = await ensureLayerReady(el, slide.url);
    if (generation !== null && generation !== transitionGeneration) return false;
    if (ok) return true;
    if (typeof slide.url_fallback === 'string' && slide.url_fallback && slide.url_fallback !== slide.url) {
      const okFb = await ensureLayerReady(el, slide.url_fallback);
      if (generation !== null && generation !== transitionGeneration) return false;
      if (okFb) {
        // Permanently point this slide at the working fallback so subsequent
        // re-renders (looping back around) do not pay the failure cost again.
        slide.url = slide.url_fallback;
        return true;
      }
    }
    return false;
  }

  function warmUpcomingSlides(startOffset = 1, count = PRELOAD_LOOKAHEAD) {
    if (!slides.length) return;
    const seen = new Set();
    for (let offset = startOffset; offset < startOffset + count; offset++) {
      const slide = slides[(idx + offset) % slides.length];
      if (!slide || !slide.url || seen.has(slide.url)) continue;
      seen.add(slide.url);
      warmImage(slide.url).catch(() => {});
    }
  }

  function decodeImageElement(el) {
    if (!el || typeof el.decode !== 'function') return Promise.resolve();
    return el.decode().catch(() => {});
  }

  // Warm upcoming images and pre-arm the hidden back layer with the next
  // slide so the upcoming crossfade starts instantly.
  function beginPreloading() {
    if (!slides.length) return;
    warmUpcomingSlides(1, PRELOAD_LOOKAHEAD);
    const next = slides[(idx + 1) % slides.length];
    if (next && next.url) {
      ensureSlideLoaded(backEl, next, transitionGeneration).catch(() => {});
    }
  }

  function swapLayers() {
    [frontEl, backEl] = [backEl, frontEl];
  }

  // ---- Phase machine -------------------------------------------------------
  function startPhase(name, dur, fn) {
    clearTimers();
    phase = name;
    phaseDur = dur;
    phaseStart = performance.now();
    timer = setTimeout(() => { fn(); }, dur);
  }

  function stepIndex(forward) {
    if (!slides.length) return;
    if (forward) {
      if (idx >= slides.length - 1) {
        slides = buildRandomizedSlides();
        idx = 0;
      } else {
        idx += 1;
      }
    } else {
      idx = (idx - 1 + slides.length) % slides.length;
    }
  }

  // Advance idx (skipping broken slides) until one loads into the hidden
  // back layer. The current image stays on screen the whole time.
  async function advanceToLoadable(forward, generation) {
    for (let tries = 0; tries < MAX_SKIPS; tries++) {
      stepIndex(forward);
      const s = slides[idx];
      const ok = await ensureSlideLoaded(backEl, s, generation);
      if (generation !== transitionGeneration) return null;
      if (ok) {
        consecutiveSkips = 0;
        return s;
      }
      consecutiveSkips++;
      console.warn('[slideshow] skipping broken slide', s.id, s.url);
    }
    return null;
  }

  // Crossfade to the next loadable slide. The incoming image fades in ON TOP
  // of the current one: the current slide never disappears (and the screen
  // never goes black) until the next has fully faded in.
  async function doTransition(forward = true, fadeMs = FADE_MS) {
    clearTimers();
    const generation = ++transitionGeneration;
    phase = 'transition';

    // If a previous crossfade was interrupted mid-fade (rapid prev/next),
    // finalize it first: the visible incoming layer becomes the front, so
    // the back layer we are about to load into stays hidden.
    if (backEl.getAttribute('data-state') === 'visible') {
      showImageInstant(frontEl, false);
      swapLayers();
    }

    const frontShowing = frontEl.getAttribute('data-state') === 'visible';
    if (!frontShowing) setLoading(true); // only the very first slide starts from black

    const target = await advanceToLoadable(forward, generation);
    if (generation !== transitionGeneration) return;
    setLoading(false);
    if (!target) {
      // Nothing loadable right now — keep the current image and retry soon.
      startPhase('hold', 10_000, () => { consecutiveSkips = 0; doTransition(forward); });
      return;
    }

    // Clear stale clamp, then clamp to the incoming image's native size
    backEl.style.maxWidth  = '';
    backEl.style.maxHeight = '';
    clampToNatural(backEl);

    setTop(backEl);
    setImgFadeDuration(backEl, fadeMs);
    showCaption(false);
    showImage(backEl, true); // crossfade begins over the still-visible front

    startPhase('transition', fadeMs, () => {
      // Old front is now fully covered — hide it without animation and swap.
      showImageInstant(frontEl, false);
      swapLayers();
      formatCaption(target);
      updateHud();
      updateLetterboxLayout();
      showCaption(true);
      beginPreloading();
      if (isPaused) {
        // Park: resume from togglePause restarts the hold countdown.
        phase = 'hold';
        phaseDur = HOLD_MS;
        phaseRemainAtPause = HOLD_MS;
        return;
      }
      startPhase('hold', HOLD_MS, () => doTransition());
    });
  }

  // ---- Manual controls -----------------------------------------------------
  function gotoSlide(delta) {
    // Quick crossfade — no black cut. Generation bump inside doTransition
    // cancels any in-flight auto transition.
    doTransition(delta > 0, MANUAL_FADE_MS);
  }

  function togglePause() {
    if (isPaused) {
      isPaused = false;
      $('btnPause').textContent = '⏸';
      if (phase === 'hold' && timer === null) {
        startPhase('hold', Math.max(1000, phaseRemainAtPause), () => doTransition());
      }
      // An in-flight transition resumes itself: its completion callback
      // checks isPaused and arms the next hold.
    } else {
      isPaused = true;
      $('btnPause').textContent = '▶';
      if (phase === 'hold' && timer) {
        const elapsed = performance.now() - phaseStart;
        phaseRemainAtPause = Math.max(0, phaseDur - elapsed);
        clearTimers();
      }
      // During a transition the crossfade completes, then parks (see above).
    }
  }

  function enterFullscreen() {
    const el = document.documentElement;
    const fn = el.requestFullscreen || el.webkitRequestFullscreen || el.mozRequestFullScreen || el.msRequestFullscreen;
    if (document.fullscreenElement) {
      (document.exitFullscreen || document.webkitExitFullscreen || document.mozCancelFullScreen || document.msExitFullscreen).call(document);
    } else if (fn) {
      fn.call(el).catch(() => {});
    }
  }

  // ---- UI: controls visibility ---------------------------------------------
  let idleTimer = null;
  function nudgeControls() {
    controls.setAttribute('data-state', 'show');
    document.body.classList.remove('hide-cursor');
    if (idleTimer) clearTimeout(idleTimer);
    idleTimer = setTimeout(() => {
      controls.removeAttribute('data-state');
      document.body.classList.add('hide-cursor');
    }, CONTROLS_IDLE_MS);
  }

  // ---- Keyboard ------------------------------------------------------------
  function onKey(e) {
    if (e.key === 'ArrowRight' || e.key === 'PageDown' || e.key === ' ') {
      e.preventDefault();
      if (e.key === ' ') togglePause();
      else gotoSlide(+1);
    } else if (e.key === 'ArrowLeft' || e.key === 'PageUp') {
      e.preventDefault();
      gotoSlide(-1);
    } else if (e.key === 'f' || e.key === 'F') {
      enterFullscreen();
    } else if (e.key === 'p' || e.key === 'P') {
      togglePause();
    }
  }

  // ---- Bootstrap -----------------------------------------------------------
  // Append the build version as a query param to every image URL so the
  // browser always picks up freshly-built Telegram-faithful imagery and never
  // serves a stale CDN copy after a rebuild.
  // We DO NOT append the cache-buster to images.adsttc.com URLs because those
  // already carry their own version query string and unrelated query params
  // would defeat their CloudFront cache. Only Telegram CDN URLs and other
  // hosts get the build_version suffix.
  function appendCacheBuster(url, buildVersion) {
    if (!url || !buildVersion || typeof url !== 'string') return url;
    try {
      const u = new URL(url);
      if (u.hostname.endsWith('images.adsttc.com')) return url;
    } catch (_) { /* relative url, fall through */ }
    const sep = url.includes('?') ? '&' : '?';
    return `${url}${sep}v=${encodeURIComponent(buildVersion)}`;
  }

  function applyBuildVersion(slides, buildVersion) {
    if (!buildVersion || !Array.isArray(slides)) return slides;
    return slides.map((s) => {
      if (!s || typeof s.url !== 'string' || !s.url) return s;
      const out = Object.assign({}, s, { url: appendCacheBuster(s.url, buildVersion) });
      if (typeof s.url_fallback === 'string' && s.url_fallback) {
        out.url_fallback = appendCacheBuster(s.url_fallback, buildVersion);
      }
      return out;
    });
  }

  async function loadSlidesJson() {
    // Cache-bust the JSON request itself so a browser cannot serve a stale slides.json.
    const bust = Date.now().toString(36);
    const res = await fetch(`./slides.json?cb=${bust}`, { cache: 'no-store' });
    if (!res.ok) throw new Error('slides.json HTTP ' + res.status);
    const data = await res.json();
    // Support both legacy flat array and versioned envelope {build_version, slides:[...]}
    if (Array.isArray(data)) return { buildVersion: '', slides: data };
    if (data && Array.isArray(data.slides)) {
      return { buildVersion: data.build_version || '', slides: data.slides };
    }
    throw new Error('slides.json: unexpected shape');
  }

  async function main() {
    try {
      const { slides: flatSlides, buildVersion } = await loadSlidesJson();
      allSlides = applyBuildVersion(flatSlides, buildVersion).filter((s) => s && s.url);
      slides = buildRandomizedSlides();
    } catch (err) {
      console.error('Failed to load slides.json', err);
      // Show a minimal error caption (Russian)
      capTitle.textContent = 'Не удалось загрузить список слайдов';
      caption.setAttribute('data-state', 'in');
      return;
    }

    if (!Array.isArray(slides) || slides.length === 0) {
      capTitle.textContent = 'Список слайдов пуст';
      caption.setAttribute('data-state', 'in');
      return;
    }

    // Wire UI
    $('btnPrev').addEventListener('click',  () => { nudgeControls(); gotoSlide(-1); });
    $('btnNext').addEventListener('click',  () => { nudgeControls(); gotoSlide(+1); });
    $('btnPause').addEventListener('click', () => { nudgeControls(); togglePause(); });
    $('btnFull').addEventListener('click',  () => { nudgeControls(); enterFullscreen(); });
    // stopPropagation: клик по кнопке не должен доходить до stage (там первый клик — fullscreen)
    $('btnReload').addEventListener('click', (e) => { e.stopPropagation(); location.reload(); });

    document.addEventListener('keydown', onKey);
    ['mousemove', 'touchstart', 'pointermove'].forEach((ev) =>
      window.addEventListener(ev, nudgeControls, { passive: true }));

    // Click on stage (but not on controls) enters fullscreen on first click.
    // Do not toggle pause on subsequent clicks: that caused accidental freezes
    // when the user simply tapped/clicked the image while browsing.
    let firstClick = true;
    stage.addEventListener('click', (e) => {
      if (controls.contains(e.target)) return;
      nudgeControls();
      if (firstClick) {
        firstClick = false;
        enterFullscreen();
      }
    });

    // Show first-launch hint briefly
    hint.setAttribute('data-state', 'show');
    setTimeout(() => hint.removeAttribute('data-state'), 4500);

    // Initial state: stage is black, no image visible
    showImage(imgA, false);
    showImage(imgB, false);
    updateHud();
    updateLetterboxLayout();

    // Recompute equal top/bottom black bands on viewport changes.
    window.addEventListener('resize', updateLetterboxLayout, { passive: true });

    // Begin: idx=-1 so the first transition lands on slides[0], fading in
    // over the black stage (the only time the stage is ever black).
    idx = -1;
    doTransition();
  }

  // Re-arm rendering after long backgrounding (browsers throttle setTimeout).
  // If the tab was hidden long enough that timers stalled past the current
  // phase budget, move on to the next slide with a normal crossfade.
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState !== 'visible' || isPaused) return;
    const elapsed = performance.now() - phaseStart;
    if (timer && phaseDur > 0 && elapsed > phaseDur + 1500) {
      doTransition(); // clears stale timers and cancels stale async work
    }
  });

  // Kick off
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', main, { once: true });
  } else {
    main();
  }
})();
