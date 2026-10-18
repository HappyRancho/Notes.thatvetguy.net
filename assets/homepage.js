/* Progressive tabs: hrefs still open the real destination when JS is unavailable. */
(()=>{'use strict';const reduced=matchMedia('(prefers-reduced-motion: reduce)').matches;
document.querySelectorAll('[data-home-tabs]').forEach(section=>{const list=section.querySelector('[role=tablist]'),tabs=[...list.querySelectorAll('[role=tab]')],panels=[...section.querySelectorAll(':scope > [role=tabpanel]')];
 const indicator=document.createElement('span');indicator.className='rx-tab-indicator';indicator.setAttribute('aria-hidden','true');list.prepend(indicator);list.classList.add('has-indicator');
 const position=()=>{const tab=tabs.find(t=>t.getAttribute('aria-selected')==='true');indicator.style.width=tab.offsetWidth+'px';indicator.style.transform='translateX('+tab.offsetLeft+'px)'};
 function select(tab,focus=false){tabs.forEach((t,i)=>{const on=t===tab;t.setAttribute('aria-selected',String(on));t.tabIndex=on?0:-1;panels[i].hidden=!on;panels[i].classList.remove('is-entering');if(on&&!reduced){void panels[i].offsetWidth;panels[i].classList.add('is-entering')}});position();if(focus)tab.focus({preventScroll:true})}
 tabs.forEach((tab,i)=>{tab.addEventListener('click',event=>{if(event.metaKey||event.ctrlKey||event.shiftKey||event.altKey)return;event.preventDefault();select(tab)});tab.addEventListener('keydown',event=>{let next;if(event.key==='ArrowRight')next=(i+1)%tabs.length;else if(event.key==='ArrowLeft')next=(i+tabs.length-1)%tabs.length;else if(event.key==='Home')next=0;else if(event.key==='End')next=tabs.length-1;if(next!==undefined){event.preventDefault();select(tabs[next],true)}})});
 new ResizeObserver(position).observe(list);document.fonts.ready.then(position);position();
});
})();
