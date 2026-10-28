/* Canonical book routes, real covers, responsive geometry and download destinations. */
import fs from 'node:fs';import {spawn} from 'node:child_process';import {chromium} from 'playwright';import AxeBuilder from '@axe-core/playwright';
const books=JSON.parse(fs.readFileSync('data/books.json')),base='http://127.0.0.1:4173',out='docs/qa/book-pages';fs.mkdirSync(out,{recursive:true});
const examples=['animal-nutrition','dhruv-desai','plumbs-handbook','primary-veterinary-anatomy','textbook-of-veterinary-internal-medicine','applied-nutrition-d-v-reddy'];
const report={views:[],errors:[],interactions:[]};let browser,server;
try{
 server=spawn('python3',['scripts/qa-server.py',process.cwd()],{stdio:'ignore'});for(let n=0;n<50;n++){try{if((await fetch(base)).ok)break}catch{}await new Promise(r=>setTimeout(r,100))}
 browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 for(const theme of ['light','dark'])for(const width of [360,390,430,768,1280]){
  const c=await browser.newContext({viewport:{width,height:844},colorScheme:theme});await c.addInitScript(t=>localStorage.setItem('tvg-theme',t),theme);const p=await c.newPage(),errors=[];p.on('pageerror',e=>errors.push(e.message));
  for(const b of width===390?books:books.filter(b=>examples.includes(b.id))){
   errors.length=0;await p.goto(base+b.page,{waitUntil:'load'});await p.evaluate(()=>document.fonts.ready);
   const geometry=await p.evaluate(()=>{const visible=e=>!e.closest('.sr-only')&&e.checkVisibility()&&e.getBoundingClientRect().height>0;return{width:innerWidth,documentWidth:document.documentElement.scrollWidth,h1:document.querySelectorAll('h1').length,clipped:[...document.querySelectorAll('h1,h2,h3,p,dd')].filter(visible).filter(e=>e.scrollWidth>e.clientWidth+1).map(e=>e.textContent.slice(0,70)),small:[...document.querySelectorAll('a,button,input,summary')].filter(visible).filter(e=>{const r=e.getBoundingClientRect();return r.width<47.5||r.height<47.5}).map(e=>({text:e.textContent.slice(0,60),w:e.getBoundingClientRect().width,h:e.getBoundingClientRect().height})),images:[...document.querySelectorAll('.book-cover img')].filter(e=>!e.complete||!e.naturalWidth).length}});
   if(geometry.documentWidth>width||geometry.h1!==1||geometry.clipped.length||geometry.small.length||geometry.images||errors.length)report.errors.push({path:b.page,theme,width,geometry,errors:[...errors]});
   if(examples.includes(b.id)){
    const axe=await new AxeBuilder({page:p}).withTags(['wcag2a','wcag2aa','wcag21a','wcag21aa']).analyze();const violations=axe.violations.filter(v=>['serious','critical'].includes(v.impact)).map(v=>({id:v.id,nodes:v.nodes.slice(0,3).map(n=>({target:n.target,summary:n.failureSummary}))}));if(violations.length)report.errors.push({path:b.page,theme,width,violations});
    if([390,1280].includes(width)){await p.screenshot({path:`${out}/${b.id}-${theme}-${width}.png`,fullPage:true,animations:'disabled'});if(theme==='light'&&width===390){const shot=await p.screenshot({type:'jpeg',quality:65});console.log('BOOK_PREVIEW '+JSON.stringify({id:b.id,theme,width,data:shot.toString('base64')}))}}
   }
   const button=p.locator('.book-download');if((await button.textContent()).trim().replace(/\s+/g,' ')!==b.downloadLabel)throw Error('Access label '+b.id);if(b.primaryUrl&&await button.getAttribute('href')!==b.primaryUrl)throw Error('Access URL '+b.id);
   report.views.push({path:b.page,theme,width,geometry});
  }await c.close();
 }
 const c=await browser.newContext({viewport:{width:390,height:844}}),p=await c.newPage();
 await p.goto(base+'/bvsc/year-1/veterinary-physiology/#books');await p.locator('#books .year-book-link').first().click();await p.waitForURL('**/books/**');if(!await p.locator('.book-download').isVisible())throw Error('Subject-to-book navigation');
 await p.goto(base+'/objective/');await p.locator('.rx-book-card a').first().click();await p.waitForURL('**/books/dhruv-desai/');if(!await p.locator('.book-download').getAttribute('href').then(s=>s.startsWith('https://t.me/')))throw Error('Telegram mapping');
 await p.goto(base+'/clinical/handbooks/');await p.locator('.rx-book-card a').first().click();await p.waitForURL('**/books/ultimate-vet-handbook/');
 await p.goto(base+'/bvsc/year-4/veterinary-surgery-and-radiology/#books');if(await p.locator('#books .year-book-link').count()>=12){await p.locator('.collection-query').fill('ophthalmology');if(await p.locator('#books .year-book-link:visible').count()!==1)throw Error('Book author/title search');}
 await p.goto(base+'/search/?q=Animal%20Nutrition');await p.waitForSelector('#page-results a[href^="/books/"]');
 await p.goto(base+'/books/');await p.locator('.book-directory-card a').first().click();await p.waitForURL('**/books/**');
 await c.close();const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:360,height:844}}),n=await nojs.newPage();for(const b of books.filter(b=>examples.includes(b.id))){await n.goto(base+b.page);if(!await n.locator('.book-download').isVisible())throw Error('No-JS download '+b.id);await n.locator('.book-source-details>summary').click();if(!await n.locator('.book-source-details').evaluate(e=>e.open))throw Error('No-JS source details');}await nojs.close();
 report.interactions.push('All book pages in two themes at 390px; six representative pages at 360/430/768/1280px; exact provider labels/URLs; source images; objective, handbook, subject and search navigation; title/author filtering; no-JS access and source disclosure.');
}catch(e){report.errors.push(e.stack||String(e))}finally{if(browser)await browser.close();if(server)server.kill();fs.writeFileSync(out+'/browser-report.json',JSON.stringify(report,null,2));console.log('BOOK_QA '+JSON.stringify({views:report.views.length,errors:report.errors,interactions:report.interactions}));if(report.errors.length)process.exitCode=1}
