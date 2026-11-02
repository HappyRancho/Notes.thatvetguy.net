/* Verification-only pages must be identical with the third-party loader blocked or allowed. */
import fs from 'node:fs';import {spawn} from 'node:child_process';import {chromium} from 'playwright';
const base=process.env.QA_BASE_URL||'http://127.0.0.1:4173',out='docs/qa/adsense';fs.mkdirSync(out,{recursive:true});
const paths=['/','/bvsc/year-1/roadmap/','/bvsc/tanuvas-notes/','/objective/','/books/dhruv-desai/'],report={views:[],errors:[]};let browser,server;
const assert=(ok,msg)=>{if(!ok)throw Error(msg)};
try{
 if(!process.env.QA_BASE_URL){server=spawn('python3',['scripts/qa-server.py',process.cwd()],{stdio:'ignore'});for(let i=0;i<50;i++){try{if((await fetch(base)).ok)break}catch{}await new Promise(r=>setTimeout(r,100))}}
 browser=await chromium.launch({args:['--no-sandbox']});
 for(const width of [360,390,430])for(const theme of ['light','dark']){
  const c=await browser.newContext({viewport:{width,height:844},reducedMotion:'reduce'});await c.addInitScript(t=>localStorage.setItem('tvg-theme',t),theme);
  const p=await c.newPage();for(const path of paths){
   const requests=[];const listener=req=>{if(req.url().includes('/pagead/js/adsbygoogle.js'))requests.push(req.url())};p.on('request',listener);
   await p.goto(base+path);await p.waitForTimeout(600);await p.evaluate(()=>document.fonts.ready);
   const state=await p.evaluate(()=>({scripts:[...document.querySelectorAll('script[src*="adsbygoogle.js"]')].map(s=>({src:s.src,head:s.parentElement===document.head,async:s.async,crossorigin:s.crossOrigin})),units:[...document.querySelectorAll('ins.adsbygoogle,.rx-ad,[data-ad-slot]')].filter(e=>e.checkVisibility()&&e.getBoundingClientRect().width>1&&e.getBoundingClientRect().height>1).length,generatedMarkup:[...document.querySelectorAll('ins.adsbygoogle')].map(e=>({class:e.className,slot:e.getAttribute('data-ad-slot'),width:e.getBoundingClientRect().width,height:e.getBoundingClientRect().height,visible:e.checkVisibility()})),manualUnits:document.querySelectorAll('[data-rx-ad],[data-rx-ad-unit]').length,manualRuntime:!!document.querySelector('script[src*="assets/adsense.js"]'),frames:[...document.querySelectorAll('iframe')].map(f=>({id:f.id,width:f.getBoundingClientRect().width,height:f.getBoundingClientRect().height,visible:f.checkVisibility()})),adFrames:[...document.querySelectorAll('iframe')].filter(f=>/google_ads|aswift/.test(f.id)&&f.checkVisibility()&&f.getBoundingClientRect().width>1&&f.getBoundingClientRect().height>1).length,overflow:document.documentElement.scrollWidth>innerWidth}));
   report.lastState={path,width,theme,...state};
   assert(state.scripts.length===1&&state.scripts[0].head&&state.scripts[0].async&&state.scripts[0].crossorigin==='anonymous','Loader configuration '+path);
   assert(state.scripts[0].src.endsWith('client=ca-pub-3524774459480835')&&requests.length===1,'Publisher or duplicate request '+path);
   assert(!state.units&&!state.manualUnits&&!state.manualRuntime&&!state.adFrames,'Unexpected advertisement '+path);assert(!state.overflow,'Overflow '+path);
   if(path==='/'&&width===390)await p.screenshot({path:out+'/home-'+theme+'.png',fullPage:true});report.views.push({path,width,theme,...state});p.off('request',listener);
  }
  // Exercise the reserved responsive shell with local inert markup, never an ad request.
  await p.goto(base+'/');await p.addStyleTag({content:fs.readFileSync('assets/adsense.css','utf8')});
  await p.evaluate(()=>{const el=document.createElement('aside');el.className='rx-ad';el.setAttribute('aria-label','Advertisement');el.innerHTML='<span class="rx-ad-label">Advertisement</span><div class="rx-ad-frame"><div class="rx-ad-unit"></div></div>';document.querySelector('#notes').after(el)});
  assert(await p.locator('.rx-ad-frame').evaluate(e=>e.getBoundingClientRect().height===250),'Ad shell must reserve its height');assert(await p.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Responsive shell overflows');
  await c.close();
 }
}catch(e){report.errors.push(e.stack||String(e))}finally{if(browser)await browser.close();if(server)server.kill();fs.writeFileSync(out+'/browser.json',JSON.stringify(report,null,2));console.log('ADSENSE_BROWSER '+JSON.stringify({views:report.views.length,errors:report.errors,lastState:report.errors.length?report.lastState:undefined}));if(report.errors.length)process.exitCode=1}
