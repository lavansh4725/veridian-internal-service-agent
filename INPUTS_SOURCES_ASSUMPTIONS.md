# Inputs, Sources & Assumptions

## Inputs

- Employee free-text issue
- Employee name and email (for newly created tickets)
- Supplied employee request queue
- Supplied knowledge-base policies
- Supplied existing ticket history

## Sources

- Data Pack — Assignment 2: Internal Service Agent (IT Support)
- Agentic AI Factory Assignment Brief

## Assumptions

1. The data pack is the authoritative source for this prototype.
2. Existing tickets marked Resolved, Rejected, or Approved (closed) are treated as historical context, not actionable cases.
3. Active tickets remain actionable.
4. When the supplied data does not define an approval path, the agent does not invent one; it routes to a human.
5. The agent can recommend the next action but does not claim to have performed external actions that the prototype cannot actually execute.
6. "Create ticket" in the prototype means creating a structured local/session ticket record, not writing into Veridian's real ticketing platform.
