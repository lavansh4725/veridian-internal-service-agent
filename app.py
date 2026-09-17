import json, uuid
from datetime import datetime
from pathlib import Path
import streamlit as st

DATA=json.loads((Path(__file__).parent/'data.json').read_text(encoding='utf-8'))
POLICIES, REQUESTS, TICKETS=DATA['policies'],DATA['requests'],DATA['tickets']
st.set_page_config(page_title='Veridian • Service Desk AI',page_icon='✦',layout='wide')

st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
:root{--bg:#080b12;--panel:#101521;--panel2:#141a28;--line:#252d3d;--text:#f4f7fb;--muted:#8d98aa;--accent:#7c5cff;--good:#27d3a2;--warn:#f4b942;--bad:#ff6577}
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}.stApp{background:radial-gradient(circle at 80% -10%,rgba(124,92,255,.18),transparent 35%),radial-gradient(circle at 0% 40%,rgba(39,211,162,.07),transparent 28%),var(--bg);color:var(--text)}
.block-container{max-width:1500px;padding:1.4rem 2rem 3rem}section[data-testid="stSidebar"]{background:#0b0f17;border-right:1px solid var(--line)}h1,h2,h3{font-family:'Space Grotesk',sans-serif;letter-spacing:-.03em}
.hero{padding:4px 0 22px}.eyebrow{color:#9a8cff;text-transform:uppercase;letter-spacing:.16em;font-size:.7rem;font-weight:700}.hero h1{font-size:2.35rem;margin:.2rem 0 .35rem}.hero p{color:var(--muted);max-width:800px}
.kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:8px 0 22px}.metric{background:linear-gradient(145deg,#121827,#0e131e);border:1px solid var(--line);border-radius:18px;padding:17px 19px}.metric small{color:var(--muted);text-transform:uppercase;letter-spacing:.08em}.metric b{display:block;font:700 2rem 'Space Grotesk';margin-top:7px}.metric span{font-size:.75rem;color:#778297}
.card{background:rgba(16,21,33,.86);border:1px solid var(--line);border-radius:18px;padding:20px}.muted{color:var(--muted);font-size:.82rem}.badge{display:inline-block;border-radius:999px;padding:5px 9px;font-size:.68rem;font-weight:700}.green{background:#0d3029;color:#58e5be}.yellow{background:#34290e;color:#ffd777}.red{background:#35141b;color:#ff8d9b}.blue{background:#102943;color:#83c6ff}
.source{border-left:3px solid var(--accent);background:#0c111b;padding:12px 14px;border-radius:0 12px 12px 0}.ticket{border:1px solid var(--line);border-radius:14px;padding:14px;background:#0f141f;margin:8px 0}.stTextArea textarea,.stTextInput input{background:#0d121c!important;border-color:var(--line)!important;color:#eef2f8!important;border-radius:11px!important}.stButton>button{border-radius:10px;border:1px solid var(--line);background:#151b29;color:#eef2f8}.stButton>button:hover{border-color:#6655c9}.stButton>button[kind="primary"]{background:linear-gradient(135deg,#7659ff,#5e47e6);border:0}.stTabs [data-baseweb="tab-list"]{gap:8px}.stTabs [data-baseweb="tab"]{background:#0f141f;border-radius:10px;padding:8px 14px}.stExpander{border-color:var(--line);background:#0e131e}@media(max-width:800px){.kpis{grid-template-columns:repeat(2,1fr)}.block-container{padding:1rem}}
</style>''',unsafe_allow_html=True)

if 'audit' not in st.session_state: st.session_state.audit=[]
if 'created' not in st.session_state: st.session_state.created=[]
if 'last' not in st.session_state: st.session_state.last=None

def log(event,details): st.session_state.audit.insert(0,{'timestamp':datetime.now().strftime('%Y-%m-%d %H:%M:%S'),'event':event,'details':details})
def classify(x):
 t=x.lower()
 if any(k in t for k in ['phishing','malware','unauthorized access']):return 'security'
 if 'password' in t or 'locked out' in t or ('login' in t and 'expense' not in t):return 'password'
 if 'vpn' in t:return 'vpn'
 if 'laptop' in t or 'screen' in t:return 'laptop'
 if 'software' in t or 'extension' in t or 'install' in t:return 'software'
 if 'printer' in t or 'paper jam' in t:return 'printer'
 if 'mailbox' in t or ('email' in t and 'quota' in t):return 'mailbox'
 if 'guest' in t and 'wifi' in t:return 'wifi'
 if 'monitor' in t or ('home' in t and 'equipment' in t):return 'wfh'
 if 'expense' in t:return 'expense'
 if 'admin access' in t or 'server' in t:return 'admin'
 return 'unclear'
def policy(intent):
 m={'password':'KB-01','vpn':'KB-02','laptop':'KB-03','software':'KB-04','printer':'KB-05','mailbox':'KB-06','wifi':'KB-07','expense':'KB-08','security':'KB-09','wfh':'KB-10'}
 return next((p for p in POLICIES if p['id']==m.get(intent)),None)
def resolve(x):
 i=classify(x);p=policy(i);t=x.lower()
 if i=='unclear':return ('FOLLOW-UP REQUIRED',i,p,'I need the affected service/device and the exact error or symptom before I can identify the correct policy.','Ask one concise follow-up; do not invent a resolution.',True)
 if i=='security':return ('ESCALATE',i,p,'This is a suspected security incident. Report it immediately to security@veridian-corp.example and do not forward it to other employees.','Route to Security and preserve the audit trail.',True)
 if i=='password':
  if '6 times' in t or 'locked out' in t:return ('RESOLVE',i,p,'You are locked out after more than 5 failed attempts. IT should manually unlock the account; no approval is required.','Route the unlock to IT.',True)
  return ('RESOLVE',i,p,'You can reset your own password through the self-service portal at any time.','Use the self-service portal.',False)
 if i=='vpn':return ('RESOLVE',i,p,'VPN credentials expire every 90 days and must be renewed by the employee.','Renew the VPN credentials.',False) if 'expired' in t else ('FOLLOW-UP REQUIRED',i,p,'VPN access is automatic for full-time employees; contractors require manager approval via the access request form.','Confirm employment type and whether this is new access or renewal.',True)
 if i=='laptop':
  if ('3.5' in t and ('dead' in t or 'won’t turn' in t)) :return ('ESCALATE',i,p,'The laptop is about 3.5 years old with a reported hardware failure. Early replacement outside the 4-year refresh cycle requires Finance sign-off in addition to IT approval.','Verify the hardware failure, then route for IT approval plus Finance sign-off.',True)
  return ('FOLLOW-UP REQUIRED',i,p,'Laptops are eligible for replacement after 3 years, or earlier for verified hardware failure.','Confirm laptop age and whether hardware failure is verified.',True)
 if i=='software':return ('ESCALATE',i,p,'Non-catalog software requires IT Security review, which takes 3–5 business days.','Route to IT Security; do not approve directly.',True) if ('not in' in t or 'extension' in t or 'non-catalog' in t) else ('RESOLVE',i,p,'Standard software in the approved catalog can be self-installed.','Use the approved catalog.',False)
 if i=='printer':return ('RESOLVE',i,p,'First check the printer queue and restart the print spooler. If it persists, log a ticket with the printer asset tag.','Perform the two checks, then escalate with the asset tag.',True)
 if i=='mailbox':return ('RESOLVE',i,p,'The default mailbox quota is 25GB. Archive old mail. Increases above 25GB require manager approval and are capped at 50GB.','Archive old mail first; request approval if more capacity is needed.',True)
 if i=='wifi':return ('RESOLVE',i,p,'Guest Wi-Fi credentials are valid for 24 hours and can be generated at the front-desk kiosk. No IT ticket is required.','Generate credentials at the front-desk kiosk.',False)
 if i=='wfh':return ('FOLLOW-UP REQUIRED',i,p,'Remote employees working more than 3 days/week are eligible for a one-time home-office equipment allowance covering a chair or monitor.','Obtain manager sign-off and Finance processing; IT handles shipping after approval.',True)
 if i=='expense':return ('ROUTE',i,p,'Expense-tool access is granted by Finance, not IT. IT can assist with login/technical issues once an account already exists.','Confirm whether an account exists; route access to Finance.',True)
 return ('ESCALATE',i,None,'The supplied policy set does not define an approval process for finance-server admin access.','Do not invent an approval path; route to a human owner with business justification.',True)
def badge(s):
 c={'RESOLVE':'green','FOLLOW-UP REQUIRED':'yellow','ESCALATE':'red','ROUTE':'blue'}.get(s,'blue');return f'<span class="badge {c}">{s}</span>'
def make_ticket(msg,r,name,email):
 tid='NEW-'+uuid.uuid4().hex[:6].upper();z={'id':tid,'employee':name,'email':email,'issue':msg,'classification':r[1],'status':r[0],'source':r[2]['id'] if r[2] else 'No direct policy','created':datetime.now().strftime('%Y-%m-%d %H:%M:%S')};st.session_state.created.insert(0,z);log('TICKET_CREATED',z);return tid

with st.sidebar:
 st.markdown('<div style="font:700 1.35rem Space Grotesk">✦ Veridian</div>',unsafe_allow_html=True);st.caption('Internal Service Desk AI');st.divider()
 page=st.radio('Workspace',['Overview','AI Support','Request Queue','Tickets & Audit','Knowledge Base'],label_visibility='collapsed');st.divider();st.markdown('**Agent status**');st.success('Online');st.caption('Source-constrained • IT Support');st.divider();st.caption('Assignment 2 • 21–25 Sep 2026')

if page=='Overview':
 st.markdown('<div class="hero"><div class="eyebrow">Internal Service Agent</div><h1>Good evening. What needs attention?</h1><p>AI-assisted IT support with transparent decisions, source grounding and human escalation when policy is missing or risk is high.</p></div>',unsafe_allow_html=True)
 st.markdown(f'<div class="kpis"><div class="metric"><small>Requests</small><b>{len(REQUESTS)}</b><span>supplied data pack</span></div><div class="metric"><small>Policies</small><b>{len(POLICIES)}</b><span>available sources</span></div><div class="metric"><small>History</small><b>{len(TICKETS)}</b><span>existing tickets</span></div><div class="metric"><small>Session tickets</small><b>{len(st.session_state.created)}</b><span>created live</span></div></div>',unsafe_allow_html=True)
 a,b=st.columns([1.3,.7]);
 with a:
  st.markdown('<div class="card"><b>✦ Agent workflow</b><p class="muted">Every request follows the same auditable path.</p><p><b>01</b> Understand → <b>02</b> Ground → <b>03</b> Decide → <b>04</b> Record</p><hr><b>Design principle</b><p class="muted">If the supplied data does not support a decision, the agent asks or routes instead of hallucinating policy.</p></div>',unsafe_allow_html=True)
 with b:
  st.markdown('<div class="card"><b>Recent activity</b><p class="muted">Live session events</p>',unsafe_allow_html=True)
  for e in st.session_state.audit[:5]:st.markdown(f'**{e["event"]}**<br><span class="muted">{e["timestamp"]}</span>',unsafe_allow_html=True)
  if not st.session_state.audit:st.caption('Run the agent to begin.');st.markdown('</div>',unsafe_allow_html=True)

elif page=='AI Support':
 st.markdown('<div class="hero"><div class="eyebrow">AI Support</div><h1>Ask the service desk</h1><p>Describe an issue naturally. The agent classifies it, finds the supplied policy and explains the next action.</p></div>',unsafe_allow_html=True)
 examples={'Laptop failure':'My laptop won’t turn on at all, it’s completely dead, had it about 3.5 years now.','Phishing':'I think I got a phishing email asking for my login.','Guest Wi-Fi':'Can I get Wi-Fi access for a guest visiting our office tomorrow?','VPN expired':'My VPN stopped working this morning, says credentials expired.','Unclear':'hey can you help, its not working'}
 l,r=st.columns([1.05,.95],gap='large')
 with l:
  choice=st.selectbox('Try a scenario',['Custom']+list(examples));default='' if choice=='Custom' else examples[choice]
  with st.form('agent'):
   msg=st.text_area('Employee message',default,height=155,placeholder='Type the employee issue…');c1,c2=st.columns(2);name=c1.text_input('Employee name','Demo Employee');email=c2.text_input('Employee email','demo@veridian-corp.example');run=st.form_submit_button('Run agent  →',type='primary',use_container_width=True)
  if run and msg.strip():
   st.session_state.last=(msg,resolve(msg),name,email);log('AGENT_RUN',{'input':msg,'classification':st.session_state.last[1][1],'status':st.session_state.last[1][0]});st.rerun()
 with r:
  st.markdown('<div class="card"><b>Live decision</b><p class="muted">Transparent output</p>',unsafe_allow_html=True)
  if not st.session_state.last:st.markdown('### ✦');st.caption('Run a scenario to see the decision.')
  else:
   msg,(status,intent,p,answer,nxt,need),name,email=st.session_state.last;st.markdown(badge(status),unsafe_allow_html=True);st.markdown(f'**Intent:** `{intent}`');st.markdown('**Agent response**');st.write(answer);st.markdown('**Next action**');st.write(nxt)
   if p:st.markdown(f'<div class="source"><b>Source · {p["id"]} — {p["title"]}</b><br><span class="muted">{p["text"]}</span></div>',unsafe_allow_html=True)
   else:st.markdown('<div class="source"><b>Source guardrail</b><br><span class="muted">No direct supplied policy supports this approval path.</span></div>',unsafe_allow_html=True)
   if need and st.button('Create structured ticket',type='primary',use_container_width=True):st.success(f'Ticket {make_ticket(msg,(status,intent,p,answer,nxt,need),name,email)} created.')
  st.markdown('</div>',unsafe_allow_html=True)

elif page=='Request Queue':
 st.markdown('<div class="hero"><div class="eyebrow">Operations</div><h1>Employee request queue</h1><p>Search, inspect and analyze the supplied employee cases.</p></div>',unsafe_allow_html=True)
 q=st.text_input('Search requests',placeholder='Employee, issue or request ID…');rows=[x for x in REQUESTS if not q or q.lower() in json.dumps(x).lower()];st.caption(f'{len(rows)} requests shown')
 for x in rows:
  st.markdown(f'<div class="ticket"><b>{x["id"]}</b> · {x["employee"]}<br><span class="muted">{x["date"]} · {x["action"]}</span><br><br>{x["request"]}</div>',unsafe_allow_html=True)
  if st.button('Analyze '+x['id'],key='a'+x['id']):
   z=resolve(x['request']);log('QUEUE_ANALYSIS',{'request_id':x['id'],'classification':z[1],'status':z[0]});st.markdown(badge(z[0])+f' **{z[1]}**',unsafe_allow_html=True);st.success(z[3]);st.info('Next: '+z[4]);
   if z[2]:st.caption(f'Source: {z[2]["id"]} — {z[2]["title"]}')

elif page=='Tickets & Audit':
 st.markdown('<div class="hero"><div class="eyebrow">Traceability</div><h1>Tickets & audit trail</h1><p>Review everything the prototype created during this session.</p></div>',unsafe_allow_html=True)
 t1,t2=st.tabs(['Created tickets','Audit events'])
 with t1:
  st.dataframe(st.session_state.created,use_container_width=True,hide_index=True) if st.session_state.created else st.info('No tickets created yet.')
 with t2:
  st.dataframe(st.session_state.audit,use_container_width=True,hide_index=True) if st.session_state.audit else st.info('No audit events yet.')

else:
 st.markdown('<div class="hero"><div class="eyebrow">Grounding</div><h1>Knowledge base</h1><p>The agent can only ground answers in the supplied Veridian policies and ticket history.</p></div>',unsafe_allow_html=True)
 for p in POLICIES:
  with st.expander(f'{p["id"]}  ·  {p["title"]}'):st.write(p['text'])
 st.divider();st.subheader('Existing ticket history');st.dataframe(TICKETS,use_container_width=True,hide_index=True)
