/* Check keyword-facing headings without losing compact layouts or static navigation. */
import fs from 'node:fs';
import {spawn} from 'node:child_process';
import {chromium} from 'playwright';
import AxeBuilder from '@axe-core/playwright';
const out='docs/qa/keyword-visibility',base='http://127.0.0.1:4173';fs.mkdirSync(out,{recursive:true});
const paths=['/','/books/','/bvsc/','/bvsc/year-4/','/bvsc/year-3/veterinary-and-animal-husbandry-extension-education/','/bvsc/year-4/veterinary-clinical-practices-ii/'];
const report={views:[],interactions:[],errors:[]};let server,browser;
const assert=(ok,message)=>{if(!ok)throw Error(message);};
try{
 server=spawn('python3',['scripts/qa-server.py',process.cwd()],{stdio:'ignore'});
 for(let n=0;n<50;n++){try{if((await fetch(base)).ok)break;}catch{}await new Promise(r=>setTimeout(r,100));}
 browser=await chromium.launch({args:['--no-sandbox']});
 for(const theme of ['light','dark'])for(const width of [360,1280]){
  const context=await browser.newContext({viewport:{width,height:900},colorScheme:theme});await context.addInitScript(t=>localStorage.setItem('tvg-theme',t),theme);
  for(const path of paths){
   const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(base+path);await page.evaluate(()=>document.fonts.ready);
   const geometry=await page.evaluate(()=>{const visible=e=>!e.closest('.sr-only')&&e.checkVisibility()&&e.getBoundingClientRect().height>0;return {overflow:document.documentElement.scrollWidth>innerWidth,h1:[...document.querySelectorAll('h1')].map(e=>e.textContent),clipped:[...document.querySelectorAll('h1,h2,h3,p')].filter(visible).filter(e=>e.scrollWidth>e.clientWidth+1).map(e=>e.textContent),small:[...document.querySelectorAll('a,button,input,summary')].filter(visible).filter(e=>{const r=e.getBoundingClientRect();return r.width<47.5||r.height<47.5;}).map(e=>e.textContent.trim().slice(0,60))};});
   const axe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();
   assert(!geometry.overflow&&!geometry.clipped.length&&!geometry.small.length,'Layout or tap targets: '+JSON.stringify({path,theme,width,geometry}));
   assert(geometry.h1.length===1&&!geometry.h1[0].includes('&amp;'),'One readable main heading: '+path);
   assert(!axe.violations.length&&!errors.length,'Accessibility or JavaScript: '+path+' '+JSON.stringify(axe.violations.map(v=>v.id)));
   if(width===360&&['/','/books/'].includes(path))await page.screenshot({path:out+'/'+(path==='/'?'home':'books')+'-'+theme+'.png'});
   report.views.push({path,theme,width,title:await page.title(),geometry,violations:axe.violations.length,errors});await page.close();
  }
  await context.close();
 }
 const context=await browser.newContext({javaScriptEnabled:false,viewport:{width:360,height:900}}),page=await context.newPage();
 await page.goto(base);await page.locator('.resource-shortcuts a[href="/books/"]').click();await page.waitForURL('**/books/');
 assert(await page.locator('[data-book-id]:visible').count()===119,'All books must remain crawlable without JavaScript');
 await page.locator('[data-book-id="minivet-guide"] a').click();await page.waitForURL('**/books/minivet-guide/');assert(await page.locator('.book-download').isVisible(),'Book action missing');
 await page.goto(base);await page.locator('.resource-shortcuts a[href="/bvsc/"]').click();await page.waitForURL('**/bvsc/');
 await page.locator('a.bvsc-subject-tile[href="/bvsc/year-1/veterinary-anatomy/"]').click();await page.waitForURL('**/bvsc/year-1/veterinary-anatomy/');
 assert(await page.locator('h1').textContent()==='Veterinary Anatomy Notes','Subject notes heading');assert(await page.locator('[data-resource-id]').count()>0,'Source notes missing');
 await context.close();report.interactions.push('No JavaScript: home shortcut → all 119 books → MiniVet detail and download action; home shortcut → BVSc subjects → Anatomy notes.');
}catch(error){report.errors.push(error.stack||String(error));process.exitCode=1;}
finally{if(browser)await browser.close();if(server)server.kill();fs.writeFileSync(out+'/browser.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify({views:report.views.length,errors:report.errors,interactions:report.interactions}));}
