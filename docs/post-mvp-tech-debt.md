# Post-MVP Technical Debt Tracker

This document captures intentional follow-ups after Phase 20 refactor and cleanup.

## Backend

- **Decouple application from infrastructure completely**
  - `CodeSnippetService` still imports infrastructure snippet assembly directly.
  - Follow-up: introduce a `SnippetAssembler` application port and inject implementation from `api/deps.py`.
- **Move registry seeding orchestration out of application layer**
  - `RegistrySeeder` currently imports persistence/registry infrastructure directly.
  - Follow-up: move this bootstrap logic into startup wiring or add explicit bootstrap ports.
- **Expand service-level tests to API integration tests**
  - Current tests focus on fast service units with in-memory doubles.
  - Follow-up: add an integration test layer against a temporary Postgres instance for auth + project + requirement + onboarding routes.

## Frontend

- **Consolidate API envelope types**
  - Some API response types are grouped by feature files (`requirement`, `recommendation`, `studio`).
  - Follow-up: introduce a shared `src/types/api-envelopes.ts` to reduce drift and duplicate shape definitions.
- **Add component-level tests for critical screens**
  - Current tests cover onboarding ordering logic only.
  - Follow-up: add React component tests for login flow, requirement intake success/error states, and architecture selection confirmation.
- **Stabilize API client paths**
  - API paths are still string literals in individual client modules.
  - Follow-up: centralize route builders in `src/lib/api/routes.ts` for safer refactors.

## DevEx and Quality

- **Coverage gates**
  - CI currently runs lint/typecheck/tests but does not enforce minimum coverage.
  - Follow-up: add lightweight coverage thresholds once baseline suites mature.
- **Boundary checks**
  - Follow-up: add static checks (or architecture tests) that prevent `application/*` from importing `infrastructure/*` directly.
