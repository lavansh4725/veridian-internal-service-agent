# AI Tools Used

## Development

- ChatGPT was used to help structure the prototype, convert the assignment requirements into an implementation plan, and generate/refine code and documentation.

## Runtime

The prototype itself intentionally uses a deterministic policy/decision engine rather than requiring a live external LLM API. This makes the demo reproducible and ensures answers remain constrained to the supplied data pack.

## Production extension

A production version could add an enterprise-approved LLM for intent extraction and response generation, with retrieval restricted to the approved knowledge base and a policy validator before any response/action is returned.
