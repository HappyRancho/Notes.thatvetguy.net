/* This file is emitted only when approval, explicit enablement and a real slot are configured. */
(()=>{'use strict';if(location.hostname!=='notes.thatvetguy.net')return;
for(const unit of document.querySelectorAll('[data-rx-ad-unit]')){
 if(unit.dataset.rxAdRequested||!/^\d{10}$/.test(unit.dataset.adSlot||'')||unit.clientWidth<=0)continue;
 unit.dataset.rxAdRequested='true';try{(window.adsbygoogle=window.adsbygoogle||[]).push({});}catch{unit.dataset.rxAdRequested='failed';}
}})();
