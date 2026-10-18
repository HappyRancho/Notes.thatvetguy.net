"""Original reading guidance; recommendations are not downloadable book claims."""
import json
from html import escape as e
from pathlib import Path
from library import slug
ROOT=Path(__file__).resolve().parent.parent

def render(b):
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
