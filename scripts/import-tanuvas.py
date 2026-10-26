#!/usr/bin/env python3
"""Inspect the TANUVAS collections linked by VetBVSc; store metadata only."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from urllib.parse import urljoin,urlsplit,parse_qs,unquote
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import hashlib,json,re,time,zipfile,io
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parent.parent
SOURCES={1:'https://vetbvsc.in/tanuvas-1st-year-notes/',2:'https://vetbvsc.in/tanuvas-notes-for-second-year/',3:'https://vetbvsc.in/tanuvas-notes-for-3rd-year/',4:'https://vetbvsc.in/4th-year-notes/'}
SUBJECTS={'VAN':(1,'Veterinary Anatomy'),'VPB':(1,'Veterinary Physiology'),'LPM':(1,'Livestock Production Management'),'ANN':(2,'Animal Nutrition'),'VPP':(2,'Veterinary Pathology'),'VMC':(2,'Veterinary Microbiology'),'AGB':(2,'Animal Genetics and Breeding'),'VPT':(3,'Veterinary Pharmacology and Toxicology'),'VPE':(3,'Veterinary Public Health and Epidemiology'),'VPA':(3,'Veterinary Parasitology'),'LPT':(3,'Livestock Products Technology'),'VAE':(3,'Veterinary and Animal Husbandry Extension Education'),'VMD':(4,'Veterinary Medicine'),'VSR':(4,'Veterinary Surgery and Radiology'),'VGO':(4,'Veterinary Gynaecology and Obstetrics')}
HOSTS={'vetbvsc.in','www.vetbvsc.in','himanshuvet.wordpress.com','himanshuvet.files.wordpress.com','drive.google.com','docs.google.com'}

class Links(HTMLParser):
 def __init__(self,html):super().__init__();self.links=[];self.href=None;self.text=[];self.feed(html)
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='a':self.href=a.get('href');self.text=[]
 def handle_data(self,text):
  if self.href:self.text.append(text)
 def handle_endtag(self,tag):
  if tag=='a' and self.href:self.links.append((self.href,re.sub(r'\s+',' ',''.join(self.text)).strip()));self.href=None

def fetch(url,limit=2500000):
 if urlsplit(url).hostname not in HOSTS:raise ValueError('Unreviewed host: '+url)
 for attempt in range(2):
  try:
   with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0 (compatible; NotesThatVetGuy-SourceReview/2)'}),timeout=25) as r:
    return r.url,r.headers.get('Content-Type',''),r.read(limit)
  except Exception:
   if attempt:raise
   time.sleep(1)

def pdf_probe(url):
 try:
  final,mime,raw=fetch(url,2048)
  return {'status':'verified' if b'%PDF-' in raw[:1024] else 'unverified','finalURL':final,'mime':mime,'reason':None if b'%PDF-' in raw[:1024] else 'No PDF signature in response'}
 except Exception as error:return {'status':'unavailable','reason':str(error)}

def document_probe(url):
 if not re.search(r'\.docx(?:$|[?#])',url,re.I):return pdf_probe(url)
 try:
  final,mime,raw=fetch(url,12000000)
  with zipfile.ZipFile(io.BytesIO(raw)) as archive:
   document=ET.fromstring(archive.read('word/document.xml'))
   title=' '.join(n.text or '' for n in document.iter('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t'))[:350]
  return {'status':'verified','finalURL':final,'mime':mime,'documentOpening':title}
 except Exception as error:return {'status':'unavailable','reason':str(error)}

def course(title):
 m=re.search(r'\b(VAN|VPB|LPM|ANN|VPP|VMC|AGB|VPT|VPE|VPA|LPT|VAE|VMD|VSR|VGO)\s*[-–— ]?\s*(\d{3})\b',title,re.I)
 if not m:return None
 prefix,num=m[1].upper(),m[2];year,subject=SUBJECTS[prefix]
 if prefix=='VPB' and num in ['112','122']:year,subject=2,'Veterinary Biochemistry'
 return year,subject,prefix+'-'+num

def resolve(item):
 url,title,year,subject,code,index=item
 try:
  # Direct PDFs and Drive viewer links are resources, not intermediate pages.
  candidates=[(url,title)] if re.search(r'\.(pdf|docx)(?:$|[?#])',url,re.I) or urlsplit(url).hostname in ['drive.google.com','docs.google.com'] else []
  if not candidates:
   final,mime,raw=fetch(url)
   if 'pdf' in mime or raw.startswith(b'%PDF-'):candidates=[(final,title)]
   else:
    for href,text in Links(raw.decode('utf-8','replace')).links:
     target=urljoin(final,href);host=urlsplit(target).hostname
     if host in HOSTS and (re.search(r'\.(pdf|docx)(?:$|[?#])',target,re.I) or host in ['drive.google.com','docs.google.com']):candidates.append((target,text or title))
  rows=[];problems=[];seen=set()
  for target,label in candidates:
   if target in seen:continue
   seen.add(target);host=urlsplit(target).hostname
   if host in ['drive.google.com','docs.google.com']:
    m=re.search(r'/d/([\w-]+)',target);fid=m[1] if m else parse_qs(urlsplit(target).query).get('id',[None])[0]
    if not fid:continue
    verification={'status':'source-listed','reason':'Drive viewer linked by collection; file bytes not verified'}
   else:
    verification=document_probe(target)
    if verification['status']!='verified':problems.append({'url':target,'course':code,**verification});continue
    fid='tanuvas-'+hashlib.sha256(target.encode()).hexdigest()[:18]
   display=title if len(candidates)==1 else code+' · '+(label if label.lower() not in ['download','download pdf','click here','here'] else unquote(urlsplit(target).path.rsplit('/',1)[-1]))
   # The linked Word file contains entomology, despite the source landing label.
   if target.endswith('/vpa-211-entomology.docx'):
    display='Veterinary Entomology (TANUVAS)'
    title='VPA-211 Veterinary Entomology'
    problems.append({'url':target,'status':'corrected-source-label','course':code,'reason':'DOCX opens with Arthropoda/Insecta; display corrected to Veterinary Entomology'})
   rows.append({'id':fid,'year':year,'subject':subject,'unit':code+' · '+re.sub(r'^.*?\b'+re.escape(code.split('-')[1])+r'\b\s*','',title).strip(' -–—'),'name':display,'title':re.sub(r'\.(pdf|docx)$','',display,flags=re.I),'url':target,'sourcePage':url,'sourceIndex':index,'sourceLabel':'VetBVSc TANUVAS collection','sourceCredit':'TANUVAS · listed by VetBVSc','collection':'TANUVAS','format':'DOCX' if re.search(r'\.docx(?:$|[?#])',target,re.I) else 'PDF','courseCode':code,'verification':verification,'alsoListedAt':[]})
  return rows,problems,{'url':url,'course':code,'resources':len(rows),'candidates':len(candidates)}
 except Exception as error:return [],[{'url':url,'course':code,'status':'unavailable','reason':str(error)}],{'url':url,'course':code,'resources':0}

def run():
 jobs=[];indexes=[];problems=[];seen=set()
 for year,url in SOURCES.items():
  try:
   final,mime,raw=fetch(url);links=Links(raw.decode('utf-8','replace')).links;found=0
   # Inspect a fourth-year TANUVAS landing destination if it exists.
   if year==4:
    alternatives=[urljoin(final,h) for h,t in links if 'tanuvas' in t.lower() and urljoin(final,h)!=final]
    if alternatives:
     final,mime,raw=fetch(alternatives[0]);links=Links(raw.decode('utf-8','replace')).links
   for href,title in links:
    target=urljoin(final,href);info=course(title)
    if not info and 'veterinary physiology book by tanuvas' in title.lower():info=(1,'Veterinary Physiology','VPB-reference')
    if not info or urlsplit(target).hostname not in HOSTS:continue
    yr,subject,code=info
    if (code,target) in seen:continue
    seen.add((code,target));jobs.append((target,title,yr,subject,code,final));found+=1
   indexes.append({'url':final,'year':year,'courses':found})
   if not found:problems.append({'url':final,'year':year,'status':'no-resources','reason':'No linked TANUVAS courses on this collection page'})
  except Exception as error:problems.append({'url':url,'year':year,'status':'unavailable','reason':str(error)})
 rows=[];pages=[]
 with ThreadPoolExecutor(max_workers=5) as pool:
  for found,errors,page in pool.map(resolve,jobs):rows+=found;problems+=errors;pages.append(page)
 unique={}
 for r in rows:
  if r['id'] in unique:
   unique[r['id']]['alsoListedAt'].append({'page':r['sourcePage'],'unit':r['unit'],'subject':r['subject'],'year':r['year']})
   if unique[r['id']]['subject']!=r['subject']:problems.append({'url':r['url'],'status':'conflicting-source-label','course':r['courseCode'],'reason':'Same file is labelled for different subjects; retained once under '+unique[r['id']]['subject']})
  else:unique[r['id']]=r
 data={'schemaVersion':1,'reviewed':datetime.now(timezone.utc).date().isoformat(),'sourceIndexes':indexes,'coursePages':pages,'notes':list(unique.values()),'unavailable':problems,'stats':{'resources':len(unique),'byYear':{str(y):sum(r['year']==y for r in unique.values()) for y in range(1,5)},'duplicatesMerged':len(rows)-len(unique),'unavailable':len(problems)}}
 if not unique:raise ValueError('No TANUVAS resources verified; keep the previous reviewed snapshot')
 (ROOT/'data/tanuvas-source.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
 print('TANUVAS_REVIEW '+json.dumps(data,ensure_ascii=False))
if __name__=='__main__':run()
