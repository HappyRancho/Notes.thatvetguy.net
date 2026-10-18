"""Original reading guidance; recommendations are not downloadable book claims."""
import json
from html import escape as e
from pathlib import Path
from library import slug
ROOT=Path(__file__).resolve().parent.parent

def render(b):
 books=json.loads((ROOT/'data/book-recommendations.json').read_text())['books']
 for year in range(1,5):
  label=b.DATA['labels'][str(year)];own=[r for r in books if r['year']==year];path=f'/bvsc/year-{year}/books/'
  desc=f'A focused book list for {label} BVSc & AH, organised by subject. Start with one core text, then use a reference for difficult topics.'
  body=b.article_intro('Best Books for '+label,desc,[('BVSc','/bvsc/'),(label,f'/bvsc/year-{year}/')])+'<p class="source-note">Choose the edition prescribed by your department. These are reading recommendations; check your college library or a legitimate bookseller for access.</p>'
  for subject in dict.fromkeys(r['subject'] for r in own):
   body+='<section class="content-section" id="'+slug(subject)+'"><h2>'+e(subject)+'</h2><div class="book-guide-list">'
   for r in [r for r in own if r['subject']==subject]:
    body+='<article class="book-guide-card"><span class="rx-row-icon sky" aria-hidden="true">'+b.icon('book')+'</span><div><h3>'+e(r['title'])+'</h3><p class="book-author">'+e(r['author'])+'</p><p>'+e(r['description'])+'</p></div></article>'
   body+='</div>'+b.link(f'/bvsc/year-{year}/'+slug(subject)+'/','Read '+e(subject)+' notes '+b.icon('arrow'),'text-link')+'</section>'
  body+='<p class="source-note">Book selection draws on VetBVSc and established veterinary reading lists. Author and publisher references are recorded with the recommendations. Notes retain their original source credits.</p></div>'
  b.write_page(path,'Best Books for '+label+' BVSc & AH',desc,body,[(r['title'],path+'#'+slug(r['subject'])) for r in own])
 from library_views import chunks,teaser,empty,file_card
 for key,title,desc,rows in [
  ('handbooks','Handbooks Collection','Veterinary handbook material in one place for BVSc & AH students. Check the original edition and use clinical references alongside supervised training.',[r for r in b.RECORDS if 'handbooks' in r['collections']]),
  ('drug-index','Drug Index Collection','Veterinary drug indexes, a drug handbook, a wall reference and vaccination schedules in one collection. Open a resource in Telegram and check its edition before clinical use.',[r for r in b.RECORDS if 'drug-index' in r['collections']])]:
  if key=='drug-index':
   from collection_cards import intro,cards
   body=intro(b,title,desc,[('Clinical','/clinical/')],clinical=True)+'<section class="content-section rx-drug-resources"><div class="rx-collection-heading"><h2>Drug references &amp; schedules</h2>'+b.icon('stethoscope')+'</div>'+cards(b,rows,clinical=True)+'</section><p class="rx-telegram-note">'+b.icon('telegram')+'<span>These links open a private Telegram collection. You need access to that collection to view its posts.</span></p></div>'
  else:
   body=b.article_intro(title,desc,[('Clinical','/clinical/')])+'<p class="clinical-callout" role="note">For study, not prescribing. Verify the species, dose and current clinical guidance before treating a patient.</p><section class="content-section"><h2>'+('Available handbooks' if key=='handbooks' else 'Drug references & schedules')+'</h2>'+(chunks(b,rows,file_card if key=='drug-index' else teaser) if rows else empty(b,'Handbooks are coming soon'))+'</section>'+('<p class="source-note">These links open a private Telegram collection. You need access to that collection to view its posts.</p>' if key=='drug-index' else '')+'</div>'
  b.write_page('/clinical/'+key+'/',title,desc,body,[(r['title'],r['permalink']) for r in rows])
