import fs from 'node:fs';
import {spawn} from 'node:child_process';
import {chromium} from 'playwright';
import AxeBuilder from '@axe-core/playwright';
const out='docs/qa/books-library';fs.mkdirSync(out,{recursive:true});
const base='http://127.0.0.1:4173',report={views:[],interactions:[],errors:[]};let browser,server;
const assert=(ok,message)=>{if(!ok)throw Error(message);};
try{
 server=spawn('python3',['scripts/qa-server.py',process.cwd()],{stdio:'ignore'});
 for(let i=0;i<50;i++){try{if((await fetch(base)).ok)break;}catch{}await new Promise(resolve=>setTimeout(resolve,100));}
 browser=await chromium.launch({args:['--no-sandbox']});
 const books=JSON.parse(fs.readFileSync('data/books.json','utf8'));
 for(const theme of ['light','dark'])for(const width of [360,390,430,768,1280]){
  const context=await browser.newContext({viewport:{width,height:900},colorScheme:theme});
  await context.addInitScript(t=>localStorage.setItem('tvg-theme',t),theme);
  const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));
  await page.goto(base+'/books/');await page.evaluate(()=>document.fonts.ready);
  const ids=await page.locator('[data-book-id]').evaluateAll(nodes=>nodes.map(n=>n.dataset.bookId));
  assert(ids.length===books.length&&new Set(ids).size===books.length,'Catalogue coverage');
  assert(await page.locator('[data-book-id]:visible').count()===24,'Compact initial book batch');
  assert(await page.locator('.bottom-nav a[aria-current=page]').textContent()==='Books','Books active navigation');
  assert(await page.locator('.bottom-nav a[href="/search/"]').count()===0,'Search remains in the bottom bar');
  const geometry=await page.evaluate(()=>({viewport:innerWidth,document:document.documentElement.scrollWidth,h1:document.querySelectorAll('h1').length,clipped:[...document.querySelectorAll('.subject-book-card strong')].filter(e=>e.scrollWidth>e.clientWidth+1&&getComputedStyle(e).overflow!=='hidden').map(e=>e.textContent)}));
  assert(geometry.document<=width&&geometry.h1===1&&!geometry.clipped.length,'Library layout '+width+' '+JSON.stringify(geometry));
  const axe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
  if(axe.violations.length){console.log(JSON.stringify(axe.violations.map(v=>({id:v.id,nodes:v.nodes.map(n=>({target:n.target,summary:n.failureSummary}))}))));await page.screenshot({path:out+'/failure.png'});}
  assert(!axe.violations.length,'Accessibility '+theme+' '+width+': '+axe.violations.map(v=>v.id).join(','));
  assert(!errors.length,'JavaScript errors');
  if([390,1280].includes(width))await page.screenshot({path:out+'/'+theme+'-'+width+'.png',animations:'disabled'});
  report.views.push({theme,width,books:ids.length,geometry,violations:axe.violations.length,errors});
  await context.close();
 }
 const context=await browser.newContext({viewport:{width:390,height:900}}),page=await context.newPage();
 await page.goto(base+'/');await page.locator('.bottom-nav a[href="/books/"]').click();await page.waitForURL('**/books/');
 await page.locator('#books-query').fill('cardiology');assert(await page.locator('[data-book-id]:visible').count()===1,'Title search');
 await page.locator('[data-book-id]:visible a').click();await page.waitForURL('**/books/manual-of-canine-and-feline-cardiology/');assert(await page.locator('.book-download').isVisible(),'Book detail access');
 assert(await page.locator('.bottom-nav a[href="/books/"][aria-current=page]').count()===1,'Book detail navigation');
 await page.goto(base+'/books/');await page.locator('#books-query').fill('zzzzNoSuchBook');assert(await page.locator('#books-empty').isVisible(),'Empty state');
 await page.locator('#books-clear').click();assert(await page.locator('[data-book-id]:visible').count()===24,'Clear restores compact initial batch');
 await page.locator('#books-query').fill('McDonald');assert(await page.locator('[data-book-id]:visible').count()>0,'Author search');
 await page.locator('#books-query').press('Escape');assert(await page.locator('[data-book-id]:visible').count()===24,'Escape clears search');
 await page.locator('#books-query').fill('veterinary anatomy');assert(await page.locator('[data-book-id]:visible').count()>=6,'Subject search');
 await page.locator('#books-clear').click();
 await page.locator('.books-filter[data-book-category="clinical"]').click();assert(await page.locator('[data-book-id]:visible').count()===24,'Clinical category first batch');
 assert(await page.locator('[data-book-id]:visible').evaluateAll(nodes=>nodes.every(n=>n.dataset.bookCategory==='clinical')),'Category isolation');
 await page.locator('#books-more').click();const clinicalCount=await page.locator('[data-book-id][data-book-category=clinical]').count();assert(await page.locator('[data-book-id]:visible').count()===Math.min(48,clinicalCount),'More reveals the next clinical batch');
 await page.locator('.books-filter[data-book-category="exam-prep"]').focus();await page.keyboard.press('Space');assert(await page.locator('[data-book-id]:visible').count()===10,'Keyboard category selection');
 await page.locator('.books-filter[data-book-category="all"]').click();
 while(await page.locator('#books-more').isVisible())await page.locator('#books-more').click();
 assert(await page.locator('[data-book-id]:visible').count()===books.length,'All books reachable through Show more');
 await page.locator('.bottom-nav [data-dialog="more-sheet"]').click();assert(await page.locator('#more-sheet a[href="/search/"]').isVisible(),'Search available in More');
 report.interactions.push('Bottom navigation to Books; book/detail navigation; title, author and subject filters; empty state; Clear and Escape reset; category filters and keyboard selection; Show more reaches the entire catalogue; search available from More.');
 await context.close();
 const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:360,height:900}}),n=await nojs.newPage();await n.goto(base+'/books/');
 assert(await n.locator('[data-book-id]:visible').count()===books.length,'No-JavaScript catalogue');
 await n.locator('.books-category-links a[href="#exam-prep"]').click();assert(new URL(n.url()).hash==='#exam-prep','No-JavaScript category navigation');
 await n.locator('#exam-prep [data-book-id] a').first().click();await n.waitForURL('**/books/*/');assert(await n.locator('.book-download').isVisible(),'No-JavaScript detail access');
 await nojs.close();report.interactions.push('The entire catalogue, category jumps and book detail access work with JavaScript disabled.');
}catch(error){report.errors.push(error.stack||String(error));process.exitCode=1;}
finally{if(browser)await browser.close();if(server)server.kill();fs.writeFileSync(out+'/browser.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));}
