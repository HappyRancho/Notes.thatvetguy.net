/* Logic checks for the actual enhancement script. This is not a rendering engine. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const source = fs.readFileSync(path.join(root, 'assets/site.js'), 'utf8');
const catalogue = JSON.parse(fs.readFileSync(path.join(root, 'assets/catalogue.json'), 'utf8'));
const settle = () => new Promise(resolve => setImmediate(resolve));

function environment(reduced) {
  const calls = [];
  let document;
  class Element extends EventTarget {
    constructor(tag = 'div', classes = '') {
      super(); this.tagName = tag.toUpperCase(); this.attrs = {}; this.children = []; this.hidden = false;
      this.textContent = ''; this.value = ''; this.open = false;
      this.style = { position: '', top: '', width: '', setProperty(key, value) { this[key] = value; } };
      const set = new Set(classes.split(' ').filter(Boolean));
      this.classList = { add: (...c) => c.forEach(x => set.add(x)), remove: x => set.delete(x), contains: x => set.has(x), toggle(x, force) { const value = force === undefined ? !set.has(x) : force; value ? set.add(x) : set.delete(x); return value; } };
    }
    setAttribute(key, value) { this.attrs[key] = String(value); }
    getAttribute(key) { return this.attrs[key] ?? null; }
    removeAttribute(key) { delete this.attrs[key]; }
    append(...nodes) { this.children.push(...nodes); }
    replaceChildren(...nodes) { this.children = nodes; }
    contains(target) { return this === target || this.children.some(c => c.contains(target)); }
    focus() { document.activeElement = this; this.dispatchEvent(new Event('focus')); }
    scrollIntoView() { calls.push({ kind: 'scroll', element: this, locked: document.body.style.position === 'fixed' }); }
    querySelector(selector) { return this.queries?.[selector] || null; }
    querySelectorAll(selector) {
      if (this.queryLists?.[selector]) return this.queryLists[selector];
      const descendants = this.children.flatMap(c => [c, ...c.querySelectorAll('*')]);
      if (selector === '*') return descendants;
      if (selector === '[role="option"]') return descendants.filter(c => c.getAttribute('role') === 'option');
      return [];
    }
    getBoundingClientRect() { return { left: 20, right: 390, top: 10, bottom: 800 }; }
    showModal() { this.open = true; }
    close() { this.open = false; queueMicrotask(() => this.dispatchEvent(new Event('close'))); }
    animate() { calls.push({ kind: 'animation' }); return { finished: Promise.resolve(), cancel() {} }; }
  }
  const menu = new Element('dialog'), button = new Element('button'), close = new Element('button');
  const input = new Element('input'), suggestions = new Element(), list = new Element('ul'), empty = new Element('p');
  const form = new Element('form'); form.append(input, suggestions); suggestions.append(list, empty); suggestions.hidden = true;
  const notes = new Element('section'), heading = new Element('h2'); notes.queries = { 'input, h2': heading };
  const menuNotes = new Element('a'), menuSearch = new Element('a', 'search-jump'), headerSearch = new Element('a', 'search-jump');
  menuNotes.href = 'https://notes.thatvetguy.net/#notes';
  menuSearch.href = headerSearch.href = 'https://notes.thatvetguy.net/#search';
  menu.queryLists = { a: [menuNotes, menuSearch] };
  const tabs = Array.from({ length: 4 }, (_, i) => { const e = new Element('a'); e.id = `tab-${i + 1}`; return e; });
  const panels = Array.from({ length: 4 }, (_, i) => { const e = new Element('section'); e.id = `year-${i + 1}`; return e; });
  const selectors = {
    '#mobile-menu': menu, '.menu-button': button, '.menu-close': close, '#resource-search': input,
    '.search-form': form, '#search-suggestions': suggestions, '#suggestion-list': list,
    '#search-status': new Element(), '#search-empty': empty, '.suggestion-label': new Element(),
    '.year-tabs': new Element(), '.academic-library': new Element(), '.site-header': new Element()
  };
  const queryLists = { '.year-tab': tabs, '.year-panel': panels, '.search-examples a': [], '.search-jump': [headerSearch, menuSearch], '.section': [] };
  document = new Element(); document.activeElement = button;
  document.body = new Element('body'); document.documentElement = new Element('html');
  document.createElement = tag => new Element(tag);
  document.querySelector = selector => selectors[selector] || null;
  document.querySelectorAll = selector => queryLists[selector] || [];
  document.getElementById = id => id === 'notes' ? notes : null;
  const window = new EventTarget();
  window.scrollTo = () => calls.push({ kind: 'restore-scroll' });
  const context = { document, window, URL, URLSearchParams, Event, console, queueMicrotask, scrollY: 120,
    matchMedia: query => ({ matches: query.includes('reduced-motion') && reduced, addEventListener() {} }),
    location: { href: 'https://notes.thatvetguy.net/', origin: 'https://notes.thatvetguy.net', pathname: '/', search: '', hash: '' },
    fetch: async () => ({ ok: true, json: async () => catalogue }),
    history: { replaceState() {} }
  };
  vm.runInNewContext(source, context, { filename: 'site.js' });
  return { menu, button, close, input, suggestions, list, empty, menuNotes, menuSearch, heading, notes, tabs, panels, document, calls };
}

function event(target, type, properties = {}) {
  const e = new Event(type, { cancelable: true });
  for (const [key, value] of Object.entries(properties)) Object.defineProperty(e, key, { value });
  target.dispatchEvent(e); return e;
}

(async () => {
  for (const reduced of [false, true]) {
    const e = environment(reduced);
    assert.equal(e.tabs[0].getAttribute('aria-selected'), 'true');
    event(e.tabs[2], 'click'); assert.equal(e.panels[2].hidden, false); assert.equal(e.panels[0].hidden, true);
    event(e.tabs[2], 'keydown', { key: 'ArrowRight' });
    assert.equal(e.tabs[3].getAttribute('aria-selected'), 'true'); assert.equal(e.document.activeElement, e.tabs[3]);
    e.button.focus(); event(e.button, 'click'); assert.equal(e.menu.open, true); assert.equal(e.document.body.style.position, 'fixed');
    assert.equal(e.button.getAttribute('aria-expanded'), 'true');
    assert.equal(event(e.menu, 'cancel').defaultPrevented, true);
    await settle(); await settle();
    assert.equal(e.menu.open, false); assert.equal(e.document.body.style.position, ''); assert.equal(e.document.activeElement, e.button);
    assert.equal(e.button.getAttribute('aria-expanded'), 'false');
    event(e.button, 'click'); event(e.menu, 'click', { clientX: 0, clientY: 0 }); await settle(); await settle(); assert.equal(e.menu.open, false);
    event(e.button, 'click'); event(e.menuNotes, 'click'); await settle(); await settle();
    assert.equal(e.document.activeElement, e.heading);
    const noteScroll = e.calls.find(c => c.element === e.notes); assert.equal(noteScroll.locked, false, 'Navigation must wait for scroll unlock');
    event(e.button, 'click'); const count = e.calls.filter(c => c.element === e.input).length;
    event(e.menuSearch, 'click'); await settle(); await settle();
    assert.equal(e.calls.filter(c => c.element === e.input).length, count + 1, 'Drawer search should scroll exactly once');
    assert.equal(e.document.activeElement, e.input);
    e.input.value = 'Haemonchus'; event(e.input, 'input'); await settle();
    assert.equal(e.suggestions.hidden, false); assert.ok(e.list.querySelectorAll('[role="option"]').length > 0);
    event(e.input, 'keydown', { key: 'ArrowDown' }); assert.ok(e.input.getAttribute('aria-activedescendant'));
    e.input.value = 'no-such-veterinary-resource'; event(e.input, 'input'); await settle();
    assert.equal(e.empty.hidden, false); assert.equal(e.list.hidden, true);
    event(e.input, 'keydown', { key: 'Escape' }); assert.equal(e.suggestions.hidden, true);
    if (reduced) assert.equal(e.calls.filter(c => c.kind === 'animation').length, 0, 'Reduced motion must skip animations');
  }
  console.log('PASS: menu scroll lock, Escape/outside dismissal, focus restoration, single search navigation, year keyboard control, suggestions and empty states; normal and reduced-motion logic. Browser rendering not covered.');
})().catch(error => { console.error(error); process.exitCode = 1; });
