"""Server-rendered, citable book pages; download providers are stated literally."""
from pathlib import Path
from html import escape as e
import re,json
from book_catalogue import books,route
from library import slug
ROOT=Path(__file__).resolve().parent.parent
def cover(b,book):
 c=book['cover'];symbolic=c['kind']=='symbolic-cover'
 label='Symbolic cover' if symbolic else 'Book cover'
 return '<figure class="book-cover"><img src="'+e(c['path'],quote=True)+'" width="'+str(c['width'])+'" height="'+str(c['height'])+'" alt="'+e(label+' — '+book['title'],quote=True)+'" fetchpriority="high" decoding="async">'+('<figcaption>Symbolic cover</figcaption>' if symbolic else '')+'</figure>'
def access_text(book):
 if book['telegram']:return 'This button opens the book’s Telegram post. View or download the file there.'+(' This is a private collection; access to its posts is required.' if '/c/' in book['telegram'] else '')
 if book.get('primaryDrive') or book['files']:return 'View or download this copy in Google Drive. Check its title page and edition before use.'
 return 'This is a reading recommendation. A linked copy is not currently available; you can request one.'
def facts(book):
 fields=[]
 if book.get('author'):fields.append(('Authors / editors',book['author']))
 if book['subjects']:fields.append(('Study area',', '.join(s['name'] for s in book['subjects'])));fields.append(('Professional year',', '.join(str(y)+('st' if y==1 else 'nd' if y==2 else 'rd' if y==3 else 'th')+' Year' for y in sorted({s['year'] for s in book['subjects']}))))
 fields.extend([('Resource type',book['type']),('Access',book['access'])])
 info=book.get('bibliography') or {}
 if info.get('publisher'):fields.append(('Reference publisher',info['publisher']))
 if info.get('referencePublishedDate'):fields.append(('Bibliographic year',str(info['referencePublishedDate'])+' · linked edition may differ'))
 if book.get('humanReference'):fields.append(('Scope','General medical reference; pair with veterinary teaching'))
 return '<dl class="book-facts">'+''.join('<div><dt>'+e(k)+'</dt><dd>'+e(v)+'</dd></div>' for k,v in fields)+'</dl>'
def breadcrumbs(book):
 if book['subjects']:
  s=book['subjects'][0];return [('BVSc','/bvsc/'),(str(s['year'])+('st' if s['year']==1 else 'nd' if s['year']==2 else 'rd' if s['year']==3 else 'th')+' Year',f'/bvsc/year-{s["year"]}/'),('Books','/books/')]
 return [('Books','/books/')]
def page(b,book):
 subject=book['subjects'][0]['name'] if book['subjects'] else 'veterinary revision' if book['collection'] in ['objective-notes','question-banks'] else 'clinical reference'
 desc=book['title']+(' by '+book['author'] if book.get('author') else '')+'. '+book['description']
 if len(desc)>175:desc=desc[:172].rsplit(' ',1)[0]+'.'
 intro=b.article_intro(book['title'],'',breadcrumbs(book));body=intro.split('<header class="reading-header',1)[0].replace('container reading-page','container reading-page book-detail',1)
 rid=book.get('resourceId') or ('book-guide-'+book['id'] if book.get('primaryUrl') else None);aliases=''
 if rid and rid in b.CATALOGUE:
  r=b.CATALOGUE[rid];aliases=''.join('<span class="anchor-alias" id="file-'+v['id']+'"></span>' for v in r['variants'] if v['id']!=rid)
 target=book['primaryUrl'] or '/request-resource/?resource='+__import__('urllib.parse',fromlist=['quote']).quote(book['title'])
 button=b.link(target,b.icon('telegram' if book['telegram'] else 'book' if book['primaryUrl'] else 'message')+'<span>'+book['downloadLabel']+'</span>'+b.icon('external' if book['primaryUrl'] else 'arrow'),'book-download'+(' file-open' if rid else ''))
 body+='<section class="book-overview"><div class="book-overview-grid">'+cover(b,book)+'<div class="book-hero-copy"><span class="book-category">'+e(book['type'])+' · '+e(('Year '+str(book['subjects'][0]['year'])) if book['subjects'] else 'Exam revision' if book['collection'] in ['objective-notes','question-banks'] else 'Clinical reference')+'</span><h1>'+e(book['title'])+'</h1>'
 if book.get('author'):body+='<p class="book-author">'+e(book['author'])+'</p>'
 body+='</div></div><article class="book-access"'+(' id="file-'+rid+'" data-resource-id="'+rid+'"' if rid else '')+'>'+aliases+button+'<p>'+access_text(book)+'</p></article></section>'
 body+='<section class="book-about"><h2>About this '+('reference' if book['type']=='Reference sheet' else 'book')+'</h2><p>'+e(book['description'])+'</p>'
 if book.get('humanReference'):body+='<p>This is a general medical text. Use veterinary-specific teaching and current species-specific references for clinical decisions.</p>'
 if book['clinical']:body+='<aside class="book-clinical-note" role="note">For study and supervised reference. Verify the species, dose, edition and current clinical guidance before treating a patient.</aside>'
 body+='</section>'
 body+='<details class="book-source-details"><summary>Edition &amp; source details '+b.icon('chevron')+'</summary><div>'+facts(book)+('<p>Reference cover; the linked edition may differ.</p>' if book['cover']['kind']=='reference-cover' else '<p>Symbolic artwork made for this listing; not the publisher’s cover.</p>' if book['cover']['kind']=='symbolic-cover' else '<p>Cover extracted from a source PDF; available copies may differ.</p>')+'<p>Credit belongs to the original authors and publishers.</p>'
 if book.get('primaryDrive'):body+='<p>Primary collection: Rx Notes. File: '+e(book['primaryDrive']['name'])+'</p>'
 if book['files']:body+='<p>Collection: Vetverse. Original file '+('labels' if len(book['files'])>1 else 'label')+':</p><ul>'+''.join('<li>'+e(f['name'])+'</li>' for f in book['files'])+'</ul>'
 elif book['telegram']:body+='<p>Access is provided through the original Telegram post.</p>'
 if book.get('originalLabel'):body+='<p>Shared file label: '+e(book['originalLabel'])+'</p>'
 body+=b.link('/request-resource/?resource='+__import__('urllib.parse',fromlist=['quote']).quote(book['title'])+'#report','Report a link or credit issue '+b.icon('arrow'),'book-report')+'</div></details>'
 copies=book['files'] if book.get('primaryDrive') else book['files'][1:]
 if copies:body+='<details class="book-other-copies"><summary>Other available copies '+b.icon('chevron')+'</summary><ul>'+''.join('<li><span>'+e(f['name'])+'</span>'+b.link(f['url'],'Open in Drive '+b.icon('external'))+'</li>' for f in copies)+'</ul></details>'
 if book['subjects']:body+=b.link(f'/bvsc/year-{book["subjects"][0]["year"]}/'+slug(book['subjects'][0]['name'])+'/#books','Back to subject books '+b.icon('arrow'),'book-subject-link')
 else:body+=b.link('/objective/' if book['collection'] in ['objective-notes','question-banks'] else '/clinical/'+str(book['collection'])+'/' if book['collection'] in ['drug-index','handbooks'] else '/books/','Back to collection '+b.icon('arrow'),'book-subject-link')
 body+='</div>';suffix=' — Telegram Download' if book['telegram'] else ' — Details & Drive Access' if book['primaryUrl'] else ' — BVSc Reading Guide'
 b.write_page(book['page'],book['title']+suffix,desc,body)

def library_categories():
 return [
  ('basic-sciences','Basic Sciences','Anatomy, physiology & biochemistry','flask','mint'),
  ('disease-diagnostics','Disease & Diagnostics','Pathology, microbiology & parasitology','shield','peach'),
  ('animal-science','Animal Science','Nutrition, breeding & livestock care','paw','yellow'),
  ('clinical','Clinical Medicine & Surgery','Medicine, surgery, reproduction & handbooks','stethoscope','sky'),
  ('drug-references','Pharmacology & Drug References','Pharmacology, doses & drug indexes','pill','mint'),
  ('public-health','Public Health & Food Science','Public health, epidemiology & food technology','people','peach'),
  ('exam-prep','Exam Preparation','Objective notes & question banks','cap','yellow'),
 ]

def library_category(book):
 if book['collection'] in ['objective-notes','question-banks']:return 'exam-prep'
 if book['collection']=='drug-index':return 'drug-references'
 if book['collection']=='handbooks':return 'clinical'
 names={s['name'] for s in book['subjects']}
 if names & {'Veterinary Anatomy','Veterinary Physiology','Veterinary Biochemistry'}:return 'basic-sciences'
 if names & {'Veterinary Pathology','Veterinary Microbiology','Veterinary Parasitology'}:return 'disease-diagnostics'
 if names & {'Animal Nutrition','Animal Genetics and Breeding','Livestock Production Management','Veterinary and Animal Husbandry Extension Education','Livestock Farm Practices'}:return 'animal-science'
 if 'Veterinary Pharmacology and Toxicology' in names:return 'drug-references'
 if names & {'Veterinary Public Health and Epidemiology','Livestock Products Technology'}:return 'public-health'
 return 'clinical'

def index(b):
 from subject_hubs import book_card
 from library import normal
 catalogue=books();categories=library_categories()
 short={'basic-sciences':'Basics','disease-diagnostics':'Disease','animal-science':'Animal Sci.','clinical':'Clinical','drug-references':'Drugs','public-health':'Public Health','exam-prep':'Exam Prep'}
 intro=b.article_intro('Books','').split('<header class="reading-header',1)[0]
 body=intro.replace('container reading-page','container reading-page books-directory',1)
 body+='<header class="books-library-heading"><span class="books-sketch" aria-hidden="true">'+b.icon('book')+'</span><div><h1>Books</h1><p class="rx-hand">A little shelf. A world of learning.</p></div><span class="books-total">'+str(len(catalogue))+'<small>titles</small></span></header>'
 body+='<div class="books-search js-only">'+b.icon('search')+'<label for="books-query" class="sr-only">Find a book by title, author or subject</label><input id="books-query" type="search" placeholder="Title, author or subject…" autocomplete="off" aria-controls="books-shelves"><button type="button" id="books-clear" hidden aria-label="Clear book search">'+b.icon('close')+'</button></div>'
 body+='<nav class="books-category-links" aria-label="Book categories">'+b.link('#books-shelves','<span>All Books</span><small>'+str(len(catalogue))+'</small>','books-filter').replace('<a ','<a data-book-category="all" ',1)
 for key,title,_,_,tone in categories:
  count=sum(library_category(r)==key for r in catalogue)
  body+=b.link('#'+key,'<span>'+short[key]+'</span><small>'+str(count)+'</small>','books-filter').replace('<a ','<a data-book-category="'+key+'" title="'+e(title,quote=True)+'" ',1)
 body+='</nav><p class="books-count" id="books-count" role="status">'+str(len(catalogue))+' books · browse the collection</p><div id="books-shelves">'
 for key,title,description,glyph,tone in categories:
  rows=[r for r in catalogue if library_category(r)==key]
  body+='<section class="books-category" data-books-section="'+key+'" id="'+key+'"><header class="books-section-heading"><span class="rx-row-icon '+tone+'" aria-hidden="true">'+b.icon(glyph)+'</span><h2>'+title+'</h2><span>'+str(len(rows))+'</span></header><div class="books-shelf subject-book-grid">'
  for book in rows:
   keywords=normal(' '.join([title,description,book['type'],*[s['name'] for s in book['subjects']]]))
   body+=book_card(b,book).replace('data-row-search="','data-book-id="'+e(book['id'],quote=True)+'" data-book-category="'+key+'" data-row-search="'+e(keywords,quote=True)+' ',1)
  body+='</div></section>'
 body+='</div><div class="books-more-wrap js-only"><button type="button" id="books-more" hidden>Show more books '+b.icon('chevron')+'</button></div><div class="books-empty" id="books-empty" hidden><h2>No books found</h2><p>Try a shorter title, an author’s surname or another subject.</p>'+b.link('/request-resource/','Request a book '+b.icon('arrow'),'book-subject-link')+'</div>'
 b.write_page('/books/','Veterinary Books, Textbooks & Clinical References','Explore veterinary books by broad subject: basic sciences, disease, animal science, clinical medicine, drug references, public health and exam preparation.',body+'</div>',[(r['title'],r['page']) for r in catalogue])
def social_cards():
 from PIL import Image,ImageDraw,ImageFont
 import textwrap
 out=ROOT/'assets/social/books';out.mkdir(parents=True,exist_ok=True)
 fontpath='/tmp/balsamiq-social.ttf' if Path('/tmp/balsamiq-social.ttf').exists() else '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'
 for book in [*books(),{'id':'index','title':'Veterinary Books Library','access':'Notes.ThatVetGuy','cover':None}]:
  image=Image.new('RGB',(1200,630),'#eaf8ff');d=ImageDraw.Draw(image);d.rounded_rectangle((40,40,1160,590),radius=30,fill='white');left=80
  c=book.get('cover')
  if c and (ROOT/c['path'].lstrip('/')).exists():
   with Image.open(ROOT/c['path'].lstrip('/')) as art:art=art.convert('RGB');art.thumbnail((220,360));image.paste(art,(80,145));left=345
  d.text((left,85),'Rx Notes · ThatVetGuy',font=ImageFont.truetype(fontpath,26),fill='#0769ce')
  y=170
  for line in textwrap.wrap(book['title'],width=30 if left>100 else 38)[:5]:d.text((left,y),line,font=ImageFont.truetype(fontpath,43),fill='#101b43');y+=53
  d.text((left,530),book['access'],font=ImageFont.truetype(fontpath,23),fill='#475571');image.save(out/(book['id']+'.webp'),'WEBP',quality=84,method=4)
def render(b):
 social_cards();index(b)
 for book in books():page(b,book)
