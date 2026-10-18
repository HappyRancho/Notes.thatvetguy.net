/* Apply a saved preference before first paint; leave both media metadata tags intact. */
(()=>{document.documentElement.classList.add('js');try{const value=localStorage.getItem('tvg-theme');if(['light','dark'].includes(value))document.documentElement.dataset.theme=value}catch{}})();
