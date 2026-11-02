/* Check the entire new Drive collection and the reported book disclosure bug. */
import fs from 'node:fs';import {spawn} from 'node:child_process';import {chromium} from 'playwright';import AxeBuilder from '@axe-core/playwright';
const source=JSON.parse(fs.readFileSync('data/tanuvas-source.json')),resources=JSON.parse(fs.readFileSync('data/resources.json')).files,books=JSON.parse(fs.readFileSync('data/books.json'));
const out='docs/qa/tanuvas-drive',base=process.env.QA_BASE_URL||'http://127.0.0.1:4173';fs.mkdirSync(out,{recursive:true});
const report={subjects:[],books:[],downloads:[],errors:[]},assert=(x,m)=>{if(!x)throw Error(m)};let browser,server;
const route=f=>resources.find(r=>r.id===source.notes.find(n=>n.folderId===f.id).id).page;
try{
 if(!process.env.QA_BASE_URL){server=spawn('python3',['scripts/qa-server.py',process.cwd()],{stdio:'ignore'});for(let i=0;i<50;i++){try{if((await fetch(base)).ok)break}catch{}await new Promise(r=>setTimeout(r,100))}}
 browser=await chromium.launch({args:['--no-sandbox']});
 for(const width of [360,1280])for(const theme of ['light','dark']){
  const c=await browser.newContext({viewport:{width,height:844},reducedMotion:'reduce'});await c.addInitScript(t=>localStorage.setItem('tvg-theme',t),theme);const p=await c.newPage();p.on('pageerror',e=>report.errors.push(e.message));
  await p.goto(base+'/bvsc/tanuvas-notes/');assert(await p.locator('[data-tanuvas-course]').count()===source.notes.length,'Directory missing files');assert(await p.locator('#year-4').count()===1,'Fourth year absent');assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Directory overflow');
  const axe=await new AxeBuilder({page:p}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();assert(!axe.violations.length,'Directory accessibility '+JSON.stringify(axe.violations.map(v=>v.id)));
  if(width===360)await p.screenshot({path:out+'/directory-'+theme+'.png',fullPage:false});
  for(const f of source.subjectFolders){
   const path=route(f),expected=source.notes.filter(n=>n.folderId===f.id).sort((a,b)=>a.sourceOrder-b.sourceOrder);await p.goto(base+path);assert(!await p.locator('#tanuvas').isVisible(),'TANUVAS starts expanded');
   await p.locator('[data-note-option="tanuvas"]').click();await p.locator('#tanuvas').waitFor({state:'visible'});
   const actual=await p.locator('#tanuvas [data-resource-id]').evaluateAll(es=>es.map(e=>({id:e.dataset.resourceId,title:e.querySelector('.file-title>span').textContent,url:e.querySelector('.file-open').getAttribute('href')})));
   assert(JSON.stringify(actual)===JSON.stringify(expected.map(n=>({id:n.id,title:n.title,url:n.url}))),path+' wrong titles/order/URLs');
   assert(await p.locator('#tanuvas').evaluate(e=>e.getBoundingClientRect().bottom<=document.querySelector('.subject-practical-link').getBoundingClientRect().top),path+' notes below Practical Vault');
   assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),path+' overflow');
   await p.goto(base+path+'#file-'+expected.at(-1).id);await p.locator('#file-'+expected.at(-1).id).waitFor({state:'visible'});
   if(f.subject==='Veterinary Medicine'&&width===360)await p.screenshot({path:out+'/medicine-'+theme+'.png',fullPage:false});
   report.subjects.push({path,width,theme,files:expected.length});
  }
  for(const f of source.subjectFolders){
   const own=books.filter(b=>b.subjects.some(s=>s.year===f.year&&s.name===f.subject));if(!own.length)continue;
   const path=route(f);await p.goto(base+path+'#books');const more=p.locator('.subject-more-books');
   if(own.length<=8){assert(!await more.count(),path+' unnecessary disclosure');assert(await p.locator('.subject-book-card:visible').count()===own.length,path+' small shelf hides books')}
   else{assert(await p.locator('.subject-book-card:visible').count()===6,'Closed disclosure leaking content');await more.locator('summary').click();assert((await more.locator('summary').innerText()).trim()==='Show fewer books','Expanded label incorrect');assert(await p.locator('.subject-book-card:visible').count()===own.length,'Expanded shelf missing books');await more.locator('summary').click();assert((await more.locator('summary').innerText()).includes('Show '+(own.length-6)+' more books'),'Collapsed label incorrect')}
   if(f.subject==='Livestock Products Technology'&&width===360){await p.locator('.subject-book-card').last().scrollIntoViewIfNeeded();await p.screenshot({path:out+'/books-'+theme+'.png',fullPage:false})}
   if(own.length>12){await p.locator('#subject-book-query').fill(own.at(-1).title);assert(await p.locator('.subject-book-card:visible').count()>0,'Book search hides result');assert(await more.getAttribute('open')!==null,'Search does not expand shelf');await p.locator('#subject-book-query').fill('');assert(await p.locator('.subject-book-card:visible').count()===6,'Clear search failed')}
   report.books.push({path,width,theme,count:own.length});
  }
  await c.close();
 }
 const c=await browser.newContext({viewport:{width:360,height:844}}),p=await c.newPage();
 for(const b of books.filter(b=>b.primaryUrl?.startsWith('https://drive.google.com/'))){await p.goto(base+b.page);const button=p.locator('.book-download');assert(await button.getAttribute('href')===b.primaryUrl,'Wrong book download');assert((await button.innerText()).includes('Google Drive'),'Wrong provider label');report.downloads.push(b.id)}
 const legacy=source.legacyAnchors[0],f=source.subjectFolders.find(f=>f.year===legacy.year&&f.subject===legacy.subject);await p.goto(base+route(f)+'#file-'+legacy.id);await p.locator('#tanuvas').waitFor({state:'visible'});await c.close();
 const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:360,height:844}}),n=await nojs.newPage();await n.goto(base+route(source.subjectFolders[0]));await n.locator('#tanuvas>summary').click();assert(await n.locator('#tanuvas .file-row:visible').count()>0,'No-JS notes unavailable');await nojs.close();
}catch(e){report.errors.push(e.stack||String(e))}finally{if(browser)await browser.close();if(server)server.kill();fs.writeFileSync(out+'/report.json',JSON.stringify(report,null,2));console.log('TANUVAS_QA '+JSON.stringify(report));if(report.errors.length)process.exitCode=1}
