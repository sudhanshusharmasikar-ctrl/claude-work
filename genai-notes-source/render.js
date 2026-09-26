// Render an HTML file to PDF with headless Chromium (Playwright).
// usage: node render.js notes.html out.pdf
const path = require('path');
let playwright;
try { playwright = require('playwright'); } catch (e) {
  playwright = require('/opt/node22/lib/node_modules/playwright');
}

(async () => {
  const [, , input, output] = process.argv;
  const browser = await playwright.chromium.launch();
  const page = await browser.newPage();
  await page.goto('file://' + path.resolve(input), { waitUntil: 'networkidle' });
  await page.evaluate(() => document.fonts.ready);
  await page.pdf({
    path: output,
    preferCSSPageSize: true,
    printBackground: true,
    outline: true,
    tagged: true,
  });
  await browser.close();
  console.log('rendered', output);
})();
