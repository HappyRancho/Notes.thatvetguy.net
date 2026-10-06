/* Small, dependency-free interactions for the static homepage. */
(() => {
  "use strict";
  const content = window.NotesData;
  if (!content) return;
  const $ = (selector, root = document) => root.querySelector(selector);
  const $$ = (selector, root = document) => [...root.querySelectorAll(selector)];
  const menu = $("#mobile-menu");
  const menuToggle = $(".menu");
  const resourceDialog = $("#resource-dialog");
  const searchBox = $(".searchbox");
  const input = $("#resource-search");
  const suggestions = $("#search-results");
  const searchList = $("#search-list");
  const searchStatus = $("#search-status");
  const clearSearch = $("#clear-search");
  const panel = $("#year-panel");
  const subjects = $("#subjects");
  const reduceMotion = matchMedia("(prefers-reduced-motion: reduce)");
  let selectedYear = 1;
  let activeResult = -1;
  let visibleResults = [];
  let scrollLock = null;
  let menuOpener = null;
  let resourceOpener = null;

  function lockScroll() {
    if (scrollLock) return;
    scrollLock = { y: window.scrollY, position: document.body.style.position, top: document.body.style.top, width: document.body.style.width };
    document.documentElement.classList.add("modal-open");
    document.body.style.position = "fixed";
    document.body.style.top = "-" + scrollLock.y + "px";
    document.body.style.width = "100%";
  }
  function unlockScroll() {
    if (!scrollLock || menu.open || resourceDialog.open) return;
    const saved = scrollLock;
    scrollLock = null;
    document.body.style.position = saved.position;
    document.body.style.top = saved.top;
    document.body.style.width = saved.width;
    document.documentElement.classList.remove("modal-open");
    window.scrollTo({top:saved.y, behavior:"instant"});
  }
  function outsideDialog(event, dialog) {
    if (event.target !== dialog) return false;
    const r = dialog.getBoundingClientRect();
    return event.clientX < r.left || event.clientX > r.right || event.clientY < r.top || event.clientY > r.bottom;
  }
  function closeMenu() { if (menu.open) menu.close(); }
  function openMenu() {
    if (menu.open) return closeMenu();
    closeSearch();
    menuOpener = document.activeElement;
    lockScroll();
    menu.showModal();
    menuToggle.setAttribute("aria-expanded","true");
  }
  menuToggle.addEventListener("click", openMenu);
  $(".drawer-close").addEventListener("click", closeMenu);
  menu.addEventListener("click", event => { if (outsideDialog(event, menu)) closeMenu(); });
  menu.addEventListener("close", () => {
    menuToggle.setAttribute("aria-expanded","false");
    unlockScroll();
    menuOpener?.focus({preventScroll:true});
  });
  $$("a", menu).forEach(link => link.addEventListener("click", () => {
    closeMenu();
    if (link.hash && link.origin === location.origin) {
      const target = document.getElementById(link.hash.slice(1));
      setTimeout(() => {
        target?.scrollIntoView({behavior:reduceMotion.matches ? "instant":"smooth", block:"start"});
        const heading = target?.querySelector("h2");
        if (heading) { heading.tabIndex = -1; heading.focus({preventScroll:true}); }
      },0);
    }
  }));
  matchMedia("(min-width: 1025px)").addEventListener("change", event => { if (event.matches) closeMenu(); });

  function focusSearch() {
    closeMenu();
    setTimeout(() => {
      $("#search").scrollIntoView({behavior:reduceMotion.matches ? "instant":"smooth", block:"start"});
      input.focus({preventScroll:true});
      updateSearch();
    },0);
  }
  $(".drawer-search").addEventListener("click", focusSearch);
  $(".search-trigger").addEventListener("click", event => { event.preventDefault(); focusSearch(); });

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }
  function sourceLink(link) {
    const a = element("a","source-link");
    a.href = link.url; a.target = "_blank"; a.rel = "noopener noreferrer";
    a.append(element("span","source-link-name",link.title + " ↗"));
    if (link.text) a.append(element("small","",link.text));
    return a;
  }
  function showResource(title, description, build) {
    closeMenu();
    closeSearch();
    resourceOpener = document.activeElement;
    $("#dialog-title").textContent = title;
    const body = $("#dialog-content");
    body.replaceChildren();
    body.append(element("p","dialog-description",description));
    body.firstElementChild.id = "resource-description";
    build(body);
    const request = element("a","dialog-request","Request a note, book or resource →");
    request.href = "mailto:contact@thatvetguy.net?subject=" + encodeURIComponent("Resource request: " + title);
    body.append(request);
    lockScroll();
    resourceDialog.showModal();
    $("#dialog-title").focus({preventScroll:true});
  }
  function showCollection(key) {
    const collection = content.collections[key];
    if (!collection) return;
    showResource(collection.title, collection.description, body => {
      if (collection.tips) {
        const list = element("dl","guide-points");
        collection.tips.forEach(([title,text]) => list.append(element("dt","",title),element("dd","",text)));
        body.append(list);
      }
      if (collection.bookList) {
        const heading = element("h3","dialog-subheading","Planned bookshelf");
        const list = element("ul","book-list");
        content.objectiveBooks.forEach(title => list.append(element("li","",title)));
        body.append(heading,list);
      }
      collection.links.forEach(link => body.append(sourceLink(link)));
    });
  }
  document.addEventListener("click", event => {
    const trigger = event.target.closest("[data-collection]");
    if (!trigger) return;
    event.preventDefault();
    showCollection(trigger.dataset.collection);
  });
  $(".dialog-close").addEventListener("click", () => resourceDialog.close());
  resourceDialog.addEventListener("click", event => { if (outsideDialog(event, resourceDialog)) resourceDialog.close(); });
  resourceDialog.addEventListener("close", () => {
    unlockScroll();
    const opener = resourceOpener;
    if (opener && !menu.contains(opener) && opener.isConnected) opener.focus({preventScroll:true});
    else menuToggle.focus({preventScroll:true});
  });

  function openSubject(title, year) {
    showResource(title, "Browse notes and books at their source. Each link opens an external study library.", body => {
      body.append(sourceLink({title:"DrVet · " + content.labels[year],text:"Year-wise notes and book listings.",url:"https://www.drvet.in/p/" + content.yearSources[year] + "-year.html"}));
      body.append(sourceLink({title:"Vet Study · subject-wise books",text:"Browse veterinary book listings by subject.",url:"https://vetstudy.journeywithasr.com/2021/05/veterinary-books-pdf_2.html"}));
    });
  }
  function renderYear(year, animate = false) {
    selectedYear = Number(year);
    $("#yearLabel").textContent = content.labels[year];
    $("#exploreYear").textContent = content.labels[year];
    $("#year-title").textContent = content.titles[year];
    $("#year-description").textContent = content.descriptions[year];
    panel.setAttribute("aria-labelledby","year-tab-" + year);
    $(".year-tabs").style.setProperty("--active",year - 1);
    $$("[data-year]").forEach(tab => {
      const active = Number(tab.dataset.year) === selectedYear;
      tab.classList.toggle("active",active);
      tab.setAttribute("aria-selected",String(active));
      tab.tabIndex = active ? 0 : -1;
    });
    subjects.replaceChildren();
    content.years[year].forEach((title,index) => {
      const button = element("button","subject");
      button.type = "button";
      const label = element("span","subject-title");
      label.append(element("small","",String(index+1).padStart(2,"0")),document.createTextNode(title));
      const arrow = element("span","arrow","↗"); arrow.setAttribute("aria-hidden","true");
      button.append(label,arrow);
      button.addEventListener("click", () => openSubject(title,year));
      subjects.append(button);
    });
    if (animate && !reduceMotion.matches) {
      panel.classList.remove("changing");
      void panel.offsetWidth;
      panel.classList.add("changing");
    }
  }
  $$("[data-year]").forEach(tab => {
    tab.addEventListener("click", () => renderYear(tab.dataset.year,true));
    tab.addEventListener("keydown", event => {
      let year = Number(tab.dataset.year);
      if (event.key === "ArrowRight") year = year % 4 + 1;
      else if (event.key === "ArrowLeft") year = (year + 2) % 4 + 1;
      else if (event.key === "Home") year = 1;
      else if (event.key === "End") year = 4;
      else return;
      event.preventDefault();
      renderYear(year,true);
      $("#year-tab-" + year).focus();
    });
  });
  $("#explore-year").addEventListener("click", () => openSubject(content.labels[selectedYear] + " · Notes & Books",selectedYear));
  renderYear(1);

  const icons = {
    Note:'<rect x="5" y="3" width="14" height="18" rx="2"/><path d="M9 8h6M9 12h6M9 16h3"/>',
    Book:'<path d="M4 4h6l2 2 2-2h6v16h-6l-2 1-2-1H4Z"/><path d="M12 6v15"/>',
    Drug:'<path d="m9 4 11 11a5 5 0 0 1-7 7L2 11a5 5 0 0 1 7-7Z"/><path d="m7 16 8-8"/>',
    Handbook:'<path d="M5 3h14v18H5Z"/><path d="M9 8h6M12 5v6M9 16h6"/>',
    Objective:'<rect x="4" y="4" width="6" height="6" rx="1"/><path d="m14 7 2 2 4-5M4 15h16M4 20h10"/>',
    PYQ:'<path d="M5 3h14v18H5Z"/><path d="M10 9a2 2 0 0 1 4 0c0 2-2 2-2 4M12 17h.01"/>',
    Subject:'<path d="M4 5c3-1 5-1 8 1 3-2 5-2 8-1v14c-3-1-5-1-8 1-3-2-5-2-8-1Z"/><path d="M12 6v14"/>'
  };
  const catalogue = [
    ...content.resources,
    ...Object.entries(content.years).flatMap(([year,names]) => names.map((title,index) => ({
      id:"subject-" + year + "-" + index,title,subject:content.labels[year] + " · Notes & Books",type:"Subject",year,
      keywords:title.includes("Parasitology") ? "Haemonchus haemonchosis mange parasites" : title.includes("Pharmacology") ? "NSAIDs toxicology" : ""
    })))
  ];
  const normalize = text => text.toLowerCase().normalize("NFKD").replace(/[\u0300-\u036f]/g,"").replace(/[^a-z0-9 ]/g," ").replace(/\s+/g," ").trim();
  function setActive(index) {
    const options = $$('[role="option"]',searchList);
    if (!options.length) return;
    activeResult = (index + options.length) % options.length;
    options.forEach((option,i) => option.setAttribute("aria-selected",String(i===activeResult)));
    input.setAttribute("aria-activedescendant",options[activeResult].id);
    options[activeResult].scrollIntoView({block:"nearest",behavior:"instant"});
  }
  function closeSearch() {
    suggestions.hidden = true;
    searchBox.classList.remove("search-open");
    input.setAttribute("aria-expanded","false");
    input.removeAttribute("aria-activedescendant");
    activeResult = -1;
  }
  function updateSearch() {
    const query = normalize(input.value);
    const words = query.split(" ").filter(Boolean);
    const matches = words.length ? catalogue.filter(item => {
      const haystack = normalize(item.title + " " + item.subject + " " + item.type + " " + (item.keywords||""));
      return words.every(word => haystack.includes(word));
    }).sort((a,b) => Number(normalize(b.title).startsWith(query)) - Number(normalize(a.title).startsWith(query))) : content.resources.slice(0,5);
    visibleResults = matches.slice(0,5);
    activeResult = -1;
    input.removeAttribute("aria-activedescendant");
    searchList.replaceChildren();
    $("#suggestion-heading").textContent = query ? "Matching resources" : "Start with a reference";
    searchStatus.textContent = matches.length ? matches.length + " matching resources. Use the arrow keys to explore." : "No matching resources. You can request one.";
    visibleResults.forEach((item,index) => {
      const option = element("a","result");
      option.id = "suggestion-" + index;
      option.setAttribute("role","option"); option.setAttribute("aria-selected","false"); option.tabIndex = -1;
      option.href = item.url || "#notes";
      if (item.url) { option.target="_blank";option.rel="noopener noreferrer"; }
      const icon = element("span","result-icon");icon.setAttribute("aria-hidden","true");
      icon.innerHTML='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">' + icons[item.type] + '</svg>';
      const copy = element("span","result-copy");
      copy.append(element("strong","",item.title),element("small","",item.source ? item.subject + " · " + item.source : item.subject));
      const badge = element("span","result-type",item.type);
      option.append(icon,copy,badge);
      option.addEventListener("click", event => {
        if (item.collection) { event.preventDefault();showCollection(item.collection); }
        else if (item.year) { event.preventDefault();openSubject(item.title,item.year); }
        closeSearch();
      });
      searchList.append(option);
    });
    const empty = $("#search-empty");
    empty.hidden = visibleResults.length > 0;
    searchList.hidden = !visibleResults.length;
    suggestions.hidden = false;
    searchBox.classList.add("search-open");
    input.setAttribute("aria-expanded","true");
    clearSearch.hidden = !input.value;
  }
  input.addEventListener("input",updateSearch);
  input.addEventListener("focus",updateSearch);
  input.addEventListener("keydown", event => {
    if (event.key === "Escape") { event.preventDefault();closeSearch(); }
    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      if (suggestions.hidden) updateSearch();
      setActive(activeResult < 0 ? (event.key === "ArrowDown" ? 0 : visibleResults.length - 1) : activeResult + (event.key === "ArrowDown" ? 1 : -1));
    }
    if (event.key === "Enter" && !suggestions.hidden) {
      event.preventDefault();
      const options=$$('[role="option"]',searchList);
      options[activeResult<0 ? 0 : activeResult]?.click();
    }
  });
  clearSearch.addEventListener("click", () => {input.value="";input.focus();updateSearch();});
  $$(".pill").forEach(button => button.addEventListener("click", () => {input.value=button.textContent;input.focus();updateSearch();}));
  document.addEventListener("pointerdown", event => {if(!searchBox.contains(event.target))closeSearch();});
  document.addEventListener("focusin", event => {if(!searchBox.contains(event.target))closeSearch();});

  const recentList=$("#recent-list");
  content.recent.forEach(id => {
    const item=content.resources.find(resource=>resource.id===id);
    if (!item?.url) return;
    const row=element("a","recent-row");
    row.href=item.url;row.target="_blank";row.rel="noopener noreferrer";
    const fresh=element("span","recent-new","NEW");
    const copy=element("span","recent-copy");
    copy.append(element("strong","",item.title),element("small","",item.subject + " · " + item.type));
    const arrow=element("span","arrow","↗");arrow.setAttribute("aria-hidden","true");
    row.append(fresh,copy,arrow);recentList.append(row);
  });
  const onScroll=()=>$("#top").classList.toggle("scrolled",window.scrollY>12);
  window.addEventListener("scroll",onScroll,{passive:true});onScroll();
  if ("IntersectionObserver" in window && !reduceMotion.matches) {
    const observer=new IntersectionObserver(entries=>entries.forEach(entry=>{
      if(entry.isIntersecting){entry.target.classList.add("arriving");observer.unobserve(entry.target);}
    }),{threshold:0.06});
    $$(".section").forEach(section=>observer.observe(section));
  }
  const query=new URLSearchParams(location.search).get("q");
  if(query){input.value=query;focusSearch();}
})();
