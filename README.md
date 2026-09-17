# Veridian Internal Service Agent

A source-constrained **IT Support Agent prototype** that helps employees handle common internal IT requests using supplied company policies and knowledge.

The agent understands an employee's request, identifies the relevant intent, retrieves the applicable policy, and decides whether to **resolve, ask for clarification, route, or escalate** the request.

The prototype is designed to be **policy-grounded, auditable, and resistant to unsupported assumptions**.

---

## Overview

```text
Employee Request
       ↓
Intent Classification
       ↓
Policy Retrieval
       ↓
Decision Engine
       ↓
┌──────────┬───────────┬───────────┬─────────┐
│ Resolve  │ Follow-up │ Escalate  │ Route   │
└──────────┴───────────┴───────────┴─────────┘
       ↓
   Ticket Creation
       ↓
   Audit Trail
```

### Key capabilities

* Understand natural-language IT requests
* Classify requests into supported intents
* Retrieve relevant policies and knowledge
* Provide source-grounded responses
* Ask follow-up questions when information is missing
* Resolve straightforward requests
* Route requests to the appropriate function
* Escalate security-sensitive or unsupported cases
* Create structured support tickets
* Display the source used for a response
* Maintain an audit trail
* Analyze requests from the support queue

---

## Source-Constrained Design

The agent uses the supplied Veridian knowledge base as its source of truth.

It does **not** invent:

* Approval workflows
* SLAs
* Internal owners
* Troubleshooting procedures
* Access requirements
* Security procedures
* Unsupported policies

When the available information is insufficient, the agent asks for clarification or escalates instead of guessing.

---

## Example

**Employee**

> My VPN stopped working this morning. It says my credentials expired.

**Agent**

```text
Decision: RESOLVE

Source: KB-02 — VPN Access

Action:
Renew the VPN credentials.

Policy:
VPN credentials expire every 90 days.
```

For a security-sensitive request:

**Employee**

> I think I received a phishing email asking for my login.

**Agent**

```text
Decision: ESCALATE

Source: KB-09 — Security Incident Reporting

Action:
Report the incident to the Security team.
```

For an unclear request:

**Employee**

> Hey, can you help? It's not working.

**Agent**

```text
Decision: FOLLOW-UP REQUIRED

Please describe what is not working and provide
the relevant error message or symptom.
```

---

## Application

The Streamlit prototype provides:

### Employee Support

Submit an IT issue and receive a policy-grounded response.

### Request Queue

Review and analyze supplied employee requests.

### Audit Trail

View agent decisions, actions, and ticket creation events.

### Knowledge Base

Explore the policies, knowledge, and ticket history available to the agent.

---

## Project Structure

```text
internal_service_agent/
│
├── app.py
├── data.json
├── requirements.txt
├── README.md
├── ARCHITECTURE.md
├── INPUTS_SOURCES_ASSUMPTIONS.md
├── AI_TOOLS_USED.md
└── DEMO_SCRIPT.md
```

---

## Technology

* **Python** — application and decision logic
* **Streamlit** — web interface
* **JSON** — prototype data storage
* **Git/GitHub** — version control

The prototype does not require an external LLM API at runtime. This keeps the system reproducible and ensures responses remain constrained to the available source data.

---

## Run Locally

### Requirements

* Python 3.9+
* pip

### Setup

```bash
git clone <YOUR_REPOSITORY_URL>
cd internal_service_agent

python -m venv .venv
```

**Windows**

```bash
.venv\Scripts\activate
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the application:

```bash
streamlit run app.py
```

---

## Prototype Scope

This is a lightweight prototype demonstrating the behavior of an internal IT support agent.

It does not directly perform production actions such as:

* Unlocking accounts
* Changing permissions
* Installing software
* Modifying VPN credentials
* Sending security notifications
* Updating production ITSM systems

Instead, it determines the appropriate next action and presents it to the user.

---

## Future Extensions

A production implementation could add:

* Enterprise LLM and RAG
* Persistent database storage
* SSO and role-based access
* ServiceNow/Jira integration
* Identity and endpoint integrations
* Human approval workflows
* Persistent audit logging
* Monitoring and analytics

---

## License

Prototype project for demonstration and development purposes.
