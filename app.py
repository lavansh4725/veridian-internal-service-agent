import json, re, uuid
from datetime import datetime
from pathlib import Path
import streamlit as st

DATA = json.loads((Path(__file__).parent / "data.json").read_text(encoding="utf-8"))
POLICIES, REQUESTS, TICKETS = DATA["policies"], DATA["requests"], DATA["tickets"]

st.set_page_config(page_title="Veridian Internal Service Agent", page_icon="🛠️", layout="wide")

if "audit" not in st.session_state:
    st.session_state.audit = []
if "created_tickets" not in st.session_state:
    st.session_state.created_tickets = []

def log_event(event, details):
    st.session_state.audit.insert(0, {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "event": event, "details": details
    })

def classify(text):
    t = text.lower()
    if any(x in t for x in ["phishing","malware","unauthorized access"]): return "security"
    if "password" in t or "locked out" in t or "login" in t and "expense" not in t: return "password"
    if "vpn" in t: return "vpn"
    if "laptop" in t or "screen" in t: return "laptop"
    if "software" in t or "extension" in t or "install" in t: return "software"
    if "printer" in t or "paper jam" in t: return "printer"
    if "mailbox" in t or "email" in t and "quota" in t: return "mailbox"
    if "guest" in t and "wifi" in t: return "wifi"
    if "monitor" in t or "home" in t and "equipment" in t: return "wfh"
    if "expense" in t: return "expense"
    if "admin access" in t or "server" in t: return "admin_access"
    return "unclear"

def policy_for(intent):
    mapping = {
        "password":"KB-01","vpn":"KB-02","laptop":"KB-03","software":"KB-04",
        "printer":"KB-05","mailbox":"KB-06","wifi":"KB-07","expense":"KB-08",
        "security":"KB-09","wfh":"KB-10"
    }
    pid = mapping.get(intent)
    return next((p for p in POLICIES if p["id"] == pid), None)

def resolve(text):
    intent = classify(text)
    p = policy_for(intent)
    t = text.lower()

    if intent == "unclear":
        return {"status":"FOLLOW-UP REQUIRED","intent":intent,"policy":None,
                "answer":"I need a little more information to identify the issue. Please describe what is not working and what you expected to happen.",
                "next":"Ask for the affected service/device and the exact error or symptom.",
                "ticket":True,"risk":"unclear"}

    if intent == "security":
        return {"status":"ESCALATE","intent":intent,"policy":p,
                "answer":"This is a suspected security incident. Report it immediately to security@veridian-corp.example. The policy says not to forward the message to other employees.",
                "next":"Route to Security; preserve the audit trail. Do not treat this as an ordinary IT ticket.",
                "ticket":True,"risk":"high"}

    if intent == "password":
        if "6 times" in t or "5" in t or "locked out" in t:
            return {"status":"RESOLVE","intent":intent,"policy":p,
                    "answer":"You are locked out after more than 5 failed attempts. IT should manually unlock the account; no approval is required.",
                    "next":"Route the unlock to IT. No approval is required.","ticket":True,"risk":"low"}
        return {"status":"RESOLVE","intent":intent,"policy":p,
                "answer":"You can reset your own password through the self-service portal at any time.",
                "next":"Use the self-service portal. If you become locked out after 5 failed attempts, contact IT for a manual unlock.",
                "ticket":False,"risk":"low"}

    if intent == "vpn":
        if "expired" in t:
            return {"status":"RESOLVE","intent":intent,"policy":p,
                    "answer":"VPN credentials expire every 90 days and must be renewed by the employee.",
                    "next":"Renew the VPN credentials. If the employee is a contractor requesting access rather than renewing credentials, manager approval via the access request form is required.",
                    "ticket":False,"risk":"low"}
        return {"status":"FOLLOW-UP REQUIRED","intent":intent,"policy":p,
                "answer":"VPN access is automatic for full-time employees; contractors require manager approval via the access request form.",
                "next":"Confirm whether the employee is full-time or a contractor and whether this is new access or credential renewal.",
                "ticket":True,"risk":"medium"}

    if intent == "laptop":
        hardware_failure = any(x in t for x in ["won’t turn","completely dead","flickering"])
        if hardware_failure and ("3.5" in t or "3.5 years" in t):
            return {"status":"RESOLVE","intent":intent,"policy":p,
                    "answer":"The laptop is about 3.5 years old and has a reported hardware failure. KB-03 permits replacement earlier than 3 years only for verified hardware failure; the Asset Management Policy says early replacement outside the 4-year refresh cycle also requires Finance sign-off in addition to IT approval.",
                    "next":"Verify the hardware failure, then route the early replacement for IT approval plus Finance sign-off. The request should normally be raised at least 2 weeks before intended replacement.",
                    "ticket":True,"risk":"medium"}
        if "2 years" in t:
            return {"status":"FOLLOW-UP REQUIRED","intent":intent,"policy":p,
                    "answer":"A 2-year-old laptop is below the 3-year replacement eligibility threshold, but KB-03 allows earlier replacement for verified hardware failure.",
                    "next":"Troubleshoot/verify the screen fault first. If hardware failure is verified, route for the applicable early-replacement approvals.",
                    "ticket":True,"risk":"medium"}
        return {"status":"FOLLOW-UP REQUIRED","intent":intent,"policy":p,
                "answer":"Laptops are eligible for replacement after 3 years, or earlier for verified hardware failure.",
                "next":"Confirm the laptop age and whether a hardware failure has been verified.",
                "ticket":True,"risk":"medium"}

    if intent == "software":
        if "not in" in t or "non-catalog" in t or "extension" in t:
            return {"status":"ESCALATE","intent":intent,"policy":p,
                    "answer":"Non-catalog software requires IT Security review, which takes 3–5 business days. The supplied data does not establish that this particular extension/tool is approved.",
                    "next":"Route to IT Security review; do not approve the installation directly.",
                    "ticket":True,"risk":"medium"}
        return {"status":"RESOLVE","intent":intent,"policy":p,
                "answer":"Standard software listed in the approved catalog can be self-installed.",
                "next":"Use the approved software catalog.","ticket":False,"risk":"low"}

    if intent == "printer":
        return {"status":"RESOLVE","intent":intent,"policy":p,
                "answer":"First check the printer queue and restart the print spooler. If the issue persists after the restart, log a ticket with the printer’s asset tag.",
                "next":"Perform the two troubleshooting steps, then escalate with the asset tag if unresolved.",
                "ticket":True,"risk":"low"}

    if intent == "mailbox":
        return {"status":"RESOLVE","intent":intent,"policy":p,
                "answer":"The default mailbox quota is 25GB. Archive old mail when nearing the quota. Any increase above 25GB requires manager approval and is capped at 50GB.",
                "next":"Archive old mail first. If more capacity is required, request manager approval for an increase up to 50GB.",
                "ticket":True,"risk":"low"}

    if intent == "wifi":
        return {"status":"RESOLVE","intent":intent,"policy":p,
                "answer":"Guest Wi-Fi credentials are valid for 24 hours and can be generated by any employee from the front-desk kiosk. No IT ticket is required.",
                "next":"Generate the guest credentials at the front-desk kiosk.","ticket":False,"risk":"low"}

    if intent == "wfh":
        return {"status":"FOLLOW-UP REQUIRED","intent":intent,"policy":p,
                "answer":"Employees working remotely more than 3 days/week are eligible for a one-time home-office equipment allowance covering a chair or monitor. Manager sign-off and Finance processing are required; IT handles shipping only after approval.",
                "next":"Obtain manager sign-off and Finance processing. Once approved, IT can handle the equipment shipping request.",
                "ticket":True,"risk":"medium"}

    if intent == "expense":
        return {"status":"ROUTE","intent":intent,"policy":p,
                "answer":"Expense-tool access is granted by Finance, not IT. IT can assist only with login/technical issues once an account already exists.",
                "next":"Confirm that an expense-tool account already exists. If access itself is missing, route to Finance; if the account exists, IT can assist with the login/technical issue.",
                "ticket":True,"risk":"medium"}

    if intent == "admin_access":
        return {"status":"ESCALATE","intent":intent,"policy":None,
                "answer":"The supplied policy set does not define an approval process for finance-server admin access. Existing history shows an admin-access request was rejected when no business justification was provided.",
                "next":"Do not invent an approval path. Ask for/route the business justification to the appropriate human owner.",
                "ticket":True,"risk":"high"}

def create_ticket(text, result, employee="Unknown", email=""):
    tid = "NEW-" + uuid.uuid4().hex[:6].upper()
    ticket = {"id":tid,"employee":employee,"email":email,"issue":text,
              "classification":result["intent"],"status":result["status"],
              "source":result["policy"]["id"] if result["policy"] else "No direct policy",
              "created":datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    st.session_state.created_tickets.insert(0,ticket)
    log_event("TICKET_CREATED", ticket)
    return tid

st.title("🛠️ Veridian Internal Service Agent")
st.caption("Source-constrained IT support prototype • Veridian Corp • Assignment 2")

with st.sidebar:
    st.header("Agent controls")
    mode = st.radio("Mode", ["Employee Support","Request Queue","Audit Trail","Knowledge Base"])
    st.divider()
    st.info("The agent is constrained to the supplied Veridian policies, employee requests and ticket history. It does not invent approval paths.")

if mode == "Employee Support":
    st.subheader("Ask the internal IT agent")
    examples = {
        "Choose an example…":"",
        "Laptop is dead":"My laptop won’t turn on at all, it’s completely dead, had it about 3.5 years now.",
        "Guest Wi-Fi":"Can I get Wi-Fi access for a guest visiting our office tomorrow?",
        "Phishing":"I think I got a phishing email asking for my login.",
        "Expense login":"I can’t log into the expense tool, keeps saying invalid credentials.",
        "Unclear request":"hey can you help, its not working"
    }
    choice = st.selectbox("Quick examples", list(examples))
    default = examples[choice]
    text = st.text_area("Employee message", value=default, height=120)
    c1,c2 = st.columns([1,1])
    with c1: employee = st.text_input("Employee name", "Demo Employee")
    with c2: email = st.text_input("Employee email", "demo@veridian-corp.example")
    if st.button("Run agent", type="primary") and text.strip():
        result = resolve(text)
        log_event("AGENT_RUN", {"input":text,"classification":result["intent"],"status":result["status"],
                                 "source":result["policy"]["id"] if result["policy"] else "None"})
        st.session_state.last_result = result
    if "last_result" in st.session_state:
        r = st.session_state.last_result
        st.divider()
        st.metric("Decision", r["status"])
        st.write("**Intent:**", r["intent"])
        st.write("**Agent response**")
        st.success(r["answer"])
        st.write("**Next action**")
        st.write(r["next"])
        st.write("**Source**")
        if r["policy"]:
            st.code(f'{r["policy"]["id"]} — {r["policy"]["title"]}\n{r["policy"]["text"]}')
        else:
            st.warning("No direct policy supports an approval path; the agent is intentionally routing to a human.")
        if r["ticket"]:
            if st.button("Create structured ticket"):
                tid = create_ticket(text, r, employee, email)
                st.success(f"Ticket {tid} created.")
        st.caption("Audit event is recorded automatically when the agent runs and when a ticket is created.")

elif mode == "Request Queue":
    st.subheader("Employee Request Queue")
    for req in REQUESTS:
        with st.expander(f'{req["id"]} • {req["employee"]} • {req["action"]}'):
            st.write(req["request"])
            if st.button(f'Analyze {req["id"]}', key=req["id"]):
                r = resolve(req["request"])
                log_event("QUEUE_ANALYSIS", {"request_id":req["id"],"classification":r["intent"],"status":r["status"]})
                st.write("**Decision:**", r["status"])
                st.write("**Response:**", r["answer"])
                st.write("**Next:**", r["next"])
                st.write("**Source:**", r["policy"]["id"] if r["policy"] else "No direct policy")

elif mode == "Audit Trail":
    st.subheader("Audit Trail")
    st.caption("Every agent execution and created ticket is recorded in this session.")
    if not st.session_state.audit:
        st.info("No events yet. Run the agent to create an audit trail.")
    else:
        st.dataframe(st.session_state.audit, use_container_width=True, hide_index=True)
    st.subheader("Created Tickets")
    if st.session_state.created_tickets:
        st.dataframe(st.session_state.created_tickets, use_container_width=True, hide_index=True)
    else:
        st.info("No tickets created in this session.")

elif mode == "Knowledge Base":
    st.subheader("Veridian Knowledge Base")
    for p in POLICIES:
        with st.expander(f'{p["id"]} — {p["title"]}'):
            st.write(p["text"])
    st.subheader("Existing Ticket History")
    st.dataframe(TICKETS, use_container_width=True, hide_index=True)
