import fs from 'node:fs';
import {spawn} from 'node:child_process';
import {chromium} from 'playwright';
import AxeBuilder from '@axe-core/playwright';
const out='docs/qa/vet-ebooks';fs.mkdirSync(out,{recursive:true});
const entries=JSON.parse(fs.readFileSync('data/vet-ebooks-books.json','utf8')).entries,base='http://127.0.0.1:4173',report={views:[],interactions:[],errors:[]};let server,browser;
const assert=(value,message)=>{if(!value)throw Error(message);};
try{
 server=spawn('python3',['scripts/qa-server.py',process.cwd()],{stdio:'ignore'});
 for(let i=0;i<50;i++){try{if((await fetch(base)).ok)break;}catch{}await new Promise(resolve=>setTimeout(resolve,100));}
 browser=await chromium.launch({args:['--no-sandbox']});
 const samples=entries.filter(e=>['minivet-guide','clinical-examination-of-farm-animals','bsava-manual-of-canine-and-feline-fracture-repair-and-management-2nd-edition'].includes(e.id));
 for(const theme of ['light','dark'])for(const width of [390,1280]){
  const context=await browser.newContext({viewport:{width,height:900},colorScheme:theme});await context.addInitScript(t=>localStorage.setItem('tvg-theme',t),theme);
  for(const entry of samples){
   const page=await context.newPage(),errors=[];page.on('pageerror',e=>errors.push(e.message));await page.goto(base+'/books/'+entry.id+'/');await page.evaluate(()=>document.fonts.ready);
   const button=page.locator('.book-download');assert(await button.isVisible(),'PDF button not visible');assert(await button.getAttribute('href')===entry.directPdf.url,'Incorrect direct PDF target');
   assert((await button.textContent()).includes('Download PDF'),'Download label');assert(await button.getAttribute('target')==='_blank','Download must preserve book page');
   assert(await page.locator('.book-access').textContent().then(t=>t.includes(entry.directPdf.sizeLabel)),'File size missing');
   assert(await page.locator('.book-study-uses li').count()===3,'Study focus missing');assert(await page.locator('.book-cover img').evaluate(i=>i.complete&&i.naturalWidth>0),'Broken cover');
   assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Horizontal overflow');
   const axe=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();assert(!axe.violations.length,'Accessibility: '+axe.violations.map(v=>v.id).join(','));assert(!errors.length,'JavaScript errors');
   if(entry.id==='minivet-guide'&&width===390)await page.screenshot({path:out+'/minivet-'+theme+'.png'});
   report.views.push({id:entry.id,theme,width,violations:axe.violations.length,errors});await page.close();
  }
  await context.close();
 }
 const context=await browser.newContext({viewport:{width:390,height:900}}),page=await context.newPage();await page.goto(base+'/books/');await page.locator('#books-query').fill('Vet eBooks');
 assert(await page.locator('[data-book-id]:visible').count()===24,'Provider search initial batch');await page.locator('#books-more').click();assert(await page.locator('[data-book-id]:visible').count()===25,'Provider search must expose exactly the 25 verified references');
 await page.locator('[data-book-id="minivet-guide"] a').click();await page.waitForURL('**/books/minivet-guide/');assert(await page.locator('.book-download').getAttribute('href')===entries.find(e=>e.id==='minivet-guide').directPdf.url,'Library-to-PDF journey');
 report.interactions.push('Provider search finds all 25 records, Show more exposes the final result, and the book card opens a canonical page with the correct direct PDF button.');await context.close();
}catch(error){report.errors.push(error.stack||String(error));process.exitCode=1;}
finally{if(browser)await browser.close();if(server)server.kill();fs.writeFileSync(out+'/browser.json',JSON.stringify(report,null,2)+'\n');console.log(JSON.stringify(report));}
