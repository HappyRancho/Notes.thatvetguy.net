"""Server-rendered, citable book pages; download providers are stated literally."""
from pathlib import Path
from html import escape as e
import re,json
from book_catalogue import books,route
from library import slug
ROOT=Path(__file__).resolve().parent.parent
def cover(b,book):
 c=book.get('cover')
 if c:
  caption='Reference cover; the linked edition may differ.' if c['kind']=='reference-cover' else 'Title-page preview from the linked file.' if c['kind']=='title-page' else 'Cover from the linked file.' if c['kind']=='file-cover' else 'Preview from the linked source file.'
  return '<figure class="book-cover"><img src="'+e(c['path'],quote=True)+'" width="'+str(c['width'])+'" height="'+str(c['height'])+'" alt="'+e(('Reference cover for ' if c['kind']=='reference-cover' else 'Source preview for ')+book['title'],quote=True)+'" fetchpriority="high" decoding="async"><figcaption>'+caption+'</figcaption></figure>'
 return '<div class="book-cover book-cover-unavailable" role="img" aria-label="No verified cover available for '+e(book['title'],quote=True)+'">'+b.icon('book')+'<span>Cover unavailable</span></div>'
def access_text(book):
 if book['telegram']:return 'This button opens the book’s Telegram post. View or download the file there.'+(' This is a private collection; access to its posts is required.' if '/c/' in book['telegram'] else '')
 if book['files']:return 'View or download this copy in Google Drive. Check its title page and edition before use.'
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
 button=b.link(target,b.icon('telegram' if book['telegram'] else 'book' if book['files'] else 'message')+'<span>'+book['downloadLabel']+'</span>'+b.icon('external' if book['primaryUrl'] else 'arrow'),'book-download'+(' file-open' if rid else ''))
 body+='<section class="book-overview"><div class="book-overview-grid">'+cover(b,book)+'<div class="book-hero-copy"><span class="book-category">'+e(book['type'])+' · '+e(subject)+'</span><h1>'+e(book['title'])+'</h1>'
 if book.get('author'):body+='<p class="book-author">'+e(book['author'])+'</p>'
 body+='<article class="book-access"'+(' id="file-'+rid+'" data-resource-id="'+rid+'"' if rid else '')+'>'+aliases+button+'<p>'+access_text(book)+'</p></article></div></div></section>'
 body+='<section class="book-about"><h2>About this '+('reference' if book['type']=='Reference sheet' else 'book')+'</h2><p>'+e(book['description'])+'</p>'
 if book.get('humanReference'):body+='<p>This is a general medical text. Use veterinary-specific teaching and current species-specific references for clinical decisions.</p>'
 if book['clinical']:body+='<aside class="book-clinical-note" role="note">For study and supervised reference. Verify the species, dose, edition and current clinical guidance before treating a patient.</aside>'
 body+='</section>'
 if book['subjects']:
  guide=b.SUBJECTS[book['subjects'][0]['name']];themes=guide['topics'][:3]
  note='Use this alongside '+subject.lower()+' lectures and practicals. Start with the topics in your current unit, then test whether you can explain the key ideas without the page in front of you.'
 elif book['collection'] in ['objective-notes','question-banks']:
  note='Useful for a second pass after learning the topic. Attempt a short set, check each answer against your teaching notes and keep a list of concepts to revisit; question collections can contain errors or older answers.'
 else:note='Use this as a reference to look up a specific question, rather than a substitute for current clinical guidance. Confirm the edition, species and context before relying on a table or recommendation.'
 body+='<section class="book-study"><header><span class="rx-row-icon yellow">'+b.icon('paper')+'</span><h2>A study note</h2></header><p>'+e(note)+'</p><small class="book-editorial">Rx Notes reading guidance</small></section>'
 body+='<details class="book-source-details"><summary>Book details, edition &amp; credits '+b.icon('chevron')+'</summary><div>'+facts(book)+'<p>Credit remains with the original authors and publishers. Reference covers and bibliographic details may describe a different edition from the linked copy. Check its title page before citing it.</p>'
 if book['files']:body+='<p>Collection: Vetverse. Original file '+('labels' if len(book['files'])>1 else 'label')+':</p><ul>'+''.join('<li>'+e(f['name'])+'</li>' for f in book['files'])+'</ul>'
 elif book['telegram']:body+='<p>Access is provided through the original Telegram post.</p>'
 if book.get('originalLabel'):body+='<p>Shared file label: '+e(book['originalLabel'])+'</p>'
 body+='<p>Last source check: <time datetime="'+book['lastVerified']+'">'+book['lastVerified']+'</time>.</p>'+b.link('/request-resource/?resource='+__import__('urllib.parse',fromlist=['quote']).quote(book['title'])+'#report','Report a link or credit issue '+b.icon('arrow'),'book-report')+'</div></details>'
 if len(book['files'])>1:body+='<details class="book-other-copies"><summary>Other available copies '+b.icon('chevron')+'</summary><ul>'+''.join('<li><span>'+e(f['name'])+'</span>'+b.link(f['url'],'Open in Drive '+b.icon('external'))+'</li>' for f in book['files'][1:])+'</ul></details>'
 if book['subjects']:body+=b.link(f'/bvsc/year-{book["subjects"][0]["year"]}/'+slug(book['subjects'][0]['name'])+'/#books','Back to subject books '+b.icon('arrow'),'book-subject-link')
 else:body+=b.link('/objective/' if book['collection'] in ['objective-notes','question-banks'] else '/clinical/'+str(book['collection'])+'/' if book['collection'] in ['drug-index','handbooks'] else '/books/','Back to collection '+b.icon('arrow'),'book-subject-link')
 body+='</div>';suffix=' — Telegram Download' if book['telegram'] else ' — Details & Drive Access' if book['files'] else ' — BVSc Reading Guide'
 b.write_page(book['page'],book['title']+suffix,desc,body)

def index(b):
 from library_views import chunks
 def card(builder,book):
  image='<img src="'+book['cover']['path']+'" width="'+str(book['cover']['width'])+'" height="'+str(book['cover']['height'])+'" alt="" loading="lazy" decoding="async">' if book.get('cover') else b.icon('book')
  return '<article class="book-directory-card">'+b.link(book['page'],'<span class="book-directory-cover" aria-hidden="true">'+image+'</span><span><strong>'+e(book['title'])+'</strong><small>'+e((book.get('author')+' · ' if book.get('author') else '')+book['access'])+'</small></span>'+b.icon('chevron'))+'</article>'
 body=b.article_intro('Veterinary Books Library','Subject books, objective resources and clinical handbooks for BVSc & AH study. Open a book for its details, cover and available Telegram or Google Drive access.').replace('container reading-page','container reading-page books-directory',1)
 categories=[('year-'+str(y),str(y)+('st' if y==1 else 'nd' if y==2 else 'rd' if y==3 else 'th')+' Year',[r for r in books() if any(s['year']==y for s in r['subjects'])]) for y in range(1,5)]+[('objective','Objective & Competition',[r for r in books() if r['collection'] in ['objective-notes','question-banks']]),('clinical','Clinical References',[r for r in books() if r['collection'] in ['handbooks','drug-index']])]
 body+='<nav class="books-year-links" aria-label="Book collections">'+''.join(b.link('#'+key,title) for key,title,_ in categories)+'</nav>'
 for key,title,rows in categories:body+='<section class="book-directory-section" id="'+key+'"><header><h2>'+title+'</h2><p>'+str(len(rows))+' resources</p></header>'+chunks(b,rows,card,24)+'</section>'
 b.write_page('/books/','Veterinary Books, Textbooks & Clinical References', 'Browse BVSc & AH books by professional year, objective collections and clinical references. Each title has its own details and available download links.',body+'</div>',[(r['title'],r['page']) for r in books()])
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
