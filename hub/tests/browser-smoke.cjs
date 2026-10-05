const {chromium}=require('playwright');
const fs=require('fs');
const assert=require('node:assert/strict');
(async()=>{
const browser=await chromium.launch({executablePath:process.env.CHROMIUM_PATH||'/usr/bin/chromium',headless:true,args:['--no-sandbox']});
const ctx=await browser.newContext({viewport:{width:1440,height:1000},acceptDownloads:true});
const page=await ctx.newPage(),errors=[],external=[];
page.on('pageerror',e=>errors.push(e.message));
page.on('request',r=>{if(!r.url().startsWith('http://127.0.0.1:8080')&&!r.url().startsWith('data:'))external.push(r.url())});
await page.goto('http://127.0.0.1:8080');await page.waitForSelector('.stats-grid');
assert.match(await page.locator('.stat-card').first().innerText(),/49/);
for(const route of ['projects','agents','sites','games','bots','files','databases','deploys','analytics','settings','services','github','graph','tasks','logs','alerts']){
 await page.goto('http://127.0.0.1:8080/#'+route);await page.waitForTimeout(100);
 assert.ok(await page.locator('main').innerText(),route);
 const overflow=await page.evaluate(()=>document.body.scrollWidth>innerWidth+1);
 assert.equal(overflow,false,'Desktop overflow '+route);
}
await page.goto('http://127.0.0.1:8080/#projects');
assert.equal(await page.locator('.project-tile').count(),49);
await page.locator('[data-projectfilter="lost"]').click();assert.equal(await page.locator('.project-tile').count(),2);
await page.locator('.project-tile').first().click();await page.waitForSelector('dialog[open]');assert.match(await page.locator('dialog').innerText(),/Файлы утрачены/);await page.keyboard.press('Escape');
await page.locator('#global-search').fill('Beaver');assert.ok(await page.locator('.project-tile').count());
await page.locator('#global-search').fill('/srv/projects');assert.ok(await page.locator('.project-tile').count());
await page.locator('#global-search').fill('');
await page.locator('[data-action="new-project"]').first().click();
await page.locator('input[name="name"]').fill('Тестовый <проект>');await page.locator('textarea[name="note"]').fill('Локальная проверка');await page.locator('#project-form button[type="submit"]').click();
await page.reload();await page.waitForSelector('main');
await page.locator('#global-search').fill('Тестовый');assert.equal(await page.locator('.project-tile').count(),1);
await page.locator('.project-tile').click();assert.match(await page.locator('dialog').innerText(),/Тестовый <проект>/);
await page.locator('[data-action^="task-for:"]').click();await page.locator('input[name="title"]').fill('Проверить восстановление');await page.locator('#task-form button[type="submit"]').click();
await page.goto('http://127.0.0.1:8080/#tasks');await page.locator('[data-task]').check();await page.reload();await page.waitForSelector('[data-task]');assert.equal(await page.locator('[data-task]').isChecked(),true);
await page.goto('http://127.0.0.1:8080/#databases');await page.locator('[data-dbfilter="postgres"]').click();await page.locator('.database-card').filter({has:page.getByRole('heading',{name:'sentra',exact:true})}).click();
await page.locator('#table-search').fill('accounts');assert.ok(await page.locator('.schema-table:visible').count());await page.locator('.schema-table:visible summary').first().click();assert.ok(await page.locator('.schema-table[open] tbody tr').count());await page.keyboard.press('Escape');
await page.goto('http://127.0.0.1:8080/#graph');assert.equal(await page.locator('.graph-node').count(),129);await page.locator('[data-graphnode="project:kabluk"]').click();assert.ok(await page.locator('.graph-node').count()<129);await page.locator('[data-node-details]').click();assert.match(await page.locator('dialog').innerText(),/Каблук|Kabluk/);await page.keyboard.press('Escape');
await page.goto('http://127.0.0.1:8080/#settings');
const [download]=await Promise.all([page.waitForEvent('download'),page.locator('[data-action="export"]').click()]);const path=await download.path();const backup=JSON.parse(fs.readFileSync(path));assert.equal(backup.snapshot.catalog.projects.length,49);assert.equal(backup.projects.length,1);assert.equal(backup.tasks.length,1);
await page.locator('#import-file').setInputFiles({name:'broken.json',mimeType:'application/json',buffer:Buffer.from('{"version":1}')});await page.waitForTimeout(100);assert.match(await page.locator('#toast').innerText(),/отменён/);assert.match(await page.locator('main').innerText(),/Настройки/);
await page.locator('#import-file').setInputFiles({name:'backup.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(backup))});await page.waitForTimeout(200);assert.match(await page.locator('#toast').innerText(),/импортирован/);
await page.goto('http://127.0.0.1:8080/#home');await page.locator('[data-mapfilter="agents"]').click();assert.equal(await page.locator('.map-node').count(),4);await page.locator('[data-mapfilter="all"]').click();assert.equal(await page.locator('.map-node').count(),12);
// Reload with all internet destinations blocked: every local dependency must still work.
await ctx.route('**/*',r=>r.request().url().startsWith('http://127.0.0.1:8080')?r.continue():r.abort());await page.reload();await page.waitForSelector('.stats-grid');
await page.screenshot({path:'/workspace/vovan-os/tests/desktop.png',fullPage:true});
await page.setViewportSize({width:390,height:844});await page.goto('http://127.0.0.1:8080/#home');await page.waitForSelector('.stats-grid');await page.waitForTimeout(350);console.log('mobile dimensions',await page.evaluate(()=>[innerWidth,document.body.scrollWidth]));assert.equal(await page.evaluate(()=>document.body.scrollWidth>innerWidth+1),false,'Mobile overflow');
await page.screenshot({path:'/workspace/vovan-os/tests/mobile.png',fullPage:true});
await page.locator('[data-action="menu"]').click();await page.locator('.nav-item[href="#databases"]').click();await page.waitForSelector('.database-card');assert.equal(await page.locator('body').getAttribute('class'),'');assert.ok(await page.locator('.database-card').count());
for(const route of ['projects','files','analytics','settings','graph']){await page.goto('http://127.0.0.1:8080/#'+route);await page.waitForTimeout(100);assert.equal(await page.evaluate(()=>document.body.scrollWidth>innerWidth+1),false,'Mobile overflow '+route)}
assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
console.log('PASS: 16 routes, 49 projects, 129 graph nodes, database search, local project/task persistence, export/import, responsive layouts, no external requests.');
await browser.close();
})().catch(e=>{console.error(e);process.exit(1)});
