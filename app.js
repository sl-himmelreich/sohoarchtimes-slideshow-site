/* SohoArchTimes — Slideshow engine
   - Loops slides forever
   - Objects are shuffled in random order on each full pass
   - Images inside each object keep their original sequence
   - 60s per slide: 5s fade-in from black -> 50s hold -> 5s fade-out to black
   - Transitions through black (no crossfade)
   - Preloads next image; skips broken images automatically
   - Resilient to slow loads; never leaves a blank white screen
*/

(() => {
  'use strict';

  // ---- Timing (ms) ---------------------------------------------------------
  const FADE_MS  = 5000;
  const HOLD_MS  = 50_000;
  const CYCLE_MS = FADE_MS + HOLD_MS + FADE_MS; // 60s
  const PRELOAD_LEAD_MS = 8000;                 // start preloading 8s before swap
  const LOAD_TIMEOUT_MS = 25_000;                // give a slow image this long to load
  const CONTROLS_IDLE_MS = 2500;                 // hide controls after idle

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
  let preloadTimer = null; // schedules preload of next slide
  let phase = 'idle';      // 'fadeIn' | 'hold' | 'fadeOut' | 'idle'
  let phaseStart = 0;
  let phaseDur = 0;
  let phaseRemainAtPause = 0;
  let nextPreloaded = false;
  let consecutiveSkips = 0;
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

  function clearTimers() {
    if (timer)        { clearTimeout(timer);        timer = null; }
    if (preloadTimer) { clearTimeout(preloadTimer); preloadTimer = null; }
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

  // Load an image into el with timeout. Resolves true on success, false on fail.
  function loadInto(el, url) {
    return new Promise((resolve) => {
      if (!url) { resolve(false); return; }
      const probe = new Image();
      probe.decoding = 'async';
      // Don't set crossOrigin — we just display, not read pixels.
      let settled = false;
      const cleanup = () => {
        probe.onload = probe.onerror = null;
        clearTimeout(t);
      };
      const t = setTimeout(() => {
        if (settled) return; settled = true; cleanup(); resolve(false);
      }, LOAD_TIMEOUT_MS);
      probe.onload = () => {
        if (settled) return; settled = true; cleanup();
        try { el.src = probe.src; } catch (_) {}
        resolve(true);
      };
      probe.onerror = () => {
        if (settled) return; settled = true; cleanup(); resolve(false);
      };
      probe.src = url;
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

    setLoading(true);
    // Ensure stage is black and image hidden before loading
    showImage(frontEl, false);
    setFadeBlack(true, true);

    // If the front layer already has this image loaded (via preload+swap), skip re-fetch
    let ok;
    if (frontEl.src && frontEl.src === s.url && frontEl.complete && frontEl.naturalWidth > 0) {
      ok = true;
    } else {
      // Try to load the image into the front layer
      ok = await loadInto(frontEl, s.url);
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
      advance(false);
      runCurrent();
      return;
    }
    consecutiveSkips = 0;
    setLoading(false);

    // Update caption now (it fades with the image-in)
    formatCaption(s);
    updateHud();

    // Phase 1: fade-in over 5s. Image goes opaque, black overlay goes transparent.
    showImage(frontEl, true);
    setFadeBlack(false);
    showCaption(true);

    startPhase('fadeIn', FADE_MS, () => {
      // Phase 2: hold visible for 50s. Schedule preload of next slide partway.
      startPhase('hold', HOLD_MS, () => {
        // Phase 3: fade-out over 5s. Image stays visible; we just raise the black overlay.
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
      // Schedule preload near end of hold
      schedulePreload(HOLD_MS - PRELOAD_LEAD_MS);
    });
  }

  function schedulePreload(delay) {
    if (preloadTimer) clearTimeout(preloadTimer);
    preloadTimer = setTimeout(async () => {
      preloadTimer = null;
      const next = slides[(idx + 1) % slides.length];
      if (!next) return;
      // Preload via probe Image but also assign to back layer so it's decoded
      const ok = await loadInto(backEl, next.url);
      nextPreloaded = ok;
      // Keep back layer hidden (opacity 0)
      showImage(backEl, false);
    }, Math.max(0, delay));
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
        // Re-arm preload schedule if appropriate
        if (phase === 'hold') {
          const remain = phaseRemainAtPause - PRELOAD_LEAD_MS;
          schedulePreload(remain > 0 ? remain : 0);
        }
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

    // Click on stage (but not on controls) toggles fullscreen on first click
    let firstClick = true;
    stage.addEventListener('click', (e) => {
      if (controls.contains(e.target)) return;
      if (firstClick) {
        firstClick = false;
        enterFullscreen();
      } else {
        togglePause();
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
