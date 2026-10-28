"""Handbook and drug-reference collections, using the same Rx book cards."""
def render(b):
 from collection_cards import intro,cards
 for key,title,desc in [
  ('handbooks','Handbooks','Quick clinical references for everyday veterinary practice.'),
  ('drug-index','Drug Index Collection','Veterinary drug indexes, a drug handbook, a wall reference and vaccination schedules in one collection. Choose a resource to see its details and Telegram download link. Check the edition before clinical use.')]:
  rows=[r for r in b.RECORDS if key in r['collections']];drug=key=='drug-index'
  body=intro(b,title,desc,[('Clinical Resources','/#clinical')],clinical=drug,handbooks=not drug)
  if drug:body+='<section class="content-section rx-drug-resources"><div class="rx-collection-heading"><h2>Drug references &amp; schedules</h2>'+b.icon('stethoscope')+'</div>'+cards(b,rows,clinical=True)+'</section>'
  else:body+='<section class="content-section rx-handbook-resources"><h2 class="sr-only">Handbook collection</h2>'+cards(b,rows)+'</section>'
  note='Downloads use a private Telegram collection. Access is required to view its posts.' if drug else 'Each book page provides its Telegram download link. Use clinical references alongside supervised training and current guidance.'
  body+='<p class="rx-telegram-note">'+b.icon('telegram')+'<span>'+note+'</span></p></div>'
  b.write_page('/clinical/'+key+'/',title,desc,body,[(r['title'],r['page']) for r in rows])
