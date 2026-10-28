"""Progressive, source-credited unit-wise checklists; no invented course units."""
from pathlib import Path
from html import escape as e
import json
from library import slug
ROOT=Path(__file__).resolve().parent.parent
DATA=json.loads((ROOT/'data/subject-syllabi.json').read_text())
def checklist_url(year,subject):return f'/bvsc/year-{year}/'+slug(subject)+'/syllabus/'
def topic_row(b,topic):
    context=('<small>'+e(topic['context'])+'</small>') if topic.get('context') else ''
    return '<li><label class="syllabus-topic"><input type="checkbox" id="topic-'+topic['id']+'" data-topic="'+topic['id']+'"><span class="syllabus-tick" aria-hidden="true">'+b.icon('check')+'</span><span>'+context+e(topic['text'])+'</span></label></li>'
def topic_list(b,topics):
    body='<ul class="syllabus-topics">'+''.join(topic_row(b,t) for t in topics[:30])+'</ul>'
    if len(topics)>30:body+='<details class="syllabus-topic-batch"><summary>Show '+str(min(30,len(topics)-30))+' more topics '+b.icon('chevron')+'</summary>'+topic_list(b,topics[30:])+'</details>'
    return body
def render(b):
    for subject in DATA['subjects']:
        name=subject['subject'];year=subject['year'];label=b.DATA['labels'][str(year)];parent=f'/bvsc/year-{year}/'+subject['slug']+'/';path=checklist_url(year,name)
        desc=f'{name} syllabus checklist for {label} BVSc & AH. Track theory and practical topics unit by unit against the published course outline.'
        body=b.article_intro(name+' Syllabus Checklist',f'Your {label} course outline, one topic at a time. Tick what you have covered and pick up where you left off.',[('BVSc','/bvsc/'),(label,f'/bvsc/year-{year}/'),(name,parent)]).replace('container reading-page','container reading-page syllabus-page',1)
        body+='<div data-syllabus="'+subject['slug']+'" data-syllabus-count="'+str(subject['totalTopics'])+'"><aside class="syllabus-progress" aria-label="Checklist progress"><div><strong data-syllabus-status>0 of '+str(subject['totalTopics'])+' topics checked</strong><span data-syllabus-percent>0%</span></div><progress max="'+str(subject['totalTopics'])+'" value="0" aria-label="Completed syllabus topics"></progress><p class="js-only" data-syllabus-storage>Your progress stays on this device.</p><noscript><p>You can tick topics here. Enable JavaScript to save progress between visits.</p></noscript><span class="sr-only" role="status" data-syllabus-announcement></span></aside>'
        body+='<nav class="syllabus-jump" aria-label="Checklist sections">'+''.join(b.link('#'+kind,b.icon('paper' if kind=='theory' else 'flask')+title) for kind,title in [('theory','Theory'),('practical','Practical')] if any(u['kind']==kind for u in subject['units']))+'</nav>'
        for kind,title in [('theory','Theory'),('practical','Practical')]:
            units=[u for u in subject['units'] if u['kind']==kind]
            if not units:continue
            body+='<section class="syllabus-section syllabus-'+kind+'" id="'+kind+'"><header><span class="rx-row-icon '+('sky' if kind=='theory' else 'peach')+'">'+b.icon('paper' if kind=='theory' else 'flask')+'</span><h2>'+title+'</h2></header>'
            if subject['unitNumbering']=='sections':body+='<p class="syllabus-section-note">The outline uses practical sections rather than numbered units.</p>'
            for i,unit in enumerate(units):
                prefix='<small>Unit '+str(unit['number'])+'</small>' if unit['number'] is not None else ''
                body+='<details class="syllabus-unit" id="'+unit['key']+'" data-syllabus-unit'+(' open' if i==0 else '')+'><summary><h3>'+prefix+e(unit['title'])+'</h3><span class="syllabus-unit-count" data-unit-count>0 / '+str(len(unit['topics']))+'</span>'+b.icon('chevron')+'</summary>'+topic_list(b,unit['topics'])+'</details>'
            body+='</section>'
        body+='</div><details class="syllabus-source"><summary>Course outline &amp; source notes '+b.icon('chevron')+'</summary><p>'+e(DATA['authority'])+'. Topics follow the VCI MSVE 2016 course contents in the DUVASU-hosted curriculum. Your university’s current syllabus and teaching instructions take precedence.</p>'
        body+=b.link(subject['sourceUrl']+'#page='+str(subject['sourcePage']),'Read the MSVE 2016 curriculum (PDF) '+b.icon('paper'),'syllabus-source-link')+'<p>Checked <time datetime="'+DATA['reviewed']+'">'+DATA['reviewed']+'</time>.</p></details>'+b.link(parent,'Back to '+e(name)+' '+b.icon('arrow'),'syllabus-back')+'</div>'
        b.write_page(path,name+' Syllabus Checklist — '+label+' BVSc & AH',desc,body)
