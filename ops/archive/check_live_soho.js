const { chromium } = require('playwright');
(async() => {
  const browser = await chromium.launch({headless:true});
  const page = await browser.newPage({ viewport: { width: 1366, height: 847 } });
  const logs = [];
  page.on('console', msg => logs.push({type: msg.type(), text: msg.text()}));
  page.on('pageerror', err => logs.push({type: 'pageerror', text: String(err)}));
  await page.goto('https://sl-himmelreich.github.io/sohoarchtimes-slideshow-site/', { waitUntil: 'networkidle' });
  await page.waitForTimeout(2000);
  const snap = async(label) => page.evaluate((label) => ({
    label,
    counter: document.querySelector('.hud__index')?.textContent?.trim(),
    total: document.querySelector('.hud__total')?.textContent?.trim(),
    title: document.querySelector('.caption')?.textContent?.trim()?.slice(0,180),
    src: document.querySelector('.slide-img')?.currentSrc || document.querySelector('.slide-img')?.src || null,
    complete: document.querySelector('.slide-img')?.complete,
    naturalWidth: document.querySelector('.slide-img')?.naturalWidth,
    naturalHeight: document.querySelector('.slide-img')?.naturalHeight,
  }), label);
  const checkpoints = [];
  checkpoints.push(await snap('t0'));
  for (const ms of [10000, 25000, 35000, 65000, 95000]) {
    await page.waitForTimeout(ms - (checkpoints.at(-1)._elapsed || 0));
    const s = await snap(`t${ms/1000}`);
    s._elapsed = ms;
    checkpoints.push(s);
  }
  console.log(JSON.stringify({ checkpoints, logs }, null, 2));
  await browser.close();
})();
