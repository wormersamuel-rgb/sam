const { chromium } = require('playwright');
(async () => {
  const [src, pdf, pngdir] = process.argv.slice(2);
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1920, height: 1080 } });
  await p.goto('file://' + src); await p.evaluate(() => document.fonts.ready); await p.waitForTimeout(300);
  await p.evaluate(() => place());
  const n = await p.locator('.slide').count();
  for (let i = 0; i < n; i++) await p.locator('.slide').nth(i).screenshot({ path: `${pngdir}/s${i+1}.png` });
  await p.emulateMedia({ media: 'print' });
  await p.pdf({ path: pdf, width: '1920px', height: '1080px', printBackground: true, preferCSSPageSize: true });
  await b.close();
})();
