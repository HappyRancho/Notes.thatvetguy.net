"""Compact community pages and browser-local email templates; no support backend."""
from pathlib import Path
from html import escape as e
from urllib.parse import urlencode
import json
ROOT=Path(__file__).resolve().parent.parent
DATA=json.loads((ROOT/'data/community.json').read_text())
FAQS=[q for group in DATA['faqGroups'] for q in group['items']]
EMAIL=DATA['email']
# key, visible label, field type, additional details
FORMATS={
 'request':dict(title='Request a resource',tag='Build the library',icon='book',tone='mint',description='Tell us the title, subject and material you need.',subject='Rx Notes | Resource request',fields=[('resource','Resource title / topic','text',False),('subject','Subject','text',False),('year','Professional year','year',False),('type','Resource type','kind',False),('reason','What would this help you study?','textarea',False),('edition','Author / edition','text',True),('source','Known source URL','url',True),('remarks','Remarks','textarea',True),('name','Your name / username (optional)','text',True)]),
 'report':dict(title='Report an error',tag='Help us put it right',icon='shield',tone='peach',description='Broken link, wrong detail or bug? Tell us what happened.',subject='Rx Notes | Error report',fields=[('issue','Issue / short summary','text',False),('type','Issue type','issue-kind',False),('date','Encountered on date','date',False),('page','Affected page / resource URL','url',False),('description','What happened?','textarea',False),('resource','Resource / file name','text',True),('file','File ID (if known)','text',True),('device','Device / browser','text',True),('steps','Steps to reproduce','textarea',True),('expected','Expected behaviour','textarea',True),('actual','Actual behaviour','textarea',True),('remarks','Remarks','textarea',True),('screenshot','Screenshot link (optional)','url',True),('name','Your name / username (optional)','text',True)]),
 'contact':dict(title='Contact the team',tag='One inbox. Real people.',icon='message',tone='sky',description='Questions, feedback or an idea for Rx Notes? We would like to hear from you.',subject='Rx Notes | General enquiry',fields=[('topic','Topic','text',False),('message','Your message','textarea',False),('name','Your name / username (optional)','text',False)]),
 'contribute':dict(title='Contribute a resource',tag='Pass the good notes on',icon='people',tone='purple',description='Share something you are entitled to contribute, with its original credit and source.',subject='Rx Notes | Resource contribution',fields=[('resource','Title / subject','text',False),('source','Original source URL','url',False),('credit','Original author / publisher credit','text',False),('permission','Your permission to share this material','textarea',False),('remarks','Remarks','textarea',True),('name','Your name / username (optional)','text',True)]),
 'rights':dict(title='Copyright & credit concerns',tag='Respect the work behind the work',icon='paper',tone='yellow',description='No copyright infringement is intended. Send the affected links and your connection to the work. We will review promptly and remove affected links or material as soon as possible.',subject='Rx Notes | Copyright or credit concern',fields=[('resource','Work / material title','text',False),('page','Affected page / file URL','url',False),('relationship','Your connection to the work','text',False),('action','Correction / removal requested','textarea',False),('name','Your name / organisation','text',False),('source','Original source / supporting information','textarea',True),('remarks','Remarks','textarea',True)])
}

def draft(key):
 f=FORMATS[key];body='Hello ThatVetGuy team,\n\n'+f['title']+'\n\n'+'\n'.join(label+': [Add details]' for _,label,_,_ in f['fields'])
 if key in ['report','request']:body+='\nScreenshot / attachment: [Attach a screenshot in your email app, if useful]'
 return body+'\n\nThank you.'

def mailto(key,body=None):return 'mailto:'+EMAIL+'?'+urlencode({'subject':FORMATS[key]['subject'],'body':body or draft(key)})
def jump_links(b):
 return '<nav class="support-jumps" aria-label="Community sections">'+''.join(b.link('#'+key,b.icon(f['icon'])+'<span>'+('Request' if key=='request' else 'Report' if key=='report' else 'Copyright' if key=='rights' else key.title())+'</span>') for key,f in FORMATS.items())+b.link('/faq/',b.icon('book')+'<span>FAQ</span>')+'</nav>'
def field(key,spec):
 name,label,kind,_=spec;ident='request-file-id' if key=='report' and name=='file' else key+'-'+name
 attrs=' id="'+ident+'" name="'+name+'" data-email-label="'+e(label,quote=True)+'"'
 choices={'year':['Not specified','1st Year','2nd Year','3rd Year','4th Year','Other / not applicable'],'kind':['Not specified','Notes','Book / handbook','Question bank','Practical material','Other'],'issue-kind':['Not specified','Broken / inaccessible link','Incorrect information / edition','Website bug','Other']}
 if kind in choices:control='<select'+attrs+'>'+''.join('<option value="'+('' if i==0 else e(value,quote=True))+'">'+e(value)+'</option>' for i,value in enumerate(choices[kind]))+'</select>'
 elif kind=='textarea':control='<textarea'+attrs+' rows="3"></textarea>'
 else:control='<input'+attrs+' type="'+kind+'"'+(' inputmode="url" placeholder="https://…"' if kind=='url' else '')+' autocomplete="off">'
 return '<div class="support-field'+(' support-field-wide' if kind=='textarea' or name not in ['year','type','date','name'] else '')+'"><label for="'+ident+'">'+e(label)+'</label>'+control+'</div>'
def panel(b,key):
 f=FORMATS[key];body='<details class="support-panel" id="'+key+'" open><summary><span class="rx-row-icon '+f['tone']+'">'+b.icon(f['icon'])+'</span><span><small>'+e(f['tag'])+'</small><h2>'+e(f['title'])+'</h2></span>'+b.icon('chevron')+'</summary><div class="support-panel-body"><p>'+e(f['description'])+'</p>'
 if key=='contact':body+='<p class="support-address">'+e(EMAIL)+'</p>'
 body+='<form data-support-form="'+key+'" data-email-subject="'+e(f['subject'],quote=True)+'" action="mailto:'+EMAIL+'" method="post" enctype="text/plain"><div class="support-fields">'+''.join(field(key,s) for s in f['fields'] if not s[3])+'</div>'
 extra=[s for s in f['fields'] if s[3]]
 if extra:body+='<details class="support-extra"><summary>Additional details <span>optional</span>'+b.icon('chevron')+'</summary><div class="support-fields">'+''.join(field(key,s) for s in extra)+'</div></details>'
 if key=='report':body+='<p class="support-hint">Attach screenshots in your email app after the draft opens, or add a screenshot link above. This page does not upload files.</p>'
 body+='<div class="support-actions">'+b.link(mailto(key),'Open email draft '+b.icon('arrow'),'support-compose request-email' if key=='request' else 'support-compose').replace('<a ','<a data-compose ',1)+'<button class="support-copy js-only" type="button" data-copy-draft>Copy email draft</button></div><p class="support-status" role="status" aria-live="polite"></p><details class="support-preview"><summary>Preview email template '+b.icon('chevron')+'</summary><label for="draft-'+key+'" class="sr-only">Email template for '+e(f['title'])+'</label><textarea id="draft-'+key+'" data-draft readonly rows="10">'+e(draft(key))+'</textarea></details><noscript><p class="support-hint">Open the template and fill in your details in your email app.</p></noscript></form></div></details>'
 return '<!--email_off-->'+body+'<!--/email_off-->'

def about(b):
 body=b.article_intro('About Rx Notes','For future vets. Thoughtfully organised.').replace('container reading-page','container reading-page community-page',1)
 body+='<section class="community-note"><span class="community-eyebrow">By the ThatVetGuy team · Independent project</span><h2>Built for the student behind the syllabus.</h2><p>Finding good notes should not be another entrance exam. Rx Notes brings credited notes, books and practical material into one organised library for veterinary students.</p></section>'
 body+='<section class="community-section"><header><h2>What you will find here</h2><p>Different resources. One familiar shelf.</p></header><div class="community-features">'
 for title,detail,url,icon,tone in [('Notes by subject','Topic notes and TANUVAS collections.','/bvsc/','paper','sky'),('An open book library','Broad categories, authors and available copies.','/books/','book','mint'),('A plan for your syllabus','Checklists, course outlines and practical resources.','/bvsc/syllabus/','check','yellow'),('Revision & study tools','Question banks, apps and study guides.','/objective/','cap','peach')]:
  body+=b.link(url,'<span class="rx-row-icon '+tone+'">'+b.icon(icon)+'</span><span><h3>'+e(title)+'</h3><p>'+e(detail)+'</p></span>'+b.icon('arrow'),'community-feature')
 body+='</div></section><section class="community-section community-start"><h2>Your first three steps</h2><ol><li><strong>Find your subject.</strong><span>Choose a professional year or browse the open book library.</span></li><li><strong>Check your course.</strong><span>Compare the syllabus checklist with your university’s current plan.</span></li><li><strong>Read, recall, repeat.</strong><span>Use notes with your prescribed texts and supervised practical work.</span></li></ol></section>'
 body+='<details class="community-letter"><summary>A note from the team '+b.icon('chevron')+'</summary><div><p>If you are behind, confused, or quietly wondering whether everyone else has it figured out: you belong here too. One difficult viva is not a verdict on the vet you can become.</p><p>Use the notes. Question the answers. Credit the people who did the work. Share what helps—good resources do not become less useful when your classmates have them too.</p><p>Keep learning, ask for help, and be kind to the person beside you. There is room for all of us to become better at this.</p><p class="community-signature">— A ThatVetGuy team member</p></div></details>'
 body+='<section class="community-section community-credits"><h2>Credit, care & clarity</h2><p>Original authors and publishers retain their rights. Rx Notes is not an official university or VCI website, and inclusion does not imply ownership or medical review. External access can change; check the linked copy’s edition and your current course requirements.</p><p>Clinical references support study and supervised use. Follow current species-specific guidance and qualified supervision when treating patients.</p><div class="support-actions">'+b.link('/faq/','Read the FAQ '+b.icon('arrow'),'support-compose')+b.link('/request-resource/','Community & Support '+b.icon('people'),'support-secondary')+'</div></section></div>'
 b.write_page('/about/','About Rx Notes — Veterinary Student Library','Meet Rx Notes, an independent ThatVetGuy study library for veterinary students. Explore its features, how to start, source credits and community support.',body)

def support(b):
 body=b.article_intro('Community & Support','Requests, reports and a helping hand.').replace('container reading-page','container reading-page community-page support-page',1)
 body+=jump_links(b)+'<p id="request-context" class="support-context" role="status"></p>'
 body+=''.join(panel(b,key) for key in FORMATS)
 body+='<p class="support-hint support-privacy">Your form details stay in this browser until you choose to open or copy an email draft. We do not submit or store them on the website.</p></div>'
 b.write_page('/request-resource/','Community & Support — Requests, Reports & Contact','Request a veterinary resource, report an error or copyright concern, contribute material, or contact Rx Notes with a structured email draft.',body)

def faq(b):
 body=b.article_intro('FAQ','Quick answers, so you can get back to learning.').replace('container reading-page','container reading-page community-page faq-page',1)
 body+='<nav class="faq-jumps support-jumps" aria-label="FAQ topics">'+''.join(b.link('#'+g['id'],b.icon(g['icon'])+'<span>'+e(g['title'])+'</span>') for g in DATA['faqGroups'])+'</nav>'
 for group in DATA['faqGroups']:
  body+='<section class="faq-group" id="'+group['id']+'"><header><span class="rx-row-icon '+group['tone']+'">'+b.icon(group['icon'])+'</span><h2>'+e(group['title'])+'</h2><small>'+str(len(group['items']))+' answers</small></header>'
  for q in group['items']:
   body+='<details class="community-question" id="faq-'+q['id']+'"><summary><h3>'+e(q['question'])+'</h3>'+b.icon('chevron')+'</summary><div><p data-faq-answer><!--email_off-->'+e(q['answer'])+'<!--/email_off--></p>'+(b.link(q['href'],e(q['label'])+' '+b.icon('arrow'),'faq-next') if q.get('href') else '')+'</div></details>'
  body+='</section>'
 body+='<aside class="community-faq-help"><h2>Still have a question?</h2><p>Send it our way. Clear questions help us build better answers.</p>'+b.link('/request-resource/#contact','Contact the team '+b.icon('message'),'support-compose')+'</aside></div>'
 b.write_page('/faq/','FAQ — Veterinary Notes, Books & Community Help','Find answers about Rx Notes, getting started, veterinary books, TANUVAS notes, resource requests, bug reports, screenshots, contributions and copyright concerns.',body)

def render(b):about(b);support(b);faq(b)
