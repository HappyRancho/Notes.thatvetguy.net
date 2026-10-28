/* Subject-only collection tiles; books always remain visible below Notes. */
(()=>{'use strict';
const reader=document.querySelector('[data-subject-reader]');if(!reader)return;
const options=[...reader.querySelectorAll('[data-note-option]')],panels=[...reader.querySelectorAll('[data-subject-panel]')];
const query=reader.querySelector('.collection-query'),search=reader.querySelector('.reader-search'),empty=reader.querySelector('.reader-empty'),status=reader.querySelector('.reader-search-status');let active=null,lastQuery='';
function filter(){if(!active)return;const words=window.NotesLogic.normal(query.value).split(' ').filter(Boolean);let count=0;
 active.querySelectorAll('[data-row-search]').forEach(row=>{row.hidden=!words.every(w=>row.dataset.rowSearch.includes(w));if(!row.hidden)count++});
 active.querySelectorAll('.reader-unit').forEach((group,i)=>{group.hidden=![...group.querySelectorAll('[data-row-search]')].some(row=>!row.hidden);if(words.length)group.open=!group.hidden;else if(lastQuery)group.open=i===0});
 active.querySelectorAll('.page-chunk').forEach(chunk=>{chunk.hidden=words.length>0&&![...chunk.querySelectorAll('[data-row-search]')].some(row=>!row.hidden);if(words.length)chunk.open=!chunk.hidden;else if(lastQuery)chunk.open=false});
 empty.hidden=!words.length||count>0;status.textContent=words.length?count+' notes found.':'';lastQuery=query.value;
}
function select(panel){active=panel;query.value='';lastQuery='';empty.hidden=true;
 panels.forEach(p=>{const on=p===panel;p.hidden=!on;p.open=on;p.dataset.selected=String(on)});options.forEach(a=>a.setAttribute('aria-expanded',String(a.dataset.noteOption===panel?.id)));
 search.hidden=!panel||panel.querySelectorAll('[data-row-search]').length<12;if(panel)filter();
}
function fromHash(scroll=false){let target;try{target=document.getElementById(decodeURIComponent(location.hash.slice(1)))}catch{return}const panel=target?.closest('[data-subject-panel]');select(panel||null);if(!panel)return;
 for(let node=target;node&&node!==reader;node=node.parentElement)if(node.tagName==='DETAILS')node.open=true;
 if(scroll)requestAnimationFrame(()=>target.scrollIntoView({block:'start',behavior:'instant'}));
}
options.forEach(a=>a.addEventListener('click',event=>{if(event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;event.preventDefault();const panel=document.getElementById(a.dataset.noteOption);if(active===panel){select(null);history.pushState(null,'',location.pathname);return}select(panel);history.pushState(null,'',a.getAttribute('href'));}));
panels.forEach(p=>p.addEventListener('toggle',()=>{if(active===p&&!p.open){select(null);history.replaceState(null,'',location.pathname)}}));
query.addEventListener('input',filter);addEventListener('hashchange',()=>fromHash(true));addEventListener('popstate',()=>fromHash());select(null);fromHash(!!location.hash);
const bookQuery=document.getElementById('subject-book-query');if(bookQuery){const scope=document.getElementById('books'),cards=[...scope.querySelectorAll('[data-row-search]')],more=scope.querySelector('.subject-more-books'),noBooks=scope.querySelector('.subject-books-empty');bookQuery.addEventListener('input',()=>{const words=window.NotesLogic.normal(bookQuery.value).split(' ').filter(Boolean);let count=0;cards.forEach(card=>{card.hidden=!words.every(w=>card.dataset.rowSearch.includes(w));if(!card.hidden)count++});if(more){more.open=!!words.length;more.hidden=!!words.length&&![...more.querySelectorAll('[data-row-search]')].some(c=>!c.hidden)}noBooks.hidden=count>0;document.getElementById('subject-book-status').textContent=count+' books found.';});}
})();
