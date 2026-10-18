import fs from 'node:fs';
const css=fs.readFileSync('assets/homepage.css','utf8');
const extract=s=>Object.fromEntries([...s.matchAll(/--([\w-]+):\s*(#[a-f\d]{6}|#[a-f\d]{3})/gi)].map(m=>[m[1],m[2]]));
const light=extract(css.match(/html\[data-ui=rx\]\{([^}]+)/)[1]),dark={...light,...extract(css.match(/html\[data-ui=rx\]\[data-theme=dark\]\{([^}]+)/)[1])};
const lum=h=>{if(h.length===4)h='#'+[...h.slice(1)].map(c=>c+c).join('');const c=h.slice(1).match(/../g).map(s=>parseInt(s,16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4);return .2126*c[0]+.7152*c[1]+.0722*c[2]};
const report=[];function check(name,fg,bg,min=4.5){const l=[lum(fg),lum(bg)].sort((a,b)=>b-a),ratio=(l[0]+.05)/(l[1]+.05);report.push({name,fg,bg,ratio:+ratio.toFixed(2),minimum:min});if(ratio<min)throw Error(name+' contrast '+ratio)}
for(const [name,t] of [['light',light],['dark',dark]])for(const bg of ['paper','surface','rx-field','rx-tab']){check(name+' body / '+bg,t.text,t[bg],7);check(name+' description / '+bg,t.muted,t[bg]);}
for(const bg of ['rx-mint','rx-yellow','rx-peach','rx-purple','rx-pink','rx-sky']){check('card heading / '+bg,'#101b43',light[bg],7);check('card description / '+bg,'#3a4c63',light[bg]);}
check('selected tab and button','#ffffff',light['rx-blue']);check('light Explore link',light['rx-blue'],light.surface);check('dark Explore link','#99cfff',dark.surface);check('Home nav','#101b43','#ffeb9f',7);check('roadmap description','#4a536b',light['rx-yellow']);
fs.mkdirSync('docs/qa/mockup-homepage',{recursive:true});fs.writeFileSync('docs/qa/mockup-homepage/contrast.json',JSON.stringify(report,null,2));console.log('PASS '+report.length+' approved-theme contrast pairs.');
