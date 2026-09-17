# Architecture & Process Flow

## Components

1. **UI layer — Streamlit**
   - Employee support chat-style form
   - Request queue
   - Knowledge base
   - Audit trail

2. **Intent classifier**
   - Maps the employee message to a constrained IT intent.
   - Includes an `unclear` state.

3. **Policy retrieval**
   - Maps intent to the exact policy ID in `data.json`.
   - No external policy source is used.

4. **Decision engine**
   - `RESOLVE`: enough information exists and the policy permits a direct answer/action.
   - `FOLLOW-UP REQUIRED`: a missing fact affects the decision.
   - `ESCALATE`: security, missing authority, or policy-sensitive case.
   - `ROUTE`: another corporate function owns the request.

5. **Ticket creator**
   - Generates a structured ticket ID.
   - Stores classification, status, source, employee and issue.

6. **Audit logger**
   - Records agent execution and ticket creation with timestamps.

## Process

```text
Employee message
      |
      v
Intent classification
      |
      +---- unclear --------------------> Ask follow-up
      |
      v
Policy retrieval
      |
      v
Decision engine
  |       |        |        |
Resolve Follow-up Escalate Route
  |       |        |        |
  +-------+--------+--------+
              |
              v
      Structured ticket
              |
              v
         Audit trail
```

## Guardrails

- Source-constrained: only supplied policies/data.
- No invented approvals or SLAs.
- Security incidents go to Security.
- Unclear ownership is surfaced.
- Historical tickets are context, not new policy.
- Closed tickets are treated as history.
