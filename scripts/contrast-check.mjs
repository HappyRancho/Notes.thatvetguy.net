import fs from 'node:fs';
const tokens=JSON.parse(fs.readFileSync('data/study-clinic-tokens.json','utf8'));
const lum=h=>{const a=h.match(/[a-f\d]{2}/gi).map(v=>parseInt(v,16)/255).map(v=>v<=.04045?v/12.92:((v+.055)/1.055)**2.4);return a[0]*.2126+a[1]*.7152+a[2]*.0722};
const ratio=(a,b)=>{const x=[lum(a),lum(b)].sort((a,b)=>a-b);return (x[1]+.05)/(x[0]+.05)};
const rows=[];
function check(theme,foreground,background,a,b,min){const result=ratio(a,b);rows.push({theme,foreground,background,ratio:+result.toFixed(2),minimum:min});if(result<min)throw Error(`${theme} ${foreground}/${background}: ${result.toFixed(2)} < ${min}`)}
for(const name of ['light','dark']){const t=tokens[name];for(const bg of ['paper','surface']){check(name,'text',bg,t.text,t[bg],7);check(name,'muted',bg,t.muted,t[bg],4.5);check(name,'border',bg,t.line,t[bg],3)}}
for(const [name,color] of Object.entries(tokens.stickers)){if(['ink','secondary'].includes(name))continue;check('both','sticker ink',name,tokens.stickers.ink,color,7);check('both','sticker secondary',name,tokens.stickers.secondary,color,4.5);check('both','sticker border',name,tokens.stickers.ink,color,3)}
check('both','primary label','primary button',tokens.stickers.lime,tokens.stickers.ink,7);
fs.mkdirSync('docs/qa/task3',{recursive:true});fs.writeFileSync('docs/qa/task3/contrast.json',JSON.stringify(rows,null,2));console.log(`PASS ${rows.length} contrast pairs; minimum ${Math.min(...rows.map(r=>r.ratio))}:1.`);
