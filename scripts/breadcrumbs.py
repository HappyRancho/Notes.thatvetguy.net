"""One route hierarchy for visible navigation and BreadcrumbList data."""
import re
from html import escape
LABELS={'/bvsc/':'BVSc','/books/':'Books','/study-tools/':'Tools & Tips','/search/':'Search','/objective/':'Objective Resources','/about/':'About','/request-resource/':'Request a Resource','/404/':'Page not found','/clinical/drug-index/':'Drug Index','/clinical/handbooks/':'Handbooks'}
def trail(path,title,pages=None):
 pages=pages or {}
 rows=[('Home','/')]
 parts=path.strip('/').split('/')
 if parts[0]=='clinical':rows.append(('Clinical Resources','/#clinical'))
 else:
  for n in range(1,len(parts)):
   parent='/'+'/'.join(parts[:n])+'/'
   name=LABELS.get(parent) or pages.get(parent,{}).get('title')
   year=re.fullmatch(r'/bvsc/year-([1-4])/',parent)
   if year:name={'1':'1st','2':'2nd','3':'3rd','4':'4th'}[year[1]]+' Year'
   if name:rows.append((name,parent))
 current=LABELS.get(path,title)
 if re.fullmatch(r'/bvsc/year-[1-4]/',path):current={'1':'1st','2':'2nd','3':'3rd','4':'4th'}[parts[1][-1]]+' Year'
 elif parts[-1]=='syllabus':current='Syllabus Checklist'
 elif parts[-1]=='practicals':current='Practical Vault'
 elif parts[-1]=='roadmap':current='Year Roadmap'
 elif parts[-1]=='notes':current='Topic-wise Notes'
 rows.append((current,path))
 return rows

def render(rows):
 items=[]
 for i,(name,url) in enumerate(rows):
  label=escape(name)
  item='<span aria-current="page">'+label+'</span>' if i==len(rows)-1 else '<a href="'+escape(url,quote=True)+'">'+label+'</a>'
  items.append('<li>'+('<span class="crumb-separator" aria-hidden="true">›</span>' if i else '')+item+'</li>')
 return '<nav class="breadcrumbs" aria-label="Breadcrumb"><ol>'+''.join(items)+'</ol></nav>'
