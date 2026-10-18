#!/usr/bin/env python3
"""Record public source-page links with explicit year/subject/unit provenance.

This imports link metadata, never the PDFs or source-page prose. Run explicitly;
a normal site build consumes the reviewed JSON and does not crawl the network.
"""
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlsplit,urljoin,parse_qs
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import json,re,time
from bs4 import BeautifulSoup
ROOT=Path(__file__).resolve().parent.parent
SOURCES={1:'https://vetbvsc.in/bvsc-notes/',2:'https://vetbvsc.in/bvsc-ah-2nd-year/',3:'https://vetbvsc.in/bvsc-ah-3rd-year/',4:'https://vetbvsc.in/bvsc-ah-4th-year-notes/'}
COURSES={1:'https://vetbvsc.in/tanuvas-1st-year-notes/',2:'https://vetbvsc.in/tanuvas-notes-for-second-year/'}
SUBJECTS=json.loads((ROOT/'data/subject-map.json').read_text())['years']
ALIASES={
'Veterinary Anatomy':['vet anatomy','veterinary anatomy'],
'Veterinary Physiology':['vet physiology','veterinary physiology'],
'Livestock Production Management':['livestock production management','livestock production and management'],
'Veterinary Microbiology':['veterinary microbiology','vet microbiology'],
'Veterinary Pathology':['veterinary pathology','vet pathology'],
'Veterinary Biochemistry':['veterinary biochemistry','vet biochemistry'],
'Animal Nutrition':['animal nutrition'],
'Animal Genetics and Breeding':['animal genetics and breeding'],
'Veterinary Pharmacology and Toxicology':['veterinary pharmacology and toxicology','vet pharmacology and toxicology'],
'Veterinary Parasitology':['veterinary parasitology','vet parasitology','vet parasitology and helminthology'],
'Veterinary Public Health and Epidemiology':['veterinary public health and epidemiology','vet public health and epidemiology'],
'Livestock Products Technology':['livestock products technology','livestock production technology'],
'Veterinary and Animal Husbandry Extension Education':['veterinary and animal husbandry extension education','veterinary and a h extension','department of veterinary a h extension'],
'Veterinary Surgery and Radiology':['veterinary surgery and radiology'],
'Veterinary Medicine':['veterinary medicine'],
'Veterinary Gynaecology and Obstetrics':['veterinary gynaecology and obstetrics','veterinary gynecology and obstetrics'],
'Veterinary Clinical Practices II':['veterinary clinical practices'],
'Veterinary Clinical Practices I':['veterinary clinical practices'],
'Livestock Farm Practices':['livestock farm practices'],
}
def normal(s):return re.sub(r'[^a-z0-9]+',' ',s.lower()).strip()
def subject_heading(text,year):
 text=re.sub(r'^\s*\d+[).]\s*','',text).strip(' :.-');n=normal(text)
 for subject in SUBJECTS[str(year)]:
  if n in ALIASES.get(subject,[normal(subject)]):return subject
 return None

def fetch(url):
 for attempt in range(3):
  try:
   req=Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; NotesThatVetGuySourceReview/1.0)'})
   with urlopen(req,timeout=40) as r:
    html=r.read().decode('utf-8','replace');final=r.url
   soup=BeautifulSoup(html,'html.parser');content=soup.select_one('.entry-content') or soup.select_one('.wp-block-post-content') or soup.find('article') or soup.find('main')
   if content is None:raise ValueError('No article content at '+url)
   return content,final
  except Exception:
   if attempt==2:raise
   time.sleep(attempt+1)

def parse(url,year,subject=None,course=None):
 content,final=fetch(url);rows=[];children=[];unit=course or 'Subject notes'
 for node in content.descendants:
  if not getattr(node,'name',None):continue
  if node.name in ['h1','h2','h3','h4','h5','h6','p','li','strong']:
   texts=node.get_text('\n',strip=True).splitlines()
   for text in texts[:2]:
    if len(text)<130:
     found=subject_heading(text,year)
     if found:subject=found;unit=course or 'Subject notes'
     if re.match(r'^Unit\s+\d',text,re.I):unit=re.sub(r'\s+',' ',text).strip()
     elif re.match(r'^Extra Notes',text,re.I):unit='Additional subject notes'
  if node.name!='a':continue
  href=urljoin(final,node.get('href',''));title=re.sub(r'\s+',' ',node.get_text(' ',strip=True));host=urlsplit(href).hostname or ''
  if host in ['drive.google.com','docs.google.com']:
   match=re.search(r'/d/([\w-]+)',href);fid=match[1] if match else parse_qs(urlsplit(href).query).get('id',[None])[0]
   if not fid:
    match=re.search(r'/folders/([\w-]+)',href);fid=match[1] if match else None
   if not fid:continue
   rows.append({'year':year,'subject':subject,'unit':unit,'id':fid,'name':title,'title':re.sub(r'\s+(?:pdf|pptx?|docx?)\s*$','',title,flags=re.I).strip(),'url':href,'sourcePage':final,'sourceLabel':'VetBVSc','sourceCredit':next((u for u in ['TANUVAS','KVASU','KVAFSU','ICAR','VCI'] if u.lower() in title.lower()),None),'collection':'TANUVAS' if course else 'Unit notes','format':'VIDEO' if re.search(r'\bmp4\b',title,re.I) else 'PDF'})
  elif subject and host in ['vetbvsc.in','www.vetbvsc.in'] and re.match(r'^(VAN|VPB|LPM|ANN|VPP|VMC|AGB)[ -]*\d',title,re.I):
   children.append((href,year,subject,title))
 return rows,children,{'url':final,'year':year,'links':len(rows),'courses':len(children)}

def run():
 allrows=[];pages=[];pending=[]
 for year,url in SOURCES.items():
  rows,children,report=parse(url,year);allrows+=rows;pages.append(report)
  if not rows:raise ValueError('Source has no Drive links: '+url)
 for year,url in COURSES.items():
  rows,children,report=parse(url,year,course='TANUVAS subject notes');allrows+=rows;pages.append(report);pending+=children
 seenpages={p['url'] for p in pages};pending=[p for p in pending if p[0] not in seenpages]
 def load(args):return parse(args[0],args[1],args[2],args[3])
 with ThreadPoolExecutor(max_workers=4) as pool:
  for rows,children,report in pool.map(load,pending):allrows+=rows;pages.append(report)
 rows=[];seen={};excluded=[]
 for r in allrows:
  if not r['subject']:
   excluded.append(r);continue
  if r['id'] in seen:
   seen[r['id']]['alsoListedAt'].append({'page':r['sourcePage'],'unit':r['unit'],'year':r['year'],'subject':r['subject']});continue
  r['alsoListedAt']=[];seen[r['id']]=r;rows.append(r)
 # The books page is research metadata only, not an automatic PDF-book import.
 content,books_page=fetch('https://vetbvsc.in/vet-books/');book_references=[];subject=None
 for node in content.find_all(['h4','h3','li']):
  text=node.get_text(' ',strip=True)
  if node.name in ['h3','h4']:
   subject=text.strip(' :');continue
  if subject and text and len(text)<350:book_references.append({'subjectLabel':subject,'title':text,'sourcePage':books_page})
 date=datetime.now(timezone.utc).date().isoformat()
 data={'schemaVersion':1,'reviewed':date,'entryPage':'https://vetbvsc.in/notes/','sourcePages':pages,'notes':rows,'bookReferences':book_references,'excluded':excluded,'stats':{'resources':len(rows),'years':{str(y):sum(r['year']==y for r in rows) for y in SOURCES},'duplicateLinksMerged':len(allrows)-len(rows)-len(excluded),'unmapped':len(excluded)}}
 dest=ROOT/'data/vetbvsc-source.json';dest.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(json.dumps(data['stats']));print('SOURCES',json.dumps(pages));print('UNMAPPED',json.dumps(excluded[:20]))
 if excluded:raise ValueError('Source links need explicit subject mapping; inspect data/vetbvsc-source.json')
if __name__=='__main__':run()
