/* Focused visual/content checks for the two finalized collection pages. */
import fs from 'node:fs';import {spawn} from 'node:child_process';import {chromium} from 'playwright';import AxeBuilder from '@axe-core/playwright';
const out='docs/qa/collection-cards';fs.mkdirSync(out,{recursive:true});const source=JSON.parse(fs.readFileSync('data/collections.json')).resources;const base=process.env.QA_BASE_URL||'http://127.0.0.1:4173';let server,browser;const report={views:[],errors:[]};
try{
 if(!process.env.QA_BASE_URL){server=spawn('python3',['scripts/qa-server.py',process.cwd()],{stdio:'ignore'});for(let n=0;n<50;n++){try{if((await fetch(base)).ok)break}catch{}await new Promise(r=>setTimeout(r,100))}}
 browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 for(const theme of ['light','dark'])for(const width of [360,390,430,768,1280]){
  const c=await browser.newContext({viewport:{width,height:844},colorScheme:theme});await c.addInitScript(t=>localStorage.setItem('tvg-theme',t),theme);const p=await c.newPage();
  for(const collection of ['objective-notes','question-banks','drug-index']){
   const drug=collection==='drug-index';await p.goto(base+(drug?'/clinical/drug-index/':'/objective/'),{waitUntil:'networkidle'});await p.evaluate(()=>document.fonts.ready);
   if(!drug)await p.locator('#objective-page-tab-'+(collection==='question-banks'?1:0)).click();
   await p.waitForTimeout(280);
   const cards=p.locator('.rx-book-card:visible'),expected=source.filter(r=>r.collection===collection);if(await cards.count()!==expected.length)throw Error('Collection count changed '+collection);
   for(let i=0;i<expected.length;i++){const card=cards.nth(i),r=expected[i];if(await card.locator('.rx-book-number').textContent()!=='#'+(i+1))throw Error('Numbering '+collection);if(await card.locator('h3').textContent()!==r.title||await card.locator('.rx-book-description').textContent()!==r.description)throw Error('Content changed '+r.id);if(await card.locator('a').count()!==1||await card.locator('a').getAttribute('href')!==r.url||await card.locator('.open-label').textContent()!=='Open Book')throw Error('CTA or URL changed '+r.id)}
   if(await p.locator('form[role=search]').count())throw Error('Unrequested search strip');
   const geometry=await p.evaluate(()=>({overflow:document.documentElement.scrollWidth>innerWidth,clipped:[...document.querySelectorAll('.rx-book-card h3,.rx-book-description')].filter(e=>e.checkVisibility()&&e.scrollWidth>e.clientWidth+1).map(e=>e.textContent),small:[...document.querySelectorAll('.rx-book-card a')].filter(e=>e.checkVisibility()).filter(e=>{const r=e.getBoundingClientRect();return r.width<47.5||r.height<47.5}).length}));
   const axe=await new AxeBuilder({page:p}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();const serious=axe.violations.filter(v=>['serious','critical'].includes(v.impact));report.views.push({collection,theme,width,geometry,violations:serious});if(geometry.overflow||geometry.clipped.length||geometry.small||serious.length)report.errors.push({collection,theme,width,geometry,violations:serious});
   await p.evaluate(()=>scrollTo(0,0));await p.screenshot({path:`${out}/${collection}-${theme}-${width}.png`,fullPage:true,animations:'disabled'});
   if(width===390&&theme==='light'){const shot=await p.screenshot({type:'jpeg',quality:75,fullPage:true});console.log('COLLECTION_PREVIEW '+JSON.stringify({collection,theme,width,data:shot.toString('base64')}))}
  }
  await p.goto(base+'/objective/');await p.locator('#objective-page-tab-0').focus();await p.keyboard.press('ArrowRight');if(await p.locator('#objective-page-tab-1').getAttribute('aria-selected')!=='true')throw Error('Keyboard tabs');await p.keyboard.press('Home');if(await p.locator('#objective-page-tab-0').getAttribute('aria-selected')!=='true')throw Error('Keyboard Home');await c.close();
 }
 const c=await browser.newContext({javaScriptEnabled:false,viewport:{width:360,height:844}}),p=await c.newPage();await p.goto(base+'/objective/');if(await p.locator('.rx-book-card:visible').count()!==10)throw Error('No-JS collections unavailable');await c.close();
}catch(e){report.errors.push(e.stack||String(e))}finally{if(browser)await browser.close();if(server)server.kill();fs.writeFileSync(out+'/report.json',JSON.stringify(report,null,2));console.log('COLLECTION_SUMMARY '+JSON.stringify({views:report.views.length,errors:report.errors}));if(report.errors.length)process.exitCode=1}
