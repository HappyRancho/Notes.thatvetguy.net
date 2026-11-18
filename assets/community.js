/* Drafts stay on this page: opening a mail app never sends a message. */
(()=>{'use strict';
const email='contact@thatvetguy.net',params=new URLSearchParams(location.search),forms=[...document.querySelectorAll('[data-support-form]')];
const fields=form=>[...form.querySelectorAll('[data-email-label]')];
forms.forEach(form=>{
 const kind=form.dataset.supportForm,subject=form.dataset.emailSubject,preview=form.querySelector('[data-draft]'),compose=form.querySelector('[data-compose]'),status=form.querySelector('[role=status]');
 const set=(name,value)=>{const field=form.elements.namedItem(name);if(field&&value)field.value=value.slice(0,2000);};
 if(['request','report'].includes(kind))set('resource',params.get('resource'));
 if(kind==='report'){
  set('file',params.get('file'));set('page',params.get('page'));
  const date=new Date();set('date',[date.getFullYear(),String(date.getMonth()+1).padStart(2,'0'),String(date.getDate()).padStart(2,'0')].join('-'));
 }
 const update=()=>{
  const lines=fields(form).map(field=>field.dataset.emailLabel+': '+(field.value.trim()||'[Add details]'));
  if(['report','request'].includes(kind))lines.push('Screenshot / attachment: [Attach a screenshot in your email app, if useful]');
  const title=form.closest('.support-panel').querySelector('h2').textContent;
  const body='Hello ThatVetGuy team,\n\n'+title+'\n\n'+lines.join('\n')+'\n\nThank you.';
  preview.value=body;compose.href='mailto:'+email+'?subject='+encodeURIComponent(subject)+'&body='+encodeURIComponent(body);status.textContent='';return body;
 };
 form.addEventListener('input',update);form.addEventListener('change',update);form.addEventListener('submit',e=>e.preventDefault());update();
 form.querySelector('[data-copy-draft]').addEventListener('click',async()=>{
  const body=update(),text='To: '+email+'\nSubject: '+subject+'\n\n'+body;
  try{await navigator.clipboard.writeText(text);status.textContent='Email draft copied. Paste it into your email app and attach any screenshots.';}
  catch{const details=form.querySelector('.support-preview');details.open=true;preview.focus();preview.select();status.textContent='Copy the selected template, then email it to '+email+'.';}
 });
});
const context=document.querySelector('#request-context');
if(context&&(params.get('file')||params.get('resource')))context.textContent=(params.get('file')?'File ID: '+params.get('file'):'Resource: '+params.get('resource'))+'. Included in the matching draft.';
let target='';try{target=decodeURIComponent(location.hash.slice(1));}catch{}
if(!target)target=params.get('file')?'report':'request';
document.querySelectorAll('.support-panel').forEach(panel=>panel.open=panel.id===target);
})();
