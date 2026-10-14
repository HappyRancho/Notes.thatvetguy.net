"""Static preset search uses the same filename/path/subject fields as client search."""
import re,unicodedata
from library import natural
def normal(s):return re.sub(r'[^a-z0-9 ]',' ',unicodedata.normalize('NFKD',s).encode('ascii','ignore').decode().lower())
def find_preset(query,records):
 words=normal(query).split()
 return sorted([r for r in records if all(w in normal(' '.join(str(r.get(k,'')) for k in ['title','subject','type','path','group','keywords'])) for w in words)],key=lambda r:natural(r['title']))
