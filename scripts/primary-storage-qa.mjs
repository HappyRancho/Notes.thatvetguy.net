/* New primary storage and collapsed-unit navigation, across every subject. */
import fs from 'node:fs';import {spawn} from 'node:child_process';import {chromium} from 'playwright';
const base='http://127.0.0.1:4173',out='docs/qa/primary-storage',data=JSON.parse(fs.readFileSync('data/resources.json')),primary=JSON.parse(fs.readFileSync('data/primary-drive-links.json')).books;
fs.mkdirSync(out,{recursive:true});const report={subjects:[],downloads:[],errors:[]};const assert=(ok,msg)=>{if(!ok)throw Error(msg)};let browser,server;
try{
 server=spawn('python3',['scripts/qa-server.py',process.cwd()],{stdio:'ignore'});for(let n=0;n<50;n++){try{if((await fetch(base)).ok)break}catch{}await new Promise(r=>setTimeout(r,100))}
 browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 for(const width of [360,430,1280]){
  const c=await browser.newContext({viewport:{width,height:844},reducedMotion:'reduce'}),p=await c.newPage();p.on('pageerror',e=>report.errors.push(e.message));
  for(const y of data.years)for(const subject of y.subjects){
   const path=`/bvsc/year-${y.year}/${subject.slug}/`;await p.goto(base+path);
   for(const option of ['notes','tanuvas']){
    const tile=p.locator(`[data-note-option="${option}"]`);if(!await tile.count())continue;
    await tile.click();const panel=p.locator('#'+option);assert(await panel.isVisible(),path+option+' hidden');
    assert(!await panel.locator('.reader-unit[open]').count(),path+' first unit auto-expanded');
    assert(await panel.evaluate(e=>e.getBoundingClientRect().bottom<=document.querySelector('.subject-practical-link').getBoundingClientRect().top),path+' panel below Vault');
    await p.waitForTimeout(50);assert(await panel.locator(':scope > summary').evaluate(e=>{const r=e.getBoundingClientRect();return r.bottom>0&&r.top<innerHeight}),path+' expansion not brought into view');
    if(await panel.locator('.reader-unit').count()){await panel.locator('.reader-unit>summary').first().click();assert(await panel.locator('.file-row:visible').count()>0,'Unit will not open');await tile.click();await tile.click();assert(!await panel.locator('.reader-unit[open]').count(),'Reopened notes keep first unit open');}
   }
   await p.goto(base+path+'syllabus/');assert(!await p.locator('.syllabus-unit[open]').count(),path+' checklist starts open');
   const unit=p.locator('.syllabus-unit').first();await unit.locator('summary').click();const tick=unit.locator('[data-topic]').first();await tick.check();await p.reload();assert(!await p.locator('.syllabus-unit[open]').count(),'Reload opens checklist');assert(await tick.isChecked(),'Saved tick lost');
   assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Horizontal overflow '+path);report.subjects.push({path,width});
  }
  const anatomy='/bvsc/year-1/veterinary-anatomy/';const note=data.files.find(r=>r.page===anatomy&&!r.collections.includes('tanuvas'));await p.goto(base+note.permalink);assert(await p.locator('#file-'+note.id).isVisible(),'Direct note link not revealed');
  await p.goto(base+anatomy+'#notes');assert(!await p.locator('#notes .reader-unit[open]').count(),'Notes collection hash opens first unit');
  await p.locator('.collection-query').fill('histology');assert(await p.locator('#notes .reader-unit[open]:visible').count()>0,'Search does not reveal matching unit');await p.locator('.collection-query').fill('');assert(!await p.locator('#notes .reader-unit[open]').count(),'Clear search opens first unit');
  if(width===360){await p.screenshot({path:out+'/notes-360.png',fullPage:false});console.log('PRIMARY_PREVIEW '+JSON.stringify({view:'notes',data:(await p.screenshot({type:'jpeg',quality:65})).toString('base64')}));}
  await c.close();
 }
 const c=await browser.newContext({viewport:{width:390,height:844}}),p=await c.newPage();
 for(const [id,file] of Object.entries(primary)){await p.goto(base+'/books/'+id+'/');assert(await p.locator('.book-download').getAttribute('href')===file.url,'Wrong file '+id);assert((await p.locator('.book-download').innerText()).includes('Open in Google Drive'),'Wrong label '+id);report.downloads.push(id)}await c.close();
 const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:360,height:844}}),n=await nojs.newPage();await n.goto(base+'/bvsc/year-1/veterinary-anatomy/');await n.locator('#notes>summary').click();assert(!await n.locator('.reader-unit[open]').count(),'No-JS first unit open');await n.locator('#notes .reader-unit>summary').first().click();assert(await n.locator('#notes .file-row:visible').count()>0,'No-JS notes unavailable');await n.goto(base+'/bvsc/year-1/veterinary-anatomy/syllabus/');await n.locator('.syllabus-unit>summary').first().click();await n.locator('[data-topic]').first().check();assert(await n.locator('[data-topic]').first().isChecked(),'No-JS checklist unavailable');await nojs.close();
}catch(e){report.errors.push(e.stack||String(e))}finally{if(browser)await browser.close();if(server)server.kill();fs.writeFileSync(out+'/report.json',JSON.stringify(report,null,2));console.log('PRIMARY_QA '+JSON.stringify(report));if(report.errors.length)process.exitCode=1}
