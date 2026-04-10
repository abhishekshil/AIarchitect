# LLM Integration Layer

This project now supports an LLM intelligence layer that augments (not replaces) deterministic planning.

## Design

- Deterministic core remains source of truth for scoring, policy checks, graph structure, and persistence.
- LLM calls are isolated behind provider and prompt abstractions:
  - `LLMProvider`
  - `PromptRegistry`
  - `LLMOrchestrator`
  - typed schema validators per task
- Every LLM-enhanced flow has deterministic fallback.

## Implemented LLM-enhanced surfaces

- Requirement normalization (`llm_assisted_v1`) with:
  - structured extraction
  - confidence gating
  - clarification question generation on ambiguity
  - fallback to heuristic normalizer
  - response-level audit payload (`normalization_audit`)
- Candidate explanations:
  - deterministic candidates are still generated and scored first
  - LLM optionally enriches summary/tradeoffs/reasoning
- Onboarding guidance:
  - static hints remain baseline
  - LLM can enrich suggestions and example placeholder

## Configuration

Set these env vars in `apps/api/.env`:

- `LLM_ENABLED` (`true|false`)
- `LLM_PROVIDER` (`disabled|openai_compatible`)
- `LLM_API_BASE_URL` (e.g. `https://api.openai.com/v1`)
- `LLM_API_KEY`
- `LLM_DEFAULT_MODEL`
- `LLM_TIMEOUT_S`
- `LLM_MAX_RETRIES`

If disabled or misconfigured, deterministic fallbacks remain active.

## Extension points

- Add new task prompts in `infrastructure/llm/prompts.py`.
- Add new structured schemas in `infrastructure/llm/schemas.py`.
- Add new features by calling `LLMOrchestrator.run_structured(...)`.
- Keep task outputs typed and validated before entering services/domain logic.
