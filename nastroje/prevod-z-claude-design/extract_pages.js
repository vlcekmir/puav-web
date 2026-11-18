// Render each route of the Claude Design bundle and dump the rendered markup.
const { chromium } = require('playwright');
const fs = require('fs');
const SRC = process.argv[2], OUT = process.argv[3];
const PAGES = [
  ['platforma', 'PUAV%20Platforma.dc.html'],
  ['praxe', 'PUAV%20Praxe.dc.html'],
  ['kontext', 'PUAV%20Kontext.dc.html'],
  ['drevo', 'PUAV%20N%C3%A1vod%20D%C5%99evo.dc.html'],
  ['pripojky', 'PUAV%20N%C3%A1vod%20P%C5%99%C3%ADpojky.dc.html'],
  ['storytelling', 'PUAV%20Klimatick%C3%BD%20Storytelling.dc.html'],
  ['oplatforme', 'PUAV%20O%20Platform%C4%9B.dc.html'],
];
(async () => {
  const browser = await chromium.launch();
  const page = await (await browser.newContext({ viewport: { width: 1366, height: 900 } })).newPage();
  await page.goto('file://' + SRC); await page.waitForSelector('h1'); await page.waitForTimeout(2000);
  // blob URL -> sha256 of content
  const blobHashes = await page.evaluate(async () => {
    const out = {};
    for (const [u, blob] of Object.entries(window.__resourceBlobs || {})) {
      const buf = await blob.arrayBuffer();
      const h = await crypto.subtle.digest('SHA-256', buf);
      out[u] = [...new Uint8Array(h)].map(b => b.toString(16).padStart(2, '0')).join('');
    }
    return out;
  });
  // hover rules and responsive rules
  const css = await page.evaluate(() => {
    let hover = [], resp = [];
    for (const s of document.styleSheets) {
      let rules; try { rules = [...s.cssRules]; } catch (e) { continue; }
      for (const r of rules) {
        if (r.selectorText && /^\.scp\d+:/.test(r.selectorText)) hover.push(r.cssText);
        if (r.media && r.conditionText && r.conditionText.includes('max-width: 640px')) {
          for (const rr of r.cssRules) resp.push({ sel: rr.selectorText, body: rr.style.cssText });
        }
      }
    }
    return { hover, resp };
  });
  fs.writeFileSync(OUT + '/blobhashes.json', JSON.stringify(blobHashes, null, 1));
  fs.writeFileSync(OUT + '/css.json', JSON.stringify(css, null, 1));
  for (const [name, href] of PAGES) {
    await page.evaluate((href) => { const a = document.createElement('a'); a.href = href; document.body.appendChild(a); a.click(); a.remove(); }, href);
    await page.waitForTimeout(1500);
    const html = await page.evaluate((resp) => {
      // tag elements targeted by responsive rules with stable classes
      resp.forEach((r, i) => { document.querySelectorAll(r.sel).forEach(el => el.classList.add('r' + i)); });
      const root = document.querySelector('#dc-root .sc-host');
      const clone = root.cloneNode(true);
      clone.querySelectorAll('[data-dc-tpl]').forEach(el => el.removeAttribute('data-dc-tpl'));
      clone.querySelectorAll('script').forEach(el => el.remove());
      resp.forEach((r, i) => { document.querySelectorAll('.r' + i).forEach(el => el.classList.remove('r' + i)); });
      const header = clone.querySelector('header');
      const footer = clone.querySelector('footer');
      const wrap = clone.querySelector('div[style*="overflow-x: hidden"]');
      const sections = [...clone.querySelectorAll('section')].filter(s => !s.parentElement.closest('section'));
      // sanity: any visible content outside header/sections/footer?
      const known = new Set([header, footer, ...sections]);
      const stray = [];
      clone.querySelectorAll('*').forEach(el => {
        if ([...known].some(k => k === el || k.contains(el))) return;
        if ([...known].some(k => el.contains(k))) return;
        if (el.textContent.trim() || el.tagName === 'IMG') stray.push(el.outerHTML.slice(0, 200));
      });
      return JSON.stringify({ wrapStyle: wrap.getAttribute('style'), header: header.outerHTML, sections: sections.map(s => s.outerHTML), footer: footer.outerHTML, stray });
    }, css.resp);
    const meta = await page.evaluate(() => ({ title: document.title, desc: document.querySelector('meta[name=description]').content }));
    fs.writeFileSync(`${OUT}/raw-${name}.json`, html);
    fs.writeFileSync(`${OUT}/meta-${name}.json`, JSON.stringify(meta));
    console.log(name, html.length, meta.title);
  }
  await browser.close();
})();
