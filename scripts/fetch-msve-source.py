#!/usr/bin/env python3
"""Retrieve the exact university-hosted curriculum supplied by the site owner."""
from pathlib import Path
from urllib.request import Request,urlopen
import hashlib,json,subprocess,tempfile,re,datetime
ROOT=Path(__file__).resolve().parent.parent
URL='https://upvetuniv.edu.in/wp-content/uploads/2020/12/BVSc-AH-Syllabus-and-Course-curriculum-MSVE-2016.pdf'
with urlopen(Request(URL,headers={'User-Agent':'Mozilla/5.0'}),timeout=60) as response:raw=response.read(32*1024*1024)
assert raw.startswith(b'%PDF-'),'University URL did not return a PDF'
with tempfile.TemporaryDirectory() as tmp:
    pdf=Path(tmp)/'msve.pdf';pdf.write_bytes(raw)
    text=subprocess.run(['pdftotext','-layout',str(pdf),'-'],capture_output=True,text=True,check=True).stdout
pages=text.split('\f');pages=pages[:-1] if not pages[-1].strip() else pages
selected=[]
for i,page in enumerate(pages):
    # Full English assessment rules and department-wise course contents.
    if i>=80 or any(term in page for term in ['Examination and Evaluation','EXAMINATION AND EVALUATION']):selected.append(dict(page=i+1,text=page))
assert any('DEPARTMENT OF VETERINARY ANATOMY' in p['text'] for p in selected),'Course contents missing'
assert any('VETERINARY GYNAECOLOGY AND OBSTETRICS' in p['text'] for p in selected),'Course contents incomplete'
data=dict(url=URL,title='BVSc & AH Syllabus and Course Curriculum — MSVE 2016',host='DUVASU, Mathura',reviewed=datetime.date.today().isoformat(),sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),pageCount=len(pages),pages=selected)
(ROOT/'data/msve-2016-source.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
print('MSVE_SOURCE '+json.dumps({k:v for k,v in data.items() if k!='pages'}))
