/* Progressive enhancement only: all study links and page content exist in the HTML. */
(() => {
  'use strict';
  document.documentElement.classList.add('js');
  const $ = (s, root = document) => root.querySelector(s);
  const $$ = (s, root = document) => [...root.querySelectorAll(s)];
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)');
  const menu = $('#mobile-menu');
  const menuButton = $('.menu-button');
  let lockedScroll = null;
  let menuOpener;
  let restoreFocus = true;
  let menuClosing = null;

  function openMenu() {
    if (!menu || menu.open) return;
    closeSuggestions();
    menuOpener = document.activeElement;
    restoreFocus = true;
    lockedScroll = { y: scrollY, position: document.body.style.position, top: document.body.style.top, width: document.body.style.width };
    document.documentElement.classList.add('scroll-locked');
    Object.assign(document.body.style, { position: 'fixed', top: `-${lockedScroll.y}px`, width: '100%' });
    menu.showModal();
    menuButton.setAttribute('aria-expanded', 'true');
    $('.menu-close').focus();
  }
  function closeMenu(focus = true) {
    if (menuClosing) return menuClosing;
    restoreFocus = focus;
    if (!menu?.open) return Promise.resolve();
    menuClosing = new Promise(resolve => {
      menu.addEventListener('close', () => { menuClosing = null; resolve(); }, { once: true });
      if (!reduceMotion.matches && typeof menu.animate === 'function') {
        const animation = menu.animate(
          [{ opacity: 1, transform: 'translateX(0)' }, { opacity: .5, transform: 'translateX(10px)' }],
          { duration: 140, easing: 'ease-in', fill: 'forwards' }
        );
        animation.finished.catch(() => {}).then(() => { if (menu.open) menu.close(); animation.cancel(); });
      } else menu.close();
    });
    return menuClosing;
  }
  menuButton?.addEventListener('click', openMenu);
  $('.menu-close')?.addEventListener('click', () => closeMenu());
  menu?.addEventListener('cancel', event => { event.preventDefault(); closeMenu(); });
  menu?.addEventListener('click', event => {
    if (event.target !== menu) return;
    const r = menu.getBoundingClientRect();
    if (event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom) closeMenu();
  });
  menu?.addEventListener('close', () => {
    menuButton.setAttribute('aria-expanded', 'false');
    document.documentElement.classList.remove('scroll-locked');
    if (lockedScroll) {
      const saved = lockedScroll; lockedScroll = null;
      Object.assign(document.body.style, { position: saved.position, top: saved.top, width: saved.width });
      window.scrollTo({ top: saved.y, behavior: 'instant' });
    }
    if (restoreFocus) menuOpener?.focus({ preventScroll: true });
  });
  $$('a', menu).forEach(a => a.addEventListener('click', async event => {
    if (a.classList.contains('search-jump')) return;
    const destination = new URL(a.href);
    if (destination.pathname === location.pathname && destination.hash) {
      event.preventDefault();
      await closeMenu(false);
      const target = document.getElementById(destination.hash.slice(1));
      target?.scrollIntoView({ behavior: reduceMotion.matches ? 'instant' : 'smooth', block: 'start' });
      const focusTarget = target?.querySelector('input, h2') || target;
      if (focusTarget) { if (focusTarget.tagName !== 'INPUT') focusTarget.tabIndex = -1; focusTarget.focus({ preventScroll: true }); }
    } else closeMenu(false);
  }));
  matchMedia('(min-width: 1024px)').addEventListener('change', e => { if (e.matches) closeMenu(false); });

  const tabs = $$('.year-tab');
  const panels = $$('.year-panel');
  let yearAnimation;
  if (tabs.length) {
    const tablist = $('.year-tabs');
    tablist.setAttribute('role', 'tablist');
    tablist.classList.add('enhanced-tabs');
    $('.academic-library').classList.add('enhanced-tabs');
    tabs.forEach((tab, i) => {
      tab.setAttribute('role', 'tab');
      tab.setAttribute('aria-controls', panels[i].id);
      panels[i].setAttribute('role', 'tabpanel');
      panels[i].tabIndex = 0;
    });
    function selectYear(index, animate = false) {
      if (animate && tabs[index].getAttribute('aria-selected') === 'true') return;
      yearAnimation?.cancel();
      tablist.style.setProperty('--selected', index);
      tabs.forEach((tab, i) => { tab.setAttribute('aria-selected', String(i === index)); tab.tabIndex = i === index ? 0 : -1; panels[i].hidden = i !== index; });
      if (animate && !reduceMotion.matches && panels[index].animate) yearAnimation = panels[index].animate([{ opacity: .65, transform: 'translateY(4px)' }, { opacity: 1, transform: 'none' }], { duration: 170, easing: 'ease-out' });
    }
    tabs.forEach((tab, i) => {
      tab.addEventListener('click', e => { e.preventDefault(); selectYear(i, true); });
      tab.addEventListener('keydown', e => {
        let next;
        if (e.key === 'ArrowRight') next = (i + 1) % tabs.length;
        else if (e.key === 'ArrowLeft') next = (i + tabs.length - 1) % tabs.length;
        else if (e.key === 'Home') next = 0;
        else if (e.key === 'End') next = tabs.length - 1;
        else if (e.key === ' ') { e.preventDefault(); selectYear(i, true); return; }
        else return;
        e.preventDefault(); selectYear(next, true); tabs[next].focus();
      });
    });
    const hashIndex = panels.findIndex(p => '#' + p.id === location.hash);
    selectYear(hashIndex >= 0 ? hashIndex : 0);
  }

  const input = $('#resource-search');
  const form = $('.search-form');
  const suggestions = $('#search-suggestions');
  const list = $('#suggestion-list');
  const status = $('#search-status');
  const pageResults = $('#page-results');
  let catalogue;
  let cataloguePromise;
  let active = -1;
  let revision = 0;
  const normalize = value => value.toLowerCase().normalize('NFKD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9 ]/g, ' ').replace(/\s+/g, ' ').trim();
  const node = (tag, cls, text) => { const e = document.createElement(tag); if (cls) e.className = cls; if (text !== undefined) e.textContent = text; return e; };
  function loadCatalogue() {
    if (!cataloguePromise) cataloguePromise = fetch('/assets/catalogue.json').then(response => { if (!response.ok) throw Error('Catalogue unavailable'); return response.json(); }).then(data => { catalogue = data; return data; }).catch(error => { cataloguePromise = null; throw error; });
    return cataloguePromise;
  }
  function matches(query, data) {
    const words = normalize(query).split(' ').filter(Boolean);
    if (!words.length) return data.slice(0, 5);
    return data.filter(item => words.every(word => normalize(`${item.title} ${item.subject} ${item.type} ${item.keywords || ''}`).includes(word)))
      .sort((a, b) => Number(normalize(b.title).startsWith(normalize(query))) - Number(normalize(a.title).startsWith(normalize(query))));
  }
  function resultLink(item) {
    const a = node('a', 'search-result');
    a.href = item.url;
    if (/^https?:/.test(item.url)) { a.target = '_blank'; a.rel = 'noopener noreferrer'; }
    const copy = node('span', 'result-copy');
    copy.append(node('strong', '', item.title), node('small', '', item.source ? `${item.subject} · ${item.source}` : item.subject));
    a.append(copy, node('span', 'result-type', item.type));
    return a;
  }
  function closeSuggestions() {
    revision++;
    if (suggestions) suggestions.hidden = true;
    input?.setAttribute('aria-expanded', 'false');
    input?.removeAttribute('aria-activedescendant'); active = -1;
  }
  async function updateSuggestions() {
    if (!input || !suggestions || pageResults) return;
    const request = ++revision;
    try {
      const data = await loadCatalogue();
      if (request !== revision || document.activeElement !== input) return;
      const results = matches(input.value, data).slice(0, 5);
      list.replaceChildren(); active = -1; input.removeAttribute('aria-activedescendant');
      $('.suggestion-label').textContent = input.value.trim() ? 'Matching resources' : 'A few useful starting points';
      results.forEach((item, i) => {
        const li = node('li'); li.setAttribute('role', 'presentation');
        const a = resultLink(item); a.id = 'result-' + i; a.setAttribute('role', 'option'); a.setAttribute('aria-selected', 'false'); a.tabIndex = -1;
        a.addEventListener('click', closeSuggestions); li.append(a); list.append(li);
      });
      list.hidden = results.length === 0;
      $('#search-empty').hidden = results.length > 0;
      status.textContent = results.length ? `${results.length} suggestions. Use arrow keys to choose.` : 'No matching resources. You can request one.';
      suggestions.hidden = false; input.setAttribute('aria-expanded', String(results.length > 0));
    } catch {
      closeSuggestions();
      status.textContent = 'Suggestions are temporarily unavailable. Browse the subject and resource links below.';
    }
  }
  async function renderPageResults() {
    if (!pageResults) return;
    const request = ++revision;
    const heading = $('#results-heading');
    try {
      const data = await loadCatalogue();
      if (request !== revision) return;
      const query = input.value.trim();
      const results = query ? matches(query, data) : data;
      heading.textContent = query ? `Results for “${query}”` : 'Browse all resources';
      pageResults.replaceChildren();
      results.forEach(item => { const row = node('div', 'page-result'); row.append(resultLink(item)); pageResults.append(row); });
      if (!results.length) { const p = node('p', 'source-note', 'No match yet. Try a subject name, or '); const a = node('a', '', 'request a resource'); a.href = '/request-resource/'; p.append(a); pageResults.append(p); }
      status.textContent = `${results.length} matching resources.`;
    } catch { heading.textContent = 'Browse the library'; pageResults.replaceChildren(node('p', 'source-note', 'Search is temporarily unavailable. Use the category links below to browse every resource.')); }
  }
  if (input) {
    if (!pageResults) {
      input.setAttribute('role', 'combobox'); input.setAttribute('aria-autocomplete', 'list'); input.setAttribute('aria-haspopup', 'listbox'); input.setAttribute('aria-expanded', 'false'); input.setAttribute('aria-controls', 'suggestion-list'); list.setAttribute('role', 'listbox'); list.setAttribute('aria-label', 'Matching resources');
      input.addEventListener('focus', updateSuggestions); input.addEventListener('input', updateSuggestions);
      input.addEventListener('keydown', e => {
        if (e.key === 'Escape') { e.preventDefault(); closeSuggestions(); return; }
        const options = $$('[role="option"]', list);
        if ((e.key === 'ArrowDown' || e.key === 'ArrowUp') && options.length && !suggestions.hidden) {
          e.preventDefault(); active = active < 0 ? (e.key === 'ArrowDown' ? 0 : options.length - 1) : (active + (e.key === 'ArrowDown' ? 1 : -1) + options.length) % options.length;
          options.forEach((option, i) => { option.classList.toggle('active', i === active); option.setAttribute('aria-selected', String(i === active)); });
          input.setAttribute('aria-activedescendant', options[active].id); options[active].scrollIntoView({ block: 'nearest', behavior: 'instant' });
        }
        if (e.key === 'Enter' && active >= 0 && !suggestions.hidden) { e.preventDefault(); options[active]?.click(); }
      });
      document.addEventListener('pointerdown', e => { if (!form.contains(e.target)) closeSuggestions(); });
      document.addEventListener('focusin', e => { if (!form.contains(e.target)) closeSuggestions(); });
      $$('.search-examples a').forEach(a => a.addEventListener('click', e => { e.preventDefault(); input.value = new URL(a.href).hash.slice(8).replaceAll('-', ' '); input.focus({ preventScroll: true }); updateSuggestions(); }));
    } else {
      input.value = new URLSearchParams(location.search).get('q') || '';
      renderPageResults(); input.addEventListener('input', renderPageResults);
      form.addEventListener('submit', e => { e.preventDefault(); const url = new URL(location.href); if (input.value.trim()) url.searchParams.set('q', input.value.trim()); else url.searchParams.delete('q'); history.replaceState(null, '', url); renderPageResults(); });
    }
  }
  $$('.search-jump').forEach(a => a.addEventListener('click', async e => {
    if (new URL(a.href).pathname !== location.pathname || !input) return;
    e.preventDefault();
    await closeMenu(false);
    input.scrollIntoView({ behavior: reduceMotion.matches ? 'instant' : 'smooth', block: 'center' });
    input.focus({ preventScroll: true });
  }));
  document.addEventListener('keydown', event => {
    const editing = /^(INPUT|TEXTAREA|SELECT)$/.test(document.activeElement?.tagName || '') || document.activeElement?.isContentEditable;
    if (event.key === '/' && !editing && !event.ctrlKey && !event.metaKey && input) { event.preventDefault(); input.focus(); }
  });
  const header = $('.site-header');
  const onScroll = () => header?.classList.toggle('scrolled', scrollY > 8);
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();
  if ('IntersectionObserver' in window && !reduceMotion.matches) {
    const observer = new IntersectionObserver(entries => entries.forEach(entry => { if (entry.isIntersecting) { entry.target.classList.add('entered'); observer.unobserve(entry.target); } }), { threshold: .06 });
    $$('.section').forEach(section => observer.observe(section));
  }
})();

/* Accessible subject material tabs; all panels remain visible without JavaScript. */
(() => {
  document.querySelectorAll('[data-material-toggle]').forEach(group => {
    const tabs=[...group.querySelectorAll('.material-tab')];
    const panels=[...group.querySelectorAll('.material-panel')];
    if(tabs.length!==panels.length)return;
    group.querySelector('.material-tablist').setAttribute('role','tablist');
    function select(index){tabs.forEach((tab,i)=>{tab.setAttribute('aria-selected',String(i===index));tab.tabIndex=i===index?0:-1;panels[i].hidden=i!==index;});}
    tabs.forEach((tab,i)=>{tab.id=panels[i].id+'-tab';tab.setAttribute('role','tab');tab.setAttribute('aria-controls',panels[i].id);panels[i].setAttribute('role','tabpanel');panels[i].setAttribute('aria-labelledby',tab.id);tab.addEventListener('click',e=>{e.preventDefault();select(i);});tab.addEventListener('keydown',e=>{if(!['ArrowLeft','ArrowRight','Home','End'].includes(e.key))return;e.preventDefault();const n=e.key==='Home'?0:e.key==='End'?tabs.length-1:(i+1)%tabs.length;select(n);tabs[n].focus();});});select(0);
  });
})();
