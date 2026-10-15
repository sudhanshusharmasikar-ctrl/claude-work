// Screenshot each exercise twice: the starter files and the tested solution, after a few
// clicks or key presses. usage: node shoot.js <starter exercises dir> <solved exercises dir> <out dir>
// Set PW_CHROMIUM=/path/to/chrome to use an already-installed Chromium.
const path = require('path');
let playwright;
try { playwright = require('playwright'); } catch (e) {
  playwright = require('/opt/node22/lib/node_modules/playwright');
}
const { chromium } = playwright;
const [, , STARTER, SOLVED, OUT] = process.argv;
const jobs = {
  '01-fix-the-form': { sel: '.card', act: async (p) => {
    await p.fill('#fullname', 'Ada Lovelace'); await p.fill('#email', 'ada@example.com');
    await p.fill('#password', 'secret123'); await p.click('button[type="submit"]'); await p.focus('#email'); } },
  '02-style-the-profile-card': { sel: '.page', act: null },
  '03-click-counter': { sel: '.card', act: async (p) => { for (let i = 0; i < 3; i++) await p.click('#increment'); } },
  '04-center-it': { sel: '.stages', act: null },
  '05-ecommerce-search-box': { sel: '.card', act: async (p) => { await p.fill('#search', 'apple'); } },
  '06-todo-list': { sel: '.card', act: async (p) => {
    for (const t of ['Buy milk', 'Revise flexbox']) { await p.fill('#todo-input', t); await p.click('#todo-form button'); }
    await p.locator('.todo-toggle').first().click(); } },
  '07-form-validation': { sel: '.card', act: async (p) => {
    await p.fill('#username', 'ada'); await p.fill('#email', 'not-an-email'); await p.fill('#password', '123');
    await p.click('button[type="submit"]'); } },
  '08-show-hide-password': { sel: '.card', act: async (p) => { await p.fill('#password', 'secret123'); await p.click('#toggle-password'); } },
  '09-dark-mode-toggle': { sel: 'body', act: async (p) => { await p.click('#theme-toggle'); await p.waitForTimeout(400); } },
  '13-accordion': { sel: '.page', act: async (p) => { await p.locator('.accordion-header').nth(1).click(); } },
  '14-tab-switcher': { sel: '.card', act: async (p) => { await p.click('.tab[data-tab="features"]'); } },
  '15-dynamic-table': { sel: '.card', act: async (p) => { await p.click('#sort-age'); } },
  '16-image-carousel': { sel: '.carousel', act: async (p) => { await p.click('#next'); } },
  '17-live-clock': { sel: '.card', act: async (p) => { await p.waitForTimeout(300); } },
};
(async () => {
  const exe = process.env.PW_CHROMIUM;
  const browser = await chromium.launch(exe ? { executablePath: exe } : {});
  for (const [ex, job] of Object.entries(jobs)) {
    for (const which of ['before', 'after']) {
      const root = which === 'before' ? STARTER : SOLVED;
      const vw = ex === '04-center-it' ? 760 : 600;
      const vh = ex === '02-style-the-profile-card' ? 470 : 640;
      const page = await browser.newPage({ viewport: { width: vw, height: vh }, deviceScaleFactor: 2 });
      await page.goto('file://' + path.join(root, ex, 'index.html'));
      if (which === 'after' && job.act) await job.act(page);
      await page.mouse.move(1, 1);
      if (ex === '09-dark-mode-toggle') await page.setViewportSize({ width: 600, height: 300 });
      const el = page.locator(job.sel).first();
      await el.screenshot({ path: path.join(OUT, `${ex}-${which}.png`) });
      await page.close();
    }
  }
  await browser.close();
  console.log('done');
})();
