"""Links into the original, unmodified professional-year outline PDFs."""
import json
from pathlib import Path
DATA=json.loads((Path(__file__).resolve().parent.parent/'data/course-outlines.json').read_text())
def outline_url(year,subject=None):
    entry=DATA['subjects'].get(str(year),{}).get(subject) if subject else None
    pdf=DATA['years'][str(entry['pdfYear'] if entry else year)]
    return pdf['url']+('#page='+str(entry['page']) if entry else '')
