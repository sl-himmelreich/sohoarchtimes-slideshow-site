/* SohoArchTimes — Slideshow engine
   - Loops slides forever
   - ALL slides are shuffled into a fresh random order on every page load
     and reshuffled again after each full pass
   - 30s hold per slide, then a 3s symmetric CROSSFADE: the current image
     fades out while the next fades in simultaneously at the same speed —
     the screen never passes through black
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
  const LOAD_TIMEOUT_MS = 90_000;               // оригиналы весят 8–20 МБ — даём им догрузиться
  const MAX_RETRIES_PER_PASS = 3;               // медленный кадр откладываем в конец прохода, не выкидываем
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
  const langBtn  = $('btnLang');
  const loaderLabel = document.querySelector('#loader .loader-label');

  // ---- i18n ----------------------------------------------------------------
  const LANG_KEY = 'soho_lang';
  const UI = {
    ru: {
      loader: 'Загрузка…',
      hint: 'Нажмите в любом месте — для полноэкранного режима',
      refresh: 'Обновить',
      loadError: 'Не удалось загрузить список слайдов',
      empty: 'Список слайдов пуст',
      tokenPrompt: 'GitHub-токен для пересборки сайта по Telegram (хранится только в этом браузере).\nПустое значение — кнопка просто перезагружает страницу.',
      tokenSaved: 'Готово: ключ сохранён в этом браузере. Кнопка ⟳ внизу справа теперь обновляет сайт по Telegram.',
      rebuildFail: (code) => `Пересборка не запустилась (HTTP ${code}). Проверьте токен: двойной клик по кнопке ⟳.`,
    },
    en: {
      loader: 'Loading…',
      hint: 'Click anywhere for fullscreen',
      refresh: 'Refresh',
      loadError: 'Failed to load the slide list',
      empty: 'The slide list is empty',
      tokenPrompt: 'GitHub token to rebuild the site from Telegram (stored only in this browser).\nLeave empty to make the button just reload the page.',
      tokenSaved: 'Done: the key is saved in this browser. The ⟳ button at the bottom right now refreshes the site from Telegram.',
      rebuildFail: (code) => `Rebuild did not start (HTTP ${code}). Check the token: double-click the ⟳ button.`,
    },
  };
  function getLang() {
    try { const v = localStorage.getItem(LANG_KEY); if (v === 'en' || v === 'ru') return v; } catch (_) {}
    return 'ru';
  }
  function setLang(v) {
    lang = (v === 'en') ? 'en' : 'ru';
    try { localStorage.setItem(LANG_KEY, lang); } catch (_) {}
    applyLang();
  }
  const t = () => UI[lang] || UI.ru;

  // ---- State ---------------------------------------------------------------
  let slides = [];
  let allSlides = [];      // canonical slide list; `slides` is its shuffled view
  let idx = 0;             // current index into slides[]
  let lang = getLang();    // 'ru' | 'en'
  let currentSlide = null; // slide currently shown (for re-rendering on lang switch)
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
  let shuffleSig = '';           // signature of the current slide set
  const warmCache = new Map();
  const MAX_SKIPS = 12;    // safety: avoid infinite skip loops

  // ---- Helpers -------------------------------------------------------------
  const setText = (el, v) => { el.textContent = (v == null ? '' : String(v).trim()); };

  function formatCaption(s) {
    currentSlide = s;
    if (!s) { setText(capTitle, ''); setText(capArch, ''); setText(capYear, ''); setText(capLoc, ''); return; }
    const en = (lang === 'en');
    setText(capTitle, en ? (s.title_en || s.title) : s.title);
    setText(capArch,  en ? (s.arch_en  != null ? s.arch_en : s.arch) : s.arch);
    setText(capYear,  s.year);
    setText(capLoc,   en ? (s.loc_en   || s.loc)   : s.loc);
  }

  // Apply the current language to all static UI and re-render the caption.
  function applyLang() {
    try { document.documentElement.lang = lang; } catch (_) {}
    if (loaderLabel) setText(loaderLabel, t().loader);
    if (hint) setText(hint, t().hint);
    const rb = $('btnReload'); if (rb) rb.title = t().refresh;
    if (langBtn) {
      const ru = langBtn.querySelector('[data-l="ru"]');
      const en = langBtn.querySelector('[data-l="en"]');
      if (ru) ru.toggleAttribute('data-active', lang === 'ru');
      if (en) en.toggleAttribute('data-active', lang === 'en');
      langBtn.setAttribute('aria-label', lang === 'ru' ? 'Язык: русский' : 'Language: English');
    }
    if (currentSlide) formatCaption(currentSlide);
    if (typeof updateLetterboxLayout === 'function') updateLetterboxLayout();
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

  // ---- Persistent shuffle "bag" --------------------------------------------
  // A single random permutation of ALL slides is played to the end before any
  // image repeats. The order + current position persist in localStorage, so a
  // page reload (or the ⟳ button) CONTINUES the same cycle instead of starting
  // a new random order — that is what prevents early repeats across reloads.
  // The bag resets automatically when the slide set changes (new build).
  const SHUFFLE_KEY = 'soho_shuffle';

  function slidesSignature(list) {
    let h = 5381;
    for (const s of list) {
      const id = String(s.id || '');
      for (let i = 0; i < id.length; i++) h = ((h << 5) + h + id.charCodeAt(i)) & 0xffffffff;
    }
    return list.length + ':' + (h >>> 0).toString(36);
  }

  function buildRandomizedSlides() {
    return shuffleArray(allSlides);
  }

  function saveShuffleState() {
    try {
      localStorage.setItem(SHUFFLE_KEY, JSON.stringify({
        sig: shuffleSig,
        ids: slides.map((s) => s.id),
        pos: idx,
      }));
    } catch (_) {}
  }

  // Returns {order, pos} to resume, or null to start a fresh permutation.
  function loadShuffleState() {
    try {
      const raw = localStorage.getItem(SHUFFLE_KEY);
      if (!raw) return null;
      const st = JSON.parse(raw);
      if (!st || st.sig !== shuffleSig || !Array.isArray(st.ids)) return null;
      const byId = new Map(allSlides.map((s) => [s.id, s]));
      const order = st.ids.map((id) => byId.get(id)).filter(Boolean);
      if (order.length !== allSlides.length) return null; // set changed — reshuffle
      let pos = Number.isInteger(st.pos) ? st.pos : -1;
      if (pos < -1 || pos >= order.length) pos = -1;
      return { order, pos };
    } catch (_) { return null; }
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

  // Кадры, не загрузившиеся в этом проходе: id -> число неудачных попыток.
  let passRetries = Object.create(null);
  // Железный предохранитель правила «без повторов, пока не показаны все»:
  // id кадров, уже показанных в текущем проходе. Что бы ни случилось с
  // очередью (перестановки, ретраи, гонки таймеров) — кадр из этого
  // множества второй раз в этом проходе не выйдет.
  let shownThisPass = new Set();
  let lastShownId = '';

  function reshuffleBag() {
    slides = buildRandomizedSlides();
    passRetries = Object.create(null);
    shownThisPass = new Set();
    // На стыке проходов новый порядок не должен начинаться с только что
    // показанного кадра — иначе один и тот же кадр идёт два раза подряд.
    if (slides.length > 1 && lastShownId && slides[0].id === lastShownId) {
      const j = 1 + randomInt(slides.length - 1);
      [slides[0], slides[j]] = [slides[j], slides[0]];
    }
    idx = -1; // следующий stepIndex попадёт на позицию 0
  }

  function stepIndex(forward) {
    if (!slides.length) return;
    if (forward) {
      if (idx >= slides.length - 1) {
        // Полный проход: каждый кадр показан (или трижды не загрузился).
        reshuffleBag();
      }
      idx += 1;
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
      if (forward && shownThisPass.has(s.id)) {
        // Кадр уже был в этом проходе (страховка от любых перестановок
        // очереди) — просто идём дальше, попытку не тратим на загрузку.
        continue;
      }
      const ok = await ensureSlideLoaded(backEl, s, generation);
      if (generation !== transitionGeneration) return null;
      if (ok) {
        consecutiveSkips = 0;
        if (forward) { shownThisPass.add(s.id); lastShownId = s.id; }
        return s;
      }
      consecutiveSkips++;
      if (forward) {
        // Правило «без повторов, пока не показаны все ~200» держится только
        // если проход реально ПОКАЗЫВАЕТ каждый кадр. Поэтому кадр, который
        // не успел загрузиться, не выкидываем из прохода, а переставляем в
        // конец очереди — попробуем снова, когда дойдёт черёд. Иначе цикл
        // сжимается до уже закешированных картинок и они идут по кругу.
        const fails = (passRetries[s.id] || 0) + 1;
        passRetries[s.id] = fails;
        if (fails <= MAX_RETRIES_PER_PASS && idx < slides.length - 1) {
          slides.splice(idx, 1);
          slides.push(s);
          idx -= 1; // на этой позиции теперь стоит следующий кадр
        }
        console.warn('[slideshow] postponing slow/broken slide', s.id, 'attempt', fails);
      } else {
        console.warn('[slideshow] skipping broken slide', s.id, s.url);
      }
    }
    return null;
  }

  // Crossfade to the next loadable slide: the current image fades out while
  // the incoming one (stacked on top) fades in simultaneously at the same
  // speed. The screen never passes through black.
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
    setImgFadeDuration(frontEl, fadeMs);
    showCaption(false);
    showImage(backEl, true);   // next fades in…
    showImage(frontEl, false); // …while the current fades out at the same speed

    startPhase('transition', fadeMs, () => {
      swapLayers();
      formatCaption(target);
      updateHud();
      updateLetterboxLayout();
      showCaption(true);
      saveShuffleState(); // persist order+position so a reload continues the cycle
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

  // ---- Site refresh button (⟳ in the HUD) ----------------------------------
  // Click: rebuild slides.json from the CURRENT public Telegram state via the
  // repo's manual GitHub Action, wait for the fresh build, reload the page.
  // Needs a GitHub token stored once in this browser (double-click to set);
  // without a token the button simply reloads the page.
  const REBUILD_API = 'https://api.github.com/repos/sl-himmelreich/sohoarchtimes-slideshow-site/actions/workflows/rebuild.yml/dispatches';
  const REBUILD_TOKEN_KEY = 'soho_rebuild_token';
  const REBUILD_WAIT_MS = 5 * 60 * 1000;

  function getRebuildToken() {
    try { return (localStorage.getItem(REBUILD_TOKEN_KEY) || '').trim(); } catch (_) { return ''; }
  }

  async function fetchBuildVersion() {
    const res = await fetch(`./slides.json?cb=${Date.now().toString(36)}`, { cache: 'no-store' });
    const d = await res.json();
    return (d && d.build_version) || '';
  }

  async function triggerSiteRebuild() {
    const token = getRebuildToken();
    if (!token) { location.reload(); return; }
    const btn = $('btnReload');
    if (btn.hasAttribute('data-busy')) return;
    btn.setAttribute('data-busy', '1');
    try {
      let before = '';
      try { before = await fetchBuildVersion(); } catch (_) {}
      const ctrl = new AbortController();
      const dispatchTimeout = setTimeout(() => ctrl.abort(), 15000);
      const res = await fetch(REBUILD_API, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${token}`, 'Accept': 'application/vnd.github+json' },
        body: JSON.stringify({ ref: 'main' }),
        signal: ctrl.signal,
      });
      clearTimeout(dispatchTimeout);
      if (res.status !== 204) {
        btn.removeAttribute('data-busy');
        alert(t().rebuildFail(res.status));
        return;
      }
      // The Action rebuilds and commits only if Telegram changed; GitHub Pages
      // then redeploys. Wait for a new build_version, or time out and reload.
      const t0 = Date.now();
      while (Date.now() - t0 < REBUILD_WAIT_MS) {
        await new Promise((r) => setTimeout(r, 8000));
        try {
          const v = await fetchBuildVersion();
          if (before && v && v !== before) break;
        } catch (_) {}
      }
    } catch (err) {
      console.warn('[rebuild] failed:', err);
    }
    location.reload();
  }

  function promptRebuildToken() {
    let existing = getRebuildToken();
    const v = window.prompt(t().tokenPrompt, existing);
    if (v === null) return;
    try {
      if (v.trim()) localStorage.setItem(REBUILD_TOKEN_KEY, v.trim());
      else localStorage.removeItem(REBUILD_TOKEN_KEY);
    } catch (_) {}
  }

  function wireReloadButton() {
    const btn = $('btnReload');
    let clickTimer = null;
    btn.addEventListener('click', (e) => {
      e.stopPropagation(); // не задевать fullscreen-по-клику на сцене
      if (clickTimer) return; // второй клик обработает dblclick
      clickTimer = setTimeout(() => { clickTimer = null; triggerSiteRebuild(); }, 350);
    });
    btn.addEventListener('dblclick', (e) => {
      e.stopPropagation();
      if (clickTimer) { clearTimeout(clickTimer); clickTimer = null; }
      promptRebuildToken();
    });
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

  // One-click token install: opening the site with #token=... in the URL
  // stores the rebuild token in this browser and cleans the address bar.
  // The token never reaches any server (URL fragments are client-side only).
  function installTokenFromHash() {
    const m = /[#&]token=([^&]+)/.exec(location.hash || '');
    if (!m) return;
    try {
      localStorage.setItem(REBUILD_TOKEN_KEY, decodeURIComponent(m[1]).trim());
      history.replaceState(null, '', location.pathname + location.search);
      alert(t().tokenSaved);
    } catch (_) {}
  }

  async function main() {
    installTokenFromHash();
    try {
      const { slides: flatSlides, buildVersion } = await loadSlidesJson();
      allSlides = applyBuildVersion(flatSlides, buildVersion).filter((s) => s && s.url);
      shuffleSig = slidesSignature(allSlides);
      const saved = loadShuffleState();
      if (saved) {
        // Continue the same permutation from where we left off (next = pos+1).
        slides = saved.order;
        idx = saved.pos;
        shownThisPass = new Set(slides.slice(0, idx + 1).map((s) => s.id));
        if (idx >= 0 && slides[idx]) lastShownId = slides[idx].id;
      } else {
        slides = buildRandomizedSlides();
        idx = -1;
      }
    } catch (err) {
      console.error('Failed to load slides.json', err);
      capTitle.textContent = t().loadError;
      caption.setAttribute('data-state', 'in');
      return;
    }

    if (!Array.isArray(slides) || slides.length === 0) {
      capTitle.textContent = t().empty;
      caption.setAttribute('data-state', 'in');
      return;
    }

    // Wire UI
    $('btnPrev').addEventListener('click',  () => { nudgeControls(); gotoSlide(-1); });
    $('btnNext').addEventListener('click',  () => { nudgeControls(); gotoSlide(+1); });
    $('btnPause').addEventListener('click', () => { nudgeControls(); togglePause(); });
    $('btnFull').addEventListener('click',  () => { nudgeControls(); enterFullscreen(); });
    wireReloadButton();
    if (langBtn) {
      langBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        nudgeControls();
        setLang(lang === 'ru' ? 'en' : 'ru');
      });
    }
    applyLang();

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

    // Begin. On a fresh start idx=-1 so the first transition lands on
    // slides[0] (fading in over the black stage — the only time it is black);
    // on a resumed cycle idx=saved.pos so the next unseen slide comes up.
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
