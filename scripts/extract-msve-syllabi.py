#!/usr/bin/env python3
"""Extract complete unit-wise syllabus topics from the original outline PDFs."""
from pathlib import Path
import re,json,hashlib,datetime
ROOT=Path(__file__).resolve().parent.parent;outline=json.loads((ROOT/'data/course-outlines.json').read_text());mapping=json.loads((ROOT/'data/subject-map.json').read_text());sources={}

source=json.loads((ROOT/'data/msve-2016-source.json').read_text())
sources={}
parts=[];spans=[];offset=0
for page in source['pages']:
 lines=[]
 for line in page['text'].splitlines():
  if re.search(r'GAZETTE|Hkkx|Hkkjr|SEC\.|SEc\.|PART III|FRA HT|Cart .*ars',line):continue
  if re.fullmatch(r'\s*\d{2,3}\s*',line):continue
  lines.append(line.rstrip())
 text='\n'.join(lines);spans.append((offset,offset+len(text),page['page']));parts.append(text);offset+=len(text)+1
for y in range(1,5):sources[y]=('\n'.join(parts),spans)
def page_at(y,pos):return next((n for start,end,n in sources[y][1] if start<=pos<=end),sources[y][1][-1][-1])
def norm(text):
 text=re.sub(r'-\s*\n\s*','-',text);return re.sub(r'\s+',' ',text).strip()
def topics(raw,split_dashes=False):
 text=norm(raw)
 # Keep abbreviations and measurements intact, split only sentence/semicolon boundaries.
 protected={}
 def protect(m):
  key=f'ABBR{len(protected)}TOKEN';protected[key]=m[0];return key
 text=re.sub(r'\b(?:[A-Za-z]\.){2,}|\b(?:i\.e\.|e\.g\.|viz\.|etc\.|Dr\.|Mr\.|St\.)',protect,text)
 pattern=r';\s*|(?<=[.!?])\s+(?=[A-Z(])'
 if split_dashes:pattern+=r'|(?=\b(?:Equines|Ovines and caprines|Swines|Canines and Felines)\s*:)|\s*–\s*|(?<=\w)\s*-\s*(?=[A-Z])|\s+-\s*'
 chunks=re.split(pattern,text)
 result=[]
 for s in chunks:
  for key,value in protected.items():s=s.replace(key,value)
  s=s.strip(' ;')
  if s:result.append(s)
 assert re.sub(r'\W','',norm(' '.join(result)))==re.sub(r'\W','',norm(raw)),'Extraction dropped topic text'
 return result
anatomy={1:'General Anatomy',2:'Fore Limb',3:'Head and Neck',4:'Thorax',5:'Abdomen',6:'Hind Limb and Pelvis',7:'Cytology and Microscopic Anatomy',8:'Embryology'}
expected={'Veterinary Anatomy':(8,8),'Veterinary Physiology':(4,4),'Livestock Production Management':(9,8),'Veterinary Biochemistry':(3,3),'Veterinary Microbiology':(5,5),'Veterinary Pathology':(6,6),'Animal Genetics and Breeding':(3,3),'Animal Nutrition':(4,4),'Veterinary Pharmacology and Toxicology':(6,5),'Veterinary Parasitology':(5,5),'Veterinary Public Health and Epidemiology':(4,4),'Livestock Products Technology':(4,4),'Veterinary and Animal Husbandry Extension Education':(9,2),'Veterinary Surgery and Radiology':(6,6),'Veterinary Medicine':(7,5),'Veterinary Gynaecology and Obstetrics':(3,3)}
result=[]
for year,names in mapping['years'].items():
 for name in names:
  year=int(year);ref=outline['subjects'][str(year)][name];sy=ref['pdfYear'];text=sources[sy][0]
  if name=='Veterinary Clinical Practices II':sy=3;text=sources[3][0]
  if name.startswith('Veterinary Clinical Practices'):
   roman='II' if name.endswith('II') else 'I';pat=r'^VETERINARY CLINICAL PRACTICES\s*[-–]\s*'+roman+r'\s*\('
  elif name=='Livestock Farm Practices':pat=r'^LIVESTOCK FARM PRACTICES\s*\('
  elif name=='Veterinary Pharmacology and Toxicology':pat=r'^VETERINARY PHARMACOLOGY\s+Credit Hours'
  elif name=='Veterinary Public Health and Epidemiology':pat=r'^.*DEPARTMENT OF VETERINARY PUBLIC HEALTH AND EPIDEMIOLOGY'
  else:pat=r'^'+re.escape(name.upper())+r'\s+Credit Hours'
  match=re.search(pat,text,re.M);assert match,name;start=match.start()
  if name=='Veterinary Clinical Practices I':end=re.search(r'^VETERINARY CLINICAL PRACTICES\s*[-–]\s*II\s*\(',text[match.end():],re.M).start()+match.end()
  elif name=='Veterinary Clinical Practices II':end=text.index('The practical component will be dealt with internally.',start)
  elif name=='Livestock Farm Practices':end=text.index('One full day per week',start)
  else:end=text.index('ANNUAL EXAMINATION',start)
  part=text[start:end];units=[];mode='practical' if 'Practices' in name else 'theory'
  if name in expected:
   theory=re.search(r'^THEORY\s*$',part,re.M);assert theory,name;offset=theory.end();part=part[offset:];start+=offset
   events=list(re.finditer(r'^[ \t]*(?:(THEORY|PRACTICALS?|PRACTCAL)\s*$|UNIT\s*[-:–]\s*(\d+)\s*(:?)\s*([^\n]*))',part,re.M))
   retained=[];last_mode='theory'
   for ev in events:
    new_mode=('theory' if ev[1]=='THEORY' else 'practical') if ev[1] else None
    if new_mode and new_mode==last_mode:continue
    if new_mode:last_mode=new_mode
    retained.append(ev)
   events=retained
   for i,event in enumerate(events):
    if event[1]:mode='theory' if event[1]=='THEORY' else 'practical';continue
    tail=event[4].strip().lstrip('_ ');endpos=events[i+1].start() if i+1<len(events) else len(part);body_start=event.end();label='';inline=''
    if tail.startswith('('):
     if ')' in tail:label,inline=tail[1:].split(')',1)
     elif ')' in part[body_start:endpos] and len(part[body_start:endpos].split(')',1)[0])<160:
      extra,rest=part[body_start:endpos].split(')',1);label=tail[1:]+' '+extra;body_start=endpos-len(rest)
     else:label=tail[1:]
    elif ')' in tail and tail.split(')',1)[0].isupper():label,inline=tail.split(')',1)
    else:inline=tail
    body=norm(re.sub(r'\bPRACTICALS\b','',(inline+' '+part[body_start:endpos]).strip()));n=int(event[2]);label=norm(label).rstrip(' .').title()
    if name=='Veterinary Anatomy':label=anatomy[n]
    if name=='Animal Nutrition' and mode=='practical' and n==3:label='Applied Ruminant Nutrition II'
    if name.endswith('Extension Education') and mode=='practical':label=['Extension Fieldwork and Communication','Livestock Business and Project Planning'][n-1]
    if not label:label='Unit '+str(n)
    assert body,(name,mode,n)
    units.append(dict(key=mode+'-'+str(n),kind=mode,number=n,title=label,sourcePage=page_at(sy,start+event.start()),sourceText=body,topics=topics(body)))
   got=tuple(sum(u['kind']==m for u in units) for m in ['theory','practical']);assert got==expected[name],(name,got)
  elif name=='Veterinary Clinical Practices II':
   events=list(re.finditer(r'^(Ambulatory Section:|Diagnostic Laboratory Section:|Medicine Section:|Gynecology and Obstetrics Section|Surgery and Radiology Section|Pet Animal Section)\s*$',part,re.M));assert len(events)==6
   for i,event in enumerate(events):
    body=norm(part[event.end():events[i+1].start() if i+1<len(events) else len(part)])
    body=re.sub(r'Note: The Laboratory shall run in collaboration.*?different species, differential diagnosis, correlating with diseases and rationale of arriving at the conclusion\.','',body)
    units.append(dict(key='practical-'+str(i+1),kind='practical',number=None,title=event[1].strip(':'),sourcePage=page_at(sy,start+event.start()),sourceText=body,topics=topics(body)))
  else:
   body=norm(part.split('\n',1)[1]);title='Clinical Orientation and Foundational Skills' if name.endswith('Practices I') else 'Livestock Farm Practices'
   units=[dict(key='practical-1',kind='practical',number=None,title=title,sourcePage=page_at(sy,start),sourceText=body,topics=topics(body))]
  for unit in units:
   if name=='Veterinary Gynaecology and Obstetrics':
    combined=[];pending=''
    for fragment in re.split(r'\s*[-–]\s*(?=[A-Z])|;\s*',unit['sourceText']):
     pending+=((' - ' if pending else '')+fragment)
     if len(pending)>=90:combined.append(pending);pending=''
    if pending:
     if combined:combined[-1]+=' - '+pending
     else:combined=[pending]
    unit['topics']=combined
   saved=[];context='';seen={}
   for t in unit['topics']:
    match_context=re.match(r'^(Bovine|Equines|Ovines and caprines|Swines|Canines and Felines)\s*:',t)
    if match_context:context=match_context[1]
    key=name+'|'+unit['key']+'|'+context+'|'+t;seen[key]=seen.get(key,0)+1
    ident=hashlib.sha256((key+'|'+str(seen[key])).encode()).hexdigest()[:14]
    saved.append(dict(id=ident,text=t,**({'context':context} if context else {})))
   unit['topics']=saved
  primary=dict(url=source['url'],sha256=source['sha256']);ident=re.sub(r'[^a-z0-9]+','-',name.lower()).strip('-')
  result.append(dict(subject=name,slug=ident,year=year,sourcePdfYear=sy,sourceUrl=primary['url'],sourceSha256=primary['sha256'],sourcePage=page_at(sy,match.start()),originalOutlineUrl=outline['years'][str(ref['pdfYear'])]['url']+'#page='+str(ref['page']),units=units,totalTopics=sum(len(u['topics']) for u in units),unitNumbering='numbered' if name in expected else 'sections'))

  coverage={
   'Veterinary Anatomy':('1–4','5–8'),'Veterinary Physiology':('1–2','3–4'),
   'Livestock Production Management':('1–4','5–8'),'Veterinary Biochemistry':('1 and 3','2'),
   'Veterinary Microbiology':('1–3','4–5'),'Veterinary Pathology':('1–3','4–6'),
   'Animal Genetics and Breeding':('1–2','3'),'Animal Nutrition':('1–2','3–4'),
   'Veterinary Pharmacology and Toxicology':('1–2','3–5'),'Veterinary Parasitology':('1–3','4–5'),
   'Veterinary Public Health and Epidemiology':('1–2','3–4'),'Livestock Products Technology':('1–2','3–4'),
   'Veterinary and Animal Husbandry Extension Education':('1','2'),
   'Veterinary Surgery and Radiology':('1–4','5–6'),'Veterinary Medicine':('1–3','4–5'),
   'Veterinary Gynaecology and Obstetrics':('1','2–3')}
  if name in coverage:
   table=text.index('ANNUAL EXAMINATION',match.start())
   assessment=dict(summary='Annual practical: two papers of 60 marks each, each carrying a weightage of 20. Practical assessment is conducted internally.',sourcePage=page_at(sy,table),papers=[dict(title='Practical Paper '+roman,detail='Units '+units+' · 60 marks · weightage 20') for roman,units in zip(['I','II'],coverage[name])])
  else:
   summary='Internally assessed twice a year: after 50% of the syllabus and after the complete syllabus. The second examination covers the full course.'
   detail='Day-to-day farm activities, record book, written objective questions and viva.' if name=='Livestock Farm Practices' else 'Clinical records, case presentations, treatment reviews, written objective questions and viva; follow your department’s instructions for your clinical year.'
   assessment=dict(summary=summary,papers=[dict(title='What is assessed',detail=detail)],sourcePage=40)
  result[-1]['assessment']=assessment
  print(year,name,len(units),sum(len(u['topics']) for u in units))
data=dict(reviewed='2026-10-28',authority='Veterinary Council of India — MSVE Regulations 2016, course contents published in The Gazette of India',basis='Full DUVASU-hosted VCI MSVE 2016 curriculum',source=source['url'],sourceSha256=source['sha256'],sourcePageCount=source['pageCount'],subjects=result)
(ROOT/'data/subject-syllabi.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
