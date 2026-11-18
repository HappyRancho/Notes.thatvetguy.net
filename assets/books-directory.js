/* A compact window onto the complete static library; no catalogue fetch is needed. */
(()=>{'use strict';
const input=document.querySelector('#books-query');if(!input)return;
const clear=document.querySelector('#books-clear'),status=document.querySelector('#books-count'),empty=document.querySelector('#books-empty'),more=document.querySelector('#books-more');
const sections=[...document.querySelectorAll('[data-books-section]')],cards=[...document.querySelectorAll('[data-book-id]')],filters=[...document.querySelectorAll('.books-filter')];
const normal=value=>value.normalize('NFKD').replace(/\p{M}/gu,'').toLowerCase().replace(/[^\p{L}\p{N}]+/gu,' ').trim();
const terms=new Map(cards.map(card=>[card,normal(card.dataset.rowSearch)]));let category='all',limit=24;
for(const filter of filters){filter.setAttribute('role','button');filter.setAttribute('aria-controls','books-shelves');}
function update(){
 const query=normal(input.value),words=query.split(' ').filter(Boolean);clear.hidden=!input.value;
 const matches=cards.filter(card=>(category==='all'||card.dataset.bookCategory===category)&&words.every(word=>terms.get(card).includes(word)));
 const visible=new Set(matches.slice(0,limit));for(const card of cards)card.hidden=!visible.has(card);
 for(const section of sections)section.hidden=![...section.querySelectorAll('[data-book-id]')].some(card=>!card.hidden);
 for(const filter of filters)filter.setAttribute('aria-pressed',String(filter.dataset.bookCategory===category));
 empty.hidden=matches.length!==0;more.hidden=visible.size>=matches.length;
 more.innerHTML='Show '+Math.min(24,matches.length-visible.size)+' more books <span aria-hidden="true">↓</span>';
 const noun=matches.length===1?'book':'books';status.textContent=matches.length===0?'No books found':visible.size<matches.length?'Showing '+visible.size+' of '+matches.length+' '+noun:matches.length+' '+noun+(query?' found':' on the shelf');
}
function resetSearch(){input.value='';limit=24;update();}
input.addEventListener('input',()=>{limit=24;update();});clear.addEventListener('click',()=>{resetSearch();input.focus();});
input.addEventListener('keydown',event=>{if(event.key==='Escape')resetSearch();});
for(const filter of filters){filter.addEventListener('click',event=>{event.preventDefault();category=filter.dataset.bookCategory;limit=24;update();});filter.addEventListener('keydown',event=>{if(event.key===' '){event.preventDefault();filter.click();}});}
more.addEventListener('click',()=>{limit+=24;update();});
function revealHash(){let ident;try{ident=decodeURIComponent(location.hash.slice(1));}catch{return;}if(sections.some(section=>section.id===ident)){category=ident;input.value='';limit=24;update();}}
addEventListener('hashchange',revealHash);revealHash();update();
})();
