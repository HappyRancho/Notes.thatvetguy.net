/* One collection at a time. Original links and native details work without JS. */
(()=>{'use strict';
const reader=document.querySelector('[data-subject-reader]');if(!reader)return;
const tabs=[...reader.querySelectorAll('[data-reader-tab]')],panels=[...reader.querySelectorAll('[data-subject-panel]')];
const query=reader.querySelector('.collection-query'),search=reader.querySelector('.reader-search'),empty=reader.querySelector('.reader-empty'),status=reader.querySelector('.reader-search-status');
let active=panels[0],lastQuery='';
reader.querySelector('.reader-tabs').setAttribute('role','tablist');
tabs.forEach(tab=>{tab.setAttribute('role','tab');tab.setAttribute('aria-controls',tab.dataset.readerTab)});
panels.forEach(panel=>{panel.dataset.summary=panel.querySelector('.reader-panel-heading p').textContent;panel.setAttribute('role','tabpanel');panel.setAttribute('aria-labelledby','reader-tab-'+panel.id)});
function filter(){
 const words=window.NotesLogic.normal(query.value).split(' ').filter(Boolean);let count=0;
 active.querySelectorAll('[data-row-search]').forEach(row=>{row.hidden=!words.every(w=>row.dataset.rowSearch.includes(w));if(!row.hidden)count++});
 active.querySelectorAll('.reader-unit').forEach((group,i)=>{const rows=[...group.querySelectorAll('[data-row-search]')];group.hidden=!rows.some(row=>!row.hidden);if(words.length)group.open=!group.hidden;else if(lastQuery)group.open=i===0});
 active.querySelectorAll('.page-chunk').forEach(chunk=>{chunk.hidden=words.length>0&&![...chunk.querySelectorAll('[data-row-search]')].some(row=>!row.hidden);if(words.length)chunk.open=!chunk.hidden;else if(lastQuery)chunk.open=false});
 active.querySelector('.reader-panel-heading p').textContent=words.length?count+' notes found':active.dataset.summary;empty.hidden=!words.length||count>0;status.textContent=words.length?count+' notes found.':'';lastQuery=query.value;
}
function select(panel,focus=false){
 if(!panel)return;active=panel;query.value='';lastQuery='';empty.hidden=true;
 panels.forEach(p=>{const on=p===panel;p.hidden=!on;p.dataset.selected=String(on)});
 tabs.forEach(tab=>{const on=tab.dataset.readerTab===panel.id;tab.setAttribute('aria-selected',String(on));tab.tabIndex=on?0:-1;tab.classList.toggle('is-selected',on);if(on&&focus)tab.focus({preventScroll:true})});
 search.hidden=panel.id==='books'||panel.querySelectorAll('[data-row-search]').length<12;filter();
}
function fromHash(scroll=false){
 let target;try{target=document.getElementById(decodeURIComponent(location.hash.slice(1)))}catch{return}
 const panel=target?.closest('[data-subject-panel]');if(!panel)return;select(panel);
 for(let node=target;node&&node!==panel;node=node.parentElement)if(node.tagName==='DETAILS')node.open=true;
 if(scroll)requestAnimationFrame(()=>target.scrollIntoView({block:'start',behavior:'instant'}));
}
tabs.forEach((tab,i)=>{
 tab.addEventListener('click',event=>{if(event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;event.preventDefault();select(document.getElementById(tab.dataset.readerTab));history.pushState(null,'',tab.getAttribute('href'))});
 tab.addEventListener('keydown',event=>{let next;if(event.key==='ArrowRight')next=(i+1)%tabs.length;else if(event.key==='ArrowLeft')next=(i+tabs.length-1)%tabs.length;else if(event.key==='Home')next=0;else if(event.key==='End')next=tabs.length-1;if(next!==undefined){event.preventDefault();select(document.getElementById(tabs[next].dataset.readerTab),true);history.replaceState(null,'',tabs[next].getAttribute('href'))}});
});
query.addEventListener('input',filter);addEventListener('hashchange',()=>fromHash(true));addEventListener('popstate',()=>{if(location.hash)fromHash();else select(panels[0])});
select(panels[0]);fromHash(!!location.hash);
})();
