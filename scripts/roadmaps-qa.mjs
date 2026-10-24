/* Match the supplied mobile roadmap composition and verify academic navigation. */
import fs from 'node:fs';import {spawn} from 'node:child_process';import {chromium} from 'playwright';import AxeBuilder from '@axe-core/playwright';
const data=JSON.parse(fs.readFileSync('data/year-roadmaps.json')),out='docs/qa/roadmaps';fs.mkdirSync(out,{recursive:true});const base='http://127.0.0.1:4173';let server,browser;const report={views:[],before:[],errors:[],interactions:[]};
try{
 server=spawn('python3',['scripts/qa-server.py',process.cwd()],{stdio:'ignore'});for(let n=0;n<50;n++){try{if((await fetch(base)).ok)break}catch{}await new Promise(r=>setTimeout(r,100))}
 browser=await chromium.launch({headless:true,args:['--no-sandbox']});
 const baseline=await browser.newContext({viewport:{width:390,height:844},colorScheme:'light'}),bp=await baseline.newPage();
 for(let year=1;year<=4;year++){try{const path=`/bvsc/year-${year}/roadmap/`;await bp.goto('https://notes.thatvetguy.net'+path,{waitUntil:'networkidle',timeout:15000});await bp.evaluate(()=>document.fonts.ready);const layout=await bp.evaluate(()=>({build:document.querySelector('meta[name=site-build]')?.content,glanceTop:document.querySelector('.road-stats').closest('.road-card').getBoundingClientRect().top+scrollY,height:document.documentElement.scrollHeight}));report.before.push({year,...layout});await bp.screenshot({path:`${out}/before-year-${year}-opening-390.png`,animations:'disabled'})}catch(error){report.before.push({year,unavailable:String(error)})}}await baseline.close();
 for(const theme of ['light','dark'])for(const width of [360,390,430,768,1024,1440]){
  const context=await browser.newContext({viewport:{width,height:844},colorScheme:theme});await context.addInitScript(t=>localStorage.setItem('tvg-theme',t),theme);const page=await context.newPage();
  for(let year=1;year<=4;year++){
   const path=`/bvsc/year-${year}/roadmap/`;await page.goto(base+path,{waitUntil:'networkidle'});await page.evaluate(()=>document.fonts.ready);
   const geometry=await page.evaluate(()=>({build:document.querySelector('meta[name=site-build]')?.content,glanceTop:document.querySelector('.road-stats').closest('.road-card').getBoundingClientRect().top+scrollY,height:document.documentElement.scrollHeight,academicNotesClosed:!document.querySelector('.road-academic-brief').open,overflow:document.documentElement.scrollWidth>innerWidth,h1:document.querySelectorAll('h1').length,clipped:[...document.querySelectorAll('.roadmap-page h1,.roadmap-page h2,.roadmap-page h3,.roadmap-page p')].filter(e=>e.checkVisibility()&&e.scrollWidth>e.clientWidth+1).map(e=>e.textContent),small:[...document.querySelectorAll('.roadmap-page a,.roadmap-page summary')].filter(e=>e.checkVisibility()).filter(e=>{const r=e.getBoundingClientRect();return r.height<47.5}).map(e=>({text:e.textContent,height:e.getBoundingClientRect().height}))}));
   if(width<=430&&(geometry.glanceTop>520||!geometry.academicNotesClosed))throw Error('Opening is not compact '+JSON.stringify({year,width,theme,geometry}));
   const before=report.before.find(x=>x.year===year);if(width===390&&theme==='light'&&before?.glanceTop&&before.build!==geometry.build&&geometry.glanceTop>before.glanceTop-(year<=2?150:60))throw Error('Insufficient vertical-space saving '+JSON.stringify({year,before,geometry}));
   const results=await new AxeBuilder({page}).withTags(['wcag2a','wcag2aa','wcag21aa']).analyze();const serious=results.violations.filter(v=>['serious','critical'].includes(v.impact));
   const selected=await page.locator('.road-stages [aria-current=step]').getAttribute('href');if(selected!==path)throw Error('Wrong active year');
   if(await page.locator('.road-stats>li').count()!==4||await page.locator('.road-credit').count()!==data.years[year].subjects.length)throw Error('Wrong course count');
   for(const a of await page.locator('.road-credit').all()){const href=await a.getAttribute('href');if(!href.startsWith(`/bvsc/year-${year}/#`))throw Error('Credit destination')}
   report.views.push({path,width,theme,geometry,violations:serious});if(geometry.overflow||geometry.clipped.length||geometry.small.length||geometry.h1!==1||serious.length)report.errors.push(report.views.at(-1));
   if([390,1440].includes(width))await page.screenshot({path:`${out}/year-${year}-${theme}-${width}.png`,fullPage:true,animations:'disabled'});
   if(width===390&&theme==='light'){await page.screenshot({path:`${out}/after-year-${year}-opening-390.png`,animations:'disabled'});const shot=await page.screenshot({type:'jpeg',quality:75});console.log('ROADMAP_OPENING '+JSON.stringify({year,geometry,before,data:shot.toString('base64')}))}
   if(width===390&&theme==='light'){const shot=await page.screenshot({type:'jpeg',quality:65,fullPage:true});console.log('ROADMAP_PREVIEW '+JSON.stringify({year,width,theme,data:shot.toString('base64')}))}
  }
  await context.close();
 }
 const context=await browser.newContext({viewport:{width:390,height:844}}),page=await context.newPage();
 for(let year=1;year<=4;year++){
  const path=`/bvsc/year-${year}/roadmap/`;await page.goto(base+`/bvsc/year-${year}/`);await page.locator('.year-roadmap-cta').click();await page.waitForURL('**'+path);
  await page.locator('.road-academic-brief summary').click();if(!await page.locator('.road-academic-brief').evaluate(e=>e.open))throw Error('Academic notes do not expand');if(year<=2&&!await page.locator('.road-academic-brief').getByText('Course-outline note.',{exact:false}).count())throw Error('Outline caveat lost');await page.locator('.road-academic-brief summary').click();
  await page.locator('.road-subject summary').last().click();if(!await page.locator('.road-subject').last().evaluate(e=>e.open))throw Error('Subject accordion');
  await page.locator('.road-sources summary').click();if(!await page.locator('.road-sources').evaluate(e=>e.open))throw Error('Source disclosure');
  await page.locator('.road-credit').first().click();await page.waitForURL('**/year-'+year+'/#*');if(!await page.locator('.year-subject-section:target').count())throw Error('Credit link did not open a subject');
  await page.goto(base+path);await page.locator('.road-stages a').nth(year%4).click();await page.waitForURL('**/year-'+(year%4+1)+'/roadmap/');
 }
 await page.goto(base+'/bvsc/year-1/roadmap/');await page.locator('.road-internship-step').click();await page.waitForURL('**/year-4/roadmap/#internship');
 await context.close();
 const nojs=await browser.newContext({javaScriptEnabled:false,viewport:{width:360,height:844}}),p=await nojs.newPage();await p.goto(base+'/bvsc/year-3/roadmap/');await p.locator('.road-subject summary').last().click();if(!await p.locator('.road-subject').last().evaluate(e=>e.open))throw Error('No-JS accordion');await p.locator('.road-credit').last().click();await p.waitForURL('**/year-3/#livestock-farm-practices');await nojs.close();
 const reduced=await browser.newContext({reducedMotion:'reduce',viewport:{width:390,height:844}}),rp=await reduced.newPage();await rp.goto(base+'/bvsc/year-1/roadmap/');const motion=await rp.locator('.road-subject summary>.icon-svg').first().evaluate(e=>getComputedStyle(e).transitionDuration);if(motion!=='0s')throw Error('Reduced motion ignored');await reduced.close();
 report.interactions.push('Four year CTA routes, active year navigation, all credit targets, subject/source disclosures, internship anchor, no-JS content and reduced motion.');
}catch(error){report.errors.push(error.stack||String(error));process.exitCode=1}finally{if(browser)await browser.close();if(server)server.kill();if(report.errors.length)process.exitCode=1;fs.writeFileSync(out+'/report.json',JSON.stringify(report,null,2));console.log('ROADMAP_SUMMARY '+JSON.stringify({views:report.views.length,errors:report.errors,interactions:report.interactions}))}
