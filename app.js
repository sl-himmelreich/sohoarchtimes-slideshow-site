/* SohoArchTimes — Slideshow engine
   - Loops slides forever
   - Objects are shuffled in random order on each full pass
   - Images inside each object keep their original sequence
   - 30s hold per slide, with 3s fade-in and 3s fade-out through black
   - Transitions through black (no crossfade)
   - Preloads next image; skips broken images automatically
   - Resilient to slow loads; never leaves a blank white screen
*/

(() => {
  'use strict';

  // ---- Timing (ms) ---------------------------------------------------------
  const FADE_MS  = 3000;
  const HOLD_MS  = 30_000;
  const CYCLE_MS = FADE_MS + HOLD_MS + FADE_MS; // 36s total
  const LOAD_TIMEOUT_MS = 25_000;               // give a slow image this long to load
  const CONTROLS_IDLE_MS = 2500;                // hide controls after idle
  const PRELOAD_LOOKAHEAD = 3;                  // warm the next few slide images immediately
  const IMAGE_CACHE_LIMIT = 24;                 // keep only a modest hot cache in memory

  void CYCLE_MS;

  // ---- DOM -----------------------------------------------------------------
  const $ = (id) => document.getElementById(id);
  const stage   = $('stage');
  const frame   = $('frame');
  const imgA    = $('imgA');
  const imgB    = $('imgB');
  const fade    = $('fade');
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
  let objectGroups = [];
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
  let phase = 'idle';      // 'fadeIn' | 'hold' | 'fadeOut' | 'idle'
  let phaseStart = 0;
  let phaseDur = 0;
  let phaseRemainAtPause = 0;
  let nextPreloaded = false;
  let consecutiveSkips = 0;
  let preloadGeneration = 0;
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
    if (!slides.length) { setText(hudCount, ''); return; }
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

  function groupSlidesByObject(flatSlides) {
    const groups = [];
    const byMid = new Map();
    for (const slide of flatSlides) {
      const mid = slide.mid;
      if (!byMid.has(mid)) {
        const group = [];
        byMid.set(mid, group);
        groups.push(group);
      }
      byMid.get(mid).push(slide);
    }
    for (const group of groups) {
      group.sort((a, b) => (a.idx || 0) - (b.idx || 0));
    }
    return groups;
  }

  function buildRandomizedSlides() {
    if (!objectGroups.length) return [];
    return shuffleArray(objectGroups).flat();
  }

  function setFadeBlack(black, instant = false) {
    if (instant) {
      fade.setAttribute('data-instant', '1');
      // force reflow so transition:none applies
      void fade.offsetWidth;
    } else {
      fade.removeAttribute('data-instant');
    }
    if (black) fade.setAttribute('data-state', 'black');
    else       fade.removeAttribute('data-state');
    if (instant) {
      // restore transition on next frame
      requestAnimationFrame(() => fade.removeAttribute('data-instant'));
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

  function beginPreloading() {
    if (!slides.length) return;
    const next = slides[(idx + 1) % slides.length];
    if (!next || !next.url) {
      nextPreloaded = false;
      return;
    }

    const generation = ++preloadGeneration;
    nextPreloaded = false;
    warmUpcomingSlides(1, PRELOAD_LOOKAHEAD);

    ensureLayerReady(backEl, next.url)
      .then((ok) => {
        if (generation !== preloadGeneration) return;
        nextPreloaded = ok;
        showImage(backEl, false);
      })
      .catch(() => {
        if (generation !== preloadGeneration) return;
        nextPreloaded = false;
      });
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

  // Run the current slide cycle: fade-in -> hold -> fade-out -> next
  async function runCurrent() {
    if (!slides.length) return;
    const s = slides[idx];

    preloadGeneration += 1;
    nextPreloaded = false;
    setLoading(true);
    // Ensure stage is black and image hidden before loading
    showImage(frontEl, false);
    setFadeBlack(true, true);

    // If the front layer already has this image loaded (via preload+swap), skip re-fetch
    let ok;
    if (isElementReady(frontEl, s.url)) {
      ok = true;
    } else {
      // Try to load the image into the front layer
      ok = await ensureLayerReady(frontEl, s.url);
    }
    if (!ok) {
      consecutiveSkips++;
      console.warn('[slideshow] skipping broken slide', s.id, s.url);
      setLoading(false);
      if (consecutiveSkips >= MAX_SKIPS) {
        // Bail out: stay on black, retry in 10s
        timer = setTimeout(() => { consecutiveSkips = 0; runCurrent(); }, 10_000);
        return;
      }
      advance(true);
      runCurrent();
      return;
    }
    consecutiveSkips = 0;
    setLoading(false);

    // Update caption now (it fades with the image-in)
    formatCaption(s);
    updateHud();
    updateLetterboxLayout();

    // Phase 1: fade-in over 5s. Image goes opaque, black overlay goes transparent.
    showImage(frontEl, true);
    setFadeBlack(false);
    showCaption(true);

    beginPreloading();

    startPhase('fadeIn', FADE_MS, () => {
      // Phase 2: hold visible for 30s while the next slides stay hot in cache.
      startPhase('hold', HOLD_MS, () => {
        // Phase 3: fade-out over 3s. Image stays visible; we just raise the black overlay.
        showCaption(false);
        setFadeBlack(true);
        startPhase('fadeOut', FADE_MS, () => {
          // Cycle done — advance and continue
          showImage(frontEl, false);
          // back layer's src may have been set by preloader — swap so it becomes front
          if (nextPreloaded) {
            swapLayers();
          }
          nextPreloaded = false;
          advance(true);
          runCurrent();
        });
      });
    });
  }

  function advance(forward) {
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

  // ---- Manual controls -----------------------------------------------------
  function gotoSlide(delta) {
    // Hard cut: black out, swap, restart cycle
    clearTimers();
    preloadGeneration += 1;
    nextPreloaded = false;
    showImage(frontEl, false);
    showImage(backEl, false);
    setFadeBlack(true, true);
    showCaption(false);
    advance(delta > 0);
    runCurrent();
  }

  function togglePause() {
    if (isPaused) {
      isPaused = false;
      $('btnPause').textContent = '⏸';
      // Resume current phase with remaining time
      if (phaseRemainAtPause > 0) {
        const cont = (phase === 'fadeIn')
          ? () => startPhase('hold', HOLD_MS, () => {
              showCaption(false);
              setFadeBlack(true);
              startPhase('fadeOut', FADE_MS, finishCycle);
            })
          : (phase === 'hold')
          ? () => {
              showCaption(false);
              setFadeBlack(true);
              startPhase('fadeOut', FADE_MS, finishCycle);
            }
          : finishCycle;
        timer = setTimeout(cont, phaseRemainAtPause);
        if (phase === 'hold' && !nextPreloaded) beginPreloading();
      } else {
        runCurrent();
      }
    } else {
      isPaused = true;
      $('btnPause').textContent = '▶';
      const elapsed = performance.now() - phaseStart;
      phaseRemainAtPause = Math.max(0, phaseDur - elapsed);
      clearTimers();
      // Freeze visual state — leave transitions where they are
    }
  }

  function finishCycle() {
    showImage(frontEl, false);
    if (nextPreloaded) swapLayers();
    nextPreloaded = false;
    advance(true);
    runCurrent();
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
  async function loadSlidesJson() {
    const res = await fetch('./slides.json', { cache: 'no-store' });
    if (!res.ok) throw new Error('slides.json HTTP ' + res.status);
    return res.json();
  }

  async function main() {
    try {
      const flatSlides = await loadSlidesJson();
      objectGroups = groupSlidesByObject(flatSlides);
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
    setFadeBlack(true, true);
    showImage(imgA, false);
    showImage(imgB, false);
    updateHud();
    updateLetterboxLayout();

    // Recompute equal top/bottom black bands on viewport changes.
    window.addEventListener('resize', updateLetterboxLayout, { passive: true });

    // Begin
    runCurrent();
  }

  // Re-arm rendering after long backgrounding (browsers throttle setTimeout).
  // If the tab was hidden long enough that timers stalled past the current
  // phase budget, force-finish the cycle and start fresh on the next slide.
  document.addEventListener('visibilitychange', () => {
    if (document.visibilityState !== 'visible' || isPaused) return;
    if (phase === 'idle' && timer === null) {
      runCurrent();
      return;
    }
    const elapsed = performance.now() - phaseStart;
    if (phaseDur > 0 && elapsed > phaseDur + 1500) {
      // Timer was throttled past its budget — restart cleanly
      clearTimers();
      nextPreloaded = false;
      showImage(frontEl, false);
      showImage(backEl, false);
      setFadeBlack(true, true);
      showCaption(false);
      advance(true);
      runCurrent();
    }
  });

  // Kick off
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', main, { once: true });
  } else {
    main();
  }
})();
