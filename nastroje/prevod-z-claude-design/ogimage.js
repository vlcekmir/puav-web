const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch(); const p = await (await b.newContext({ viewport: { width: 1200, height: 900 }, deviceScaleFactor: 1 })).newPage();
  await p.goto(process.argv[2], { waitUntil: 'networkidle' }); await p.evaluate(() => document.fonts.ready);
  await p.evaluate(async () => {
    const hero = document.querySelector('#top');
    const text = hero.querySelector('h1').parentElement;
    text.querySelector('p').remove();
    text.lastElementChild.remove();               // buttons
    hero.querySelector('div[style*="min-height"]').style.minHeight = '630px';
  });
  const box = await p.evaluate(() => { const r = document.querySelector('#top').getBoundingClientRect(); return { y: r.top + window.scrollY, h: r.height }; });
  await p.screenshot({ path: process.argv[3], type: 'jpeg', quality: 85, clip: { x: 0, y: box.y + (box.h - 630) / 2, width: 1200, height: 630 } });
  await b.close();
})();
