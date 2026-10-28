/* Reproduce public navigation in temporary, normal Chrome profiles, without bypassing warnings. */
import fs from 'node:fs';import os from 'node:os';import path from 'node:path';
import {execFileSync} from 'node:child_process';import {chromium} from 'playwright';
const out='docs/qa/domain-warning';fs.mkdirSync(out,{recursive:true});
const notes='https://notes.thatvetguy.net/',main='https://thatvetguy.net/';
let executablePath;for(const candidate of ['google-chrome','google-chrome-stable']){try{executablePath=execFileSync('which',[candidate],{encoding:'utf8'}).trim();if(executablePath)break}catch{}}
let installedVersion='unknown';try{installedVersion=execFileSync(executablePath||chromium.executablePath(),['--version'],{encoding:'utf8'}).trim()}catch{}
const report={installedVersion,browser:executablePath?'Google Chrome':'Playwright Chromium',views:[],errors:[],limitations:['These are desktop-engine checks, including a narrow viewport. They do not reproduce the affected Android installation or its private browsing history. A successful navigation is not proof that every visitor is unaffected.']};
for(const scenario of [{name:'clean-profile',parentFirst:false,width:1280},{name:'parent-then-notes',parentFirst:true,width:390}]){
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'notes-chrome-domain-'));let context;
 try{
  context=await chromium.launchPersistentContext(dir,{...(executablePath?{executablePath}:{}),headless:true,args:['--no-sandbox'],viewport:{width:scenario.width,height:844}});
  const browserVersion=context.browser()?.version();const page=context.pages()[0]||await context.newPage(),consoleMessages=[];
  page.on('console',m=>{if(/lookalike|spoof|safety.?tip/i.test(m.text()))consoleMessages.push(m.text().slice(0,1500))});
  let parentVisit=null;
  if(scenario.parentFirst){try{const r=await page.goto(main,{waitUntil:'load',timeout:25000});parentVisit={url:page.url(),status:r?.status(),title:await page.title()};await page.mouse.wheel(0,300);await page.keyboard.press('Tab');await page.waitForTimeout(1500)}catch(e){parentVisit={error:String(e)}}}
  const response=await page.goto(notes,{waitUntil:'load',timeout:25000});await page.waitForTimeout(1500);
  const text=await page.locator('body').innerText(),warning=/did you mean|site (?:that )?you just tried to visit looks fake|deceptive site ahead|your connection is not private/i.test(text);
  const row={scenario:scenario.name,width:scenario.width,version:browserVersion,userAgent:await page.evaluate(()=>navigator.userAgent),parentVisit,status:response?.status(),finalURL:page.url(),title:await page.title(),h1:await page.locator('h1').count(),warningDetected:warning,consoleMessages,tls:await response?.securityDetails(),bodyExcerpt:warning?text.slice(0,3000):null};
  report.views.push(row);await page.screenshot({path:`${out}/${scenario.name}.png`,animations:'disabled'});console.log('CHROME_DOMAIN_VIEW '+JSON.stringify(row));
  if(warning||row.status!==200||row.finalURL!==notes||row.h1!==1)report.errors.push(row);
 }catch(error){report.errors.push({scenario:scenario.name,error:String(error)})}finally{if(context)await context.close();fs.rmSync(dir,{recursive:true,force:true})}
}
fs.writeFileSync(`${out}/chrome.json`,JSON.stringify(report,null,2));console.log('CHROME_DOMAIN_SUMMARY '+JSON.stringify(report));if(report.errors.length)process.exitCode=1;
