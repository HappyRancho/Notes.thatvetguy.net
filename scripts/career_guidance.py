"""Progressively disclosed career guidance; facts and community reports stay distinct."""
import json
from pathlib import Path
from html import escape as e
DATA=json.loads((Path(__file__).resolve().parent.parent/'data/career-guidance.json').read_text())

def drawer(b,title,lead,body,ident=''):
 return '<details class="career-guide-drawer"'+(' id="'+ident+'"' if ident else '')+'><summary><span><strong>'+title+'</strong><small>'+lead+'</small></span>'+b.icon('chevron')+'</summary><div class="career-guide-body">'+body+'</div></details>'
def paras(rows):
 return ''.join('<p><strong>'+label+'</strong> '+copy+'</p>' for label,copy in rows)
def refs(b,items):
 return '<nav class="career-inline-sources" aria-label="Sources for this guidance">'+''.join(b.link('#source-'+sid,label) for sid,label in items)+'</nav>'
def panel(b,ident,title,lead,body):
 return '<section class="tool-section career-panel" id="'+ident+'" data-career-panel><header class="career-panel-heading"><h2>'+title+'</h2><p>'+lead+'</p></header>'+body+'</section>'
def route_depth(b,ident):
 d=DATA['routes'][ident]
 return drawer(b,'Skills, progression & questions','Look beyond the job title.',paras([('Build these skills.',e(d['skills'])),('Where it can lead.',e(d['progression'])),('Ask before committing.',e(d['questions']))]))
def panels(b):
 study=drawer(b,'Work first or study further?','Choose the training for the work you want.',paras([
 ('Start with a supervised job if…','you need income, want to test a work setting or need clinical confidence. Compare the mentor and induction plan, not just the hospital name. A job can clarify a later postgraduate choice; keep an eye on admission cycles.'),
 ('Consider MVSc if…','a discipline genuinely interests you or the roles you want require relevant postgraduate training. Clinical subjects, diagnostics, production and public health lead to different daily work. An MVSc is not a guarantee of a faculty post or a recognised specialist title.'),
 ('Consider a PhD if…','you enjoy forming questions, analysing evidence and writing—not only learning facts. Check the actual research or teaching posts you hope to pursue, then assess the supervisor, project, funding and facilities.'),
 ('MPH, management or data training?','Start from vacancies that accept your qualification. Public-health, business and technology courses vary in eligibility and outcomes. Ask whether the course teaches a missing skill; an additional degree alone does not qualify you for every related job.')]))
 study+=drawer(b,'Which postgraduate discipline fits?','Match the work, then investigate the department.',paras([
 ('Patients & procedures','Explore medicine, surgery, gynaecology or other relevant clinical disciplines. Ask about supervised caseload, procedures, referral work and how responsibilities increase.'),
 ('Samples & mechanisms','Explore pathology, microbiology, parasitology, pharmacology or related research areas. Look for functioning equipment, biosafety, sample access and training in interpreting results.'),
 ('Herds, food & populations','Explore nutrition, genetics, production, livestock products, epidemiology or public health. Check the field projects, datasets, industry links and the work graduates actually enter.'),
 ('Foundations & teaching','Anatomy, physiology and biochemistry can lead towards teaching and research. Ask what methods you will learn and check current appointment requirements before assuming a teaching route.')]))
 study+=drawer(b,'Admissions: follow the right route','An exam application and a college application can be separate.',
 '<ol><li><strong>Pick the programme and institution.</strong> Read its current prospectus, recognised qualifications, subject eligibility and registration or internship requirements.</li><li><strong>Identify the exact selection route.</strong> Check whether the applicable veterinary seats use an ICAR-linked process, a university examination or another route. Do not assume one exam covers every MVSc seat.</li><li><strong>Track every stage.</strong> Examination, institutional application, counselling, document verification and fee deadlines may be separate.</li><li><strong>Prepare the documents early.</strong> Check degree/provisional certificates, transcripts, internship completion, registration and category documents against the current notice.</li></ol>'+refs(b,[('pg-nta','NTA: current ICAR notices'),('ivri','IVRI: MVSc information'),('pg-tanuvas','TANUVAS: PG admissions')]))
 study+=drawer(b,'Before accepting a seat','Talk to current students as well as the department.',paras([
 ('Learning quality','Who supervises you? How often do you meet? Is the promised clinical exposure or laboratory facility actually available to students?'),
 ('Money & time','Get written information on fees, stipend availability, accommodation, bonds and conditions. Include living costs and income you would forgo; do not budget from an old social-media post.'),
 ('Outcomes','Ask what recent graduates do and how the programme helped them get there. Speak to more than one student; one excellent or unhappy experience is not the whole department.'),
 ('A useful final question','If this degree did not bring an immediate job offer, would the training still move you towards work you want to do?')] ))
 out=panel(b,'pg-or-practice','Further study, with a purpose','Job, MVSc or another degree? Start with the work you want to learn.',study)
 countries=[
 ('United Kingdom','RCVS recognition → registration','uk',[
 ('1 · Check recognition','Use the RCVS guidance for your exact primary qualification. Do not assume that an Indian BVSc or a UK master’s automatically permits clinical practice.'),
 ('2 · Follow the applicable route','If your qualification is not recognised, check eligibility for the statutory membership examination, including documents, English requirements and the current written and clinical assessment process.'),
 ('3 · Plan beyond the exam','Complete the applicable registration requirements, then separately check immigration permission and employment. Ask a prospective employer about induction and support.')],'rcvs','RCVS: recognition and statutory exam'),
 ('United States','Equivalency + NAVLE + state requirements','us',[
 ('1 · Choose a jurisdiction','Check the state licensing board before paying for an equivalency pathway. Acceptance of ECFVG or PAVE and additional requirements must be verified for that jurisdiction.'),
 ('2 · Map the assessments','Graduates of non-accredited schools may need an educational equivalency pathway. Check the applicable BCSE or QSE milestone for NAVLE eligibility, plus the remaining clinical and credential requirements.'),
 ('3 · Finish the licensing route','Passing NAVLE alone is not a licence. Check the state’s application, remaining examinations or documentation, and immigration/work authorisation separately.')],'icva','ICVA: NAVLE application and eligibility'),
 ('Canada','NEB certification → provincial registration','canada',[
 ('1 · Start with the NEB','Check how your qualification is assessed and which examinations or recognised equivalencies apply. The Canadian process should not be treated as identical to a US state licence.'),
 ('2 · Understand the sequence','For the applicable non-accredited-graduate pathway, review BCSE, NAVLE and the clinical assessment requirements, including PSA/CPE where required. Use the current NEB rules for ordering and eligibility.'),
 ('3 · Check the province','The NEB Certificate of Qualification and registration with the intended provincial regulator are distinct stages. Language, local registration and immigration requirements also need checking.')],'canada-neb','CVMA/NEB: examinations and certification'),
 ('Australia & New Zealand','Recognised qualification or AVE route','anz',[
 ('1 · Check your qualification','Use AVBC’s recognition guidance. If your qualification is not recognised, establish eligibility for the Australasian Veterinary Examination before planning a move.'),
 ('2 · Read the current handbook','Check the preliminary and clinical examination pathway, language and document requirements, available sittings and applicable fees. Budget for the route you actually need.'),
 ('3 · Register where you will work','Examination success and registration are separate. Check the relevant Australian state or territory board, or the Veterinary Council of New Zealand, plus immigration and employment requirements.')],'avbc','AVBC: Australasian Veterinary Examination')]
 abroad='<p class="career-key-note"><strong>A master’s abroad is not a clinical licence.</strong> Research, study, registration, employment and visas each have their own rules.</p>'
 for title,lead,ident,rows,sid,label in countries:
  abroad+=drawer(b,title,lead,paras(rows)+refs(b,[(sid,label)]),'country-'+ident)
 abroad+=drawer(b,'Can I afford the route?','Build a budget before choosing a country.',paras([
 ('Price the full journey','List credential verification, language tests, each assessment, preparation, clinical placements where required, travel, accommodation, registration and visa costs using current official figures.'),
 ('Plan for delays','Include living costs, limited earning opportunities while preparing and a retake contingency. A friend’s timeline or an agent’s promise is not a regulator’s guarantee.'),
 ('Keep a second option','Decide what you will do while waiting: supervised work, relevant research or another realistic local role. Set a spending limit and a date to review progress.'),
 ('Verify before paying','Use the regulator’s current handbook and fee schedule. Check any course or agent’s claims directly; no preparation provider can guarantee a licence or job.')]))
 out+=panel(b,'overseas','Work abroad: know the route','Choose a destination to see the steps and what needs checking.',abroad)
 decide='<span id="next-30-days" class="anchor-alias"></span><p class="career-key-note"><strong>Choose the next useful step, not your whole life.</strong> Compare two realistic opportunities and find out what is still unknown.</p>'
 decide+=drawer(b,'1. Set your non-negotiables','Location, finances, hours and support.',paras([
 ('What must be true?','Write down your minimum income needs, acceptable locations, family responsibilities and how long you can fund study or exam preparation. Separate a requirement from a preference.'),
 ('Which working day suits you?','Think about consultations, procedures, farm travel, laboratory work, data, writing or teaching. Consider nights, emergencies and public-facing work—not only your favourite subject.'),
 ('What support do you need now?','A first role should match your competence. Identify the supervision, equipment and escalation support needed to work safely; a prestigious title does not replace them.')]))
 decide+=drawer(b,'2. Compare opportunities, not stereotypes','“Government” or “private” is not a job description.',paras([
 ('Use the same questions','For each option record daily work, eligibility, actual location, take-home pay, duty hours, mentorship and the next learning opportunity. Mark unknown answers as unknown rather than scoring them optimistically.'),
 ('Read the written terms','Check allowances, accommodation, probation, notice, bond conditions and contract duration. Government vacancies also have specific posting and selection rules; do not assume a post will open when you need it.'),
 ('Choose your trade-off','Decide what matters most right now. A better mentor may outweigh a modest pay difference; family location may outweigh a preferred sector. There is no universal best order.'),
 ('Ask about a normal week','Speak to a recent graduate and someone established in the exact kind of role. Ask what takes most of their time, what is difficult and what they wish they had checked before joining.')]))
 decide+=drawer(b,'3. Try a small version of the work','Replace guessing with an experience you can reflect on.',paras([
 ('Arrange a safe trial','Through your college, request an approved observation visit, supervised placement or small project. Do not independently perform clinical work beyond your training or registration.'),
 ('Notice what energises you','After the experience, record what you enjoyed, what drained you, what you could improve with practice and which conditions would need to change.'),
 ('Make one reversible commitment','Apply for a suitable role, visit a department, learn one relevant method or start a defined exam-preparation block. Set a review date and decide what evidence would make you change direction.')]))
 decide+=drawer(b,'4. Interview the employer or supervisor','Five answers worth getting before you say yes.',
 '<ul><li><strong>Mentorship:</strong> Who is the named supervisor, when do we work together and who covers their absence?</li><li><strong>Workload:</strong> What are the actual rota, emergency duties, travel and time-off arrangements?</li><li><strong>Responsibility:</strong> Which decisions can I make, which need review, and how do referrals or escalation work?</li><li><strong>Learning:</strong> Is there protected feedback time, training, equipment and access to the cases or methods promised?</li><li><strong>Terms:</strong> Can I see pay, deductions, contract length, notice and any bond in writing?</li></ul>')
 community='<p class="community-context">These are individual Reddit experiences, not verified employment statistics or eligibility guidance. We use them to identify questions worth asking; salary claims are not treated as evidence.</p>'
 for c in DATA['community']:
  community+=drawer(b,e(c['title']),e(c['context']),paras([('What the discussion raised.',e(c['observation'])),('Our practical takeaway.',e(c['action']))])+b.link(c['url'],'Read the original discussion','community-source'))
 decide+=drawer(b,'What real-world discussions can teach us','Three experiences, translated into better questions.',community)
 out+=panel(b,'how-to-decide','How to decide','Find a direction that fits your life—and test it before committing.',decide)
 return out
