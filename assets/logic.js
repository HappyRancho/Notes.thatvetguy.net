/* Shared, testable search and storage primitives; no dependencies. */
(function(root,factory){if(typeof module==='object'&&module.exports)module.exports=factory();else root.NotesLogic=factory()})(typeof globalThis!=='undefined'?globalThis:this,()=>{
 const normal=value=>String(value||'').toLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g,'').replace(/[^a-z0-9 ]/g,' ').replace(/\s+/g,' ').trim();
 function find(query,index){const q=normal(query),words=q.split(' ').filter(Boolean);return index.filter(r=>!words.length||words.every(w=>normal([r.title,r.subject,r.type,r.description,r.keywords,(r.aliases||[]).join(' ')].join(' ')).includes(w))).sort((a,b)=>Number(normal(b.title).startsWith(q))-Number(normal(a.title).startsWith(q)))}
 function store(storage){const memory=new Map();return{read(key,initial){try{return JSON.parse(storage.getItem(key))??initial}catch{return memory.get(key)??initial}},write(key,value){memory.set(key,value);try{storage.setItem(key,JSON.stringify(value));return true}catch{return false}}}}
 return{normal,find,store};
});
