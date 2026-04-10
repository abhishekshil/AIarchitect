# Cursor Prompt Pack

## 20-Phase Step-by-Step Development Plan

## AI Solution Planning Engine

Use this file as a copy-paste prompt sequence inside Cursor.

---

# 0. Master Prompt

Paste this first into Cursor before starting Phase 1.

```text
You are my senior staff engineer and system architect.

We are building a product called:
AI Solution Planning Engine

Core idea:
This is NOT a fixed AI workflow builder.
This is a general AI solution planning engine that takes a user requirement in natural language, analyzes it, maps it to capability blocks, generates multiple architecture options, lets the user select one, creates architecture-specific onboarding tasks, assembles the runtime workflow, provides inference/testing, and generates integration-ready code snippets.

The platform must support current and future patterns such as:
- single LLM
- multi-LLM
- RAG + LLM
- fine-tuned model
- RAG + LLM + fine-tuning
- multi-agent systems
- hybrid agentic systems
- structured extraction pipelines
- classification/routing workflows
- future unknown combinations through capability composition

Important architectural principle:
Do not hardcode the platform around only a few known flows.
Build it as a modular planning engine with registries, canonical internal objects, graph-based planning, and extensible workflow generation.

We will build this step by step.

Your behavior rules:
1. Do not jump ahead.
2. For each step, first explain what we are building and why.
3. Then propose the exact folder structure, file list, interfaces, and implementation order.
4. Then generate code only for the current step.
5. Keep code production-oriented, typed, and modular.
6. Prefer clean architecture and future extensibility over shortcuts.
7. If a design decision affects future steps, state it explicitly.
8. When something is incomplete, add TODO comments and document extension points.
9. After each step, provide:
   - what was created
   - how to run it
   - what to test
   - what the next step should be
10. If you need to choose, optimize for:
   - maintainability
   - extensibility
   - clarity
   - modularity
   - developer experience

Target stack for MVP:
- Frontend: Next.js + TypeScript
- Backend: FastAPI + Python
- DB: PostgreSQL
- Cache/queue: Redis
- Object storage: S3-compatible abstraction
- Vector store: abstracted behind interface
- Auth: simple email/password or mock auth first, designed to be replaceable
- API style: REST first
- Async jobs: background workers / queue abstraction
- ORM: choose practical modern options
- Validation: strong schema validation
- Containers: Docker-ready
- Monorepo preferred if practical

Core internal concepts the codebase must support:
- RequirementProfile
- ConstraintProfile
- CapabilityBlock
- ArchitectureTemplate
- SolutionCandidate
- TaskGraph
- RuntimeGraph
- EvaluationPlan
- IntegrationPackage

MVP product flow:
1. User login
2. Create project
3. Submit requirement
4. Analyze requirement
5. Generate architecture options
6. Select architecture
7. Generate onboarding tasks
8. Complete onboarding
9. Build system
10. Test in inference playground
11. Generate code snippets

Initial supported patterns for MVP:
- single LLM assistant
- RAG assistant
- classification/extraction workflow
- RAG + validator/agent workflow

Non-goals for first build:
- full production fine-tuning pipeline
- enterprise-grade IAM
- full autonomous agents
- complex billing
- full provider marketplace

Now follow this execution protocol:

PHASE EXECUTION PROTOCOL

For each phase:
A. Restate the phase objective in 3-6 bullets
B. Propose architecture/design for this phase
C. List files to create/update
D. Generate code
E. Give run/test instructions
F. Stop and wait for my confirmation before next phase

Important:
Never implement multiple phases at once unless I explicitly ask.

Project phases:
Phase 1: Monorepo/project foundation
Phase 2: Backend domain models and database schema
Phase 3: Auth and project management APIs
Phase 4: Requirement intake and normalization
Phase 5: Capability registry and architecture template registry
Phase 6: Candidate synthesis and scoring engine
Phase 7: Architecture recommendation APIs
Phase 8: Architecture selection and task graph generation
Phase 9: Guided onboarding APIs
Phase 10: Runtime graph builder and build orchestration skeleton
Phase 11: Inference playground backend skeleton
Phase 12: Code snippet generation
Phase 13: Frontend app shell and dashboard
Phase 14: Requirement intake UI
Phase 15: Architecture options UI
Phase 16: Onboarding UI
Phase 17: Build/test/integration UI
Phase 18: Docker/dev environment and local setup hardening
Phase 19: Basic tests and CI skeleton
Phase 20: Refactor pass and technical debt cleanup

Implementation constraints:
- backend must separate domain, application, infrastructure, and API layers where reasonable
- registries must be config-driven or interface-driven, not tightly hardcoded
- candidate scoring should be explainable
- architecture options must include rationale and trade-offs
- onboarding generation must be driven by selected architecture/capabilities
- runtime graph must be represented as structured data, even if execution is mocked initially
- code snippets must be architecture-aware
- all APIs should be designed so frontend can consume them without rework later

When generating code:
- generate real code, not pseudo-code
- include types/interfaces/schemas
- include comments only where useful
- avoid overengineering
- make reasonable assumptions and state them
- if something should be mocked in MVP, mock it cleanly behind an interface

Start with:
Phase 1: Monorepo/project foundation

For Phase 1, do all of the following:
- propose monorepo layout
- choose backend and frontend package structure
- set up shared conventions
- create initial backend and frontend skeletons
- set up environment variable strategy
- set up formatting/linting basics
- set up Docker/devcontainer-friendly structure
- explain why this structure supports future extensibility

Then stop.
```

---

# 1. Phase 1 Prompt

```text
Proceed to Phase 1: Monorepo/project foundation.

Requirements:
- propose monorepo layout
- choose backend and frontend package structure
- set up shared conventions
- create initial backend and frontend skeletons
- set up environment variable strategy
- set up formatting/linting basics
- set up Docker/devcontainer-friendly structure
- explain why this structure supports future extensibility
- stop after Phase 1
```

---

# 2. Phase 2 Prompt

```text
Proceed to Phase 2: Backend domain models and database schema.

Requirements:
- create core domain models
- define DB schema
- keep canonical internal objects central
- separate persistence models from domain models where useful
- include migrations or migration-ready structure
- model at least the following concepts:
  - User
  - Organization/Workspace
  - Project
  - RequirementProfile
  - ConstraintProfile
  - ArchitectureTemplate
  - SolutionCandidate
  - TaskGraph
  - RuntimeGraph
  - EvaluationPlan
  - IntegrationPackage
- explain any trade-offs between normalized schema vs JSON fields
- stop after Phase 2
```

---

# 3. Phase 3 Prompt

```text
Proceed to Phase 3: Auth and project management APIs.

Requirements:
- create minimal auth suitable for MVP
- create project CRUD APIs
- keep auth replaceable for future enterprise auth
- include API schemas, routes, services, and persistence wiring
- support user signup/login/logout/me
- support workspace-aware project creation and listing
- define authorization boundaries clearly
- stop after Phase 3
```

---

# 4. Phase 4 Prompt

```text
Proceed to Phase 4: Requirement intake and normalization.

Requirements:
- implement requirement submission API
- define RequirementProfile and ConstraintProfile creation flow
- support raw text input first
- normalization can be heuristic/rule-based initially
- keep design extensible for future LLM-assisted analysis
- infer fields such as:
  - business goal
  - primary task type
  - grounding need
  - latency sensitivity
  - cost sensitivity
  - privacy sensitivity
  - human-in-loop need
- store both raw and normalized requirement data
- stop after Phase 4
```

---

# 5. Phase 5 Prompt

```text
Proceed to Phase 5: Capability registry and architecture template registry.

Requirements:
- create registry abstractions
- seed initial capabilities
- seed initial architecture templates
- keep registry config-driven where practical
- support capability metadata such as inputs, outputs, prerequisites, compatibility, risk, and cost profile
- support architecture template metadata such as required capabilities, optional capabilities, supported constraints, onboarding template ref, runtime graph template ref, and evaluation template ref
- make it easy to add new capabilities/templates later without core rewrites
- stop after Phase 5
```

---

# 6. Phase 6 Prompt

```text
Proceed to Phase 6: Candidate synthesis and scoring engine.

Requirements:
- synthesize multiple solution candidates from RequirementProfile + registries
- add explainable scoring
- output trade-offs and rationale
- keep heuristics simple but extensible
- support multiple scoring modes such as:
  - best overall
  - lowest cost
  - fastest to launch
  - highest quality
- output fields should include:
  - summary
  - score
  - rationale
  - trade-offs
  - complexity estimate
  - latency estimate
  - cost estimate
- stop after Phase 6
```

---

# 7. Phase 7 Prompt

```text
Proceed to Phase 7: Architecture recommendation APIs.

Requirements:
- expose APIs to fetch candidate architecture options
- return structured option payloads for frontend
- include rationale, trade-offs, score, complexity, and cost estimate fields
- support recommendation generation per project
- persist generated candidates for later selection
- make response format stable for UI consumption
- stop after Phase 7
```

---

# 8. Phase 8 Prompt

```text
Proceed to Phase 8: Architecture selection and task graph generation.

Requirements:
- persist selected candidate
- generate TaskGraph from architecture template + candidate capabilities
- include dependencies and guidance references
- represent onboarding as structured task nodes and edges
- support conditional task generation where possible
- keep task graph extensible for future architectures
- stop after Phase 8
```

---

# 9. Phase 9 Prompt

```text
Proceed to Phase 9: Guided onboarding APIs.

Requirements:
- provide onboarding task retrieval APIs
- allow task submission APIs
- validate task responses
- support progress tracking
- include task guidance, suggestions, and example placeholders
- support task states such as:
  - not_started
  - in_progress
  - submitted
  - validated
  - requires_revision
  - completed
- stop after Phase 9
```

---

# 10. Phase 10 Prompt

```text
Proceed to Phase 10: Runtime graph builder and build orchestration skeleton.

Requirements:
- create RuntimeGraph representation
- translate selected architecture + onboarding into runtime graph
- build can be mocked but must be structured
- include async job skeleton
- include build status tracking
- support runtime graph nodes such as:
  - model node
  - retriever node
  - validator node
  - router node
  - agent node
  - formatter node
- persist runtime graph versions
- stop after Phase 10
```

---

# 11. Phase 11 Prompt

```text
Proceed to Phase 11: Inference playground backend skeleton.

Requirements:
- expose test endpoint
- load runtime graph
- mock or partially implement architecture-aware inference behavior
- prepare response structure for citations, traces, and metadata
- support at least these mocked behaviors:
  - single LLM response
  - RAG response with citations
  - classification/extraction structured response
  - RAG + validator/agent trace output
- persist inference history
- stop after Phase 11
```

---

# 12. Phase 12 Prompt

```text
Proceed to Phase 12: Code snippet generation.

Requirements:
- generate architecture-aware snippets
- support cURL, JavaScript, and Python
- include example request/response and environment notes
- generate snippets from project architecture + endpoint metadata
- include sample code for inference/testing usage
- keep snippet generation modular for future SDK expansion
- persist generated snippets if useful
- stop after Phase 12
```

---

# 13. Phase 13 Prompt

```text
Proceed to Phase 13: Frontend app shell and dashboard.

Requirements:
- build frontend app shell
- add auth-aware routing skeleton
- create dashboard page
- create project list/create flow UI
- establish shared layout, navigation, and state conventions
- keep frontend modular and ready for upcoming workflow screens
- stop after Phase 13
```

---

# 14. Phase 14 Prompt

```text
Proceed to Phase 14: Requirement intake UI.

Requirements:
- build requirement submission page
- connect to backend API
- include project context
- show loading, error, and success states
- support raw text input first
- prepare UI structure for future file attachment support
- keep UI clean and extensible
- stop after Phase 14
```

---

# 15. Phase 15 Prompt

```text
Proceed to Phase 15: Architecture options UI.

Requirements:
- build architecture recommendation screen
- render architecture cards or comparison table
- show rationale, score, trade-offs, cost, complexity, and latency indicators
- allow user to select one option
- connect selection action to backend API
- keep UI simple for non-technical users but information-rich enough for technical users
- stop after Phase 15
```

---

# 16. Phase 16 Prompt

```text
Proceed to Phase 16: Onboarding UI.

Requirements:
- build onboarding task flow UI from TaskGraph
- support sequential or graph-backed step rendering
- show task guidance, examples, validation errors, and progress
- support task submission and status updates
- keep design flexible for different architecture types
- stop after Phase 16
```

---

# 17. Phase 17 Prompt

```text
Proceed to Phase 17: Build/test/integration UI.

Requirements:
- build system build status screen
- build inference playground UI
- build integration/snippet tab
- display architecture-aware output metadata such as citations or traces
- support code language switching for snippets
- support copy actions and basic usage instructions
- stop after Phase 17
```

---

# 18. Phase 18 Prompt

```text
Proceed to Phase 18: Docker/dev environment and local setup hardening.

Requirements:
- add or refine Docker setup
- add docker-compose or equivalent local orchestration
- harden environment variable handling
- improve local developer experience
- ensure backend, frontend, db, and redis can run together locally
- add startup/readme instructions if missing
- stop after Phase 18
```

---

# 19. Phase 19 Prompt

```text
Proceed to Phase 19: Basic tests and CI skeleton.

Requirements:
- add basic backend tests
- add basic frontend tests where practical
- add CI skeleton for lint, type-check, and test
- cover critical flows such as:
  - auth
  - project creation
  - requirement normalization
  - candidate generation
  - onboarding task submission
- keep test architecture maintainable and fast
- stop after Phase 19
```

---

# 20. Phase 20 Prompt

```text
Proceed to Phase 20: Refactor pass and technical debt cleanup.

Requirements:
- identify structural weaknesses across backend and frontend
- fix naming inconsistencies
- improve module boundaries where needed
- remove accidental coupling
- document TODOs for post-MVP work
- improve developer documentation
- do not do random rewrites; focus on maintainability and correctness
- stop after Phase 20
```

---

# Reusable Quality Prompt

Use this before any phase if needed.

```text
Before writing code, identify any weak assumptions or structural mistakes in the current codebase and fix them only if they block this phase. Do not do unrelated refactors.
```

---

# Reusable Short Prompt

Use this when continuing phase by phase.

```text
Act as my senior engineer for the AI Solution Planning Engine project.

Follow these rules:
- only implement the current phase
- explain the design first
- list files before coding
- write production-oriented modular code
- preserve extensibility for registries, candidate scoring, task graphs, runtime graphs, and architecture templates
- after coding, give run/test instructions and stop

Current phase:
[PASTE CURRENT PHASE HERE]

Project context:
- Next.js frontend
- FastAPI backend
- PostgreSQL
- Redis
- modular planning engine, not a fixed workflow builder
- MVP supports single LLM, RAG, classification/extraction, and RAG + validator/agent flow

Core internal objects:
- RequirementProfile
- ConstraintProfile
- CapabilityBlock
- ArchitectureTemplate
- SolutionCandidate
- TaskGraph
- RuntimeGraph
- EvaluationPlan
- IntegrationPackage

Now implement only this phase.
```

---

# Usage Note

Recommended usage order:

1. Paste the Master Prompt once.
2. Run each phase prompt one by one.
3. Do not let Cursor skip phases.
4. Review output after each phase before continuing.
5. Use the reusable quality prompt whenever the codebase starts drifting.



# LLM
You are my senior staff engineer and AI systems architect.

We have completed the first 20 development phases of the AI Solution Planning Engine platform.

Now we are doing the next major step:

ADD LLM-POWERED INTELLIGENCE LAYER
WITHOUT BREAKING THE DETERMINISTIC PLANNING CORE.

Important context:
This platform is NOT a generic chatbot product.
It is a general AI solution planning engine.

The existing system already includes:
- auth
- projects
- requirement intake
- requirement normalization
- capability registry
- architecture template registry
- candidate synthesis
- candidate scoring
- architecture recommendation APIs
- architecture selection
- task graph generation
- guided onboarding APIs
- runtime graph builder
- inference playground skeleton
- code snippet generation
- frontend flows
- tests / CI / refactor baseline

Critical design rule:
Do NOT replace the deterministic core with free-form LLM behavior.
We are adding LLMs as an intelligence layer around the planning engine, not turning the whole platform into an uncontrolled agent system.

The deterministic core must remain the source of truth for:
- capability compatibility
- policy checks
- architecture scoring framework
- task graph structure
- runtime graph structure
- evaluation thresholds
- integration package structure

LLMs should be added for:
1. requirement understanding
2. constraint extraction assistance
3. clarification question generation
4. candidate explanation generation
5. onboarding guidance generation
6. improvement suggestions
7. optional architecture refinement assistance
8. optional evaluation explanation

Goal:
Refactor and extend the codebase so LLMs are integrated cleanly, behind interfaces, with provider abstraction, prompt versioning, typed outputs, validation, fallback logic, and observability.

Behavior rules:
1. First inspect the current codebase structure and identify the best integration points.
2. Do not rewrite the whole project.
3. Preserve existing APIs where possible.
4. Introduce LLM functionality through new abstractions and adapters.
5. All LLM outputs must be validated before use.
6. Every LLM-powered feature must have deterministic fallback behavior.
7. Keep the system provider-agnostic.
8. Use structured output patterns wherever possible.
9. Make prompts versionable and easy to improve later.
10. Stop after implementing this LLM integration phase.

What I want you to build:

PART 1 — LLM ARCHITECTURE DESIGN
Design and implement an LLM integration layer with clear boundaries.

Create or refine these concepts if they do not already exist:
- LLMProvider interface
- PromptTemplate abstraction
- PromptRegistry
- LLMTask enum or typed task identifiers
- StructuredOutput schemas
- LLMResponse validator
- Fallback strategy layer
- LLM telemetry / observability hooks

Provider design requirements:
- provider-agnostic abstraction
- start with one real provider if needed, but design for multiple providers
- support chat/completions style invocation
- support structured JSON output mode where available
- support timeout and retry settings
- support model selection by task

Prompt system requirements:
- prompts must not be scattered through business logic
- prompts should be stored in a structured prompt registry or dedicated prompt modules
- each prompt should have:
  - prompt id
  - purpose
  - version
  - expected output schema
  - fallback behavior notes

PART 2 — ADD LLM TO REQUIREMENT UNDERSTANDING
Integrate LLM support into requirement normalization.

The LLM should help with:
- extracting business goal
- identifying primary and secondary task types
- inferring grounding need
- inferring behavior specialization need
- inferring privacy/compliance sensitivity
- inferring latency/cost sensitivity
- identifying whether human-in-loop may be required
- identifying whether agentic decomposition may help
- generating confidence and ambiguity hints

Requirements:
- LLM output must map into RequirementProfile and ConstraintProfile
- LLM output must be schema-validated
- existing deterministic normalization should remain as fallback
- if LLM confidence is weak or malformed, fallback to current rule-based logic
- preserve auditability of raw input, llm output, validated output, and final normalized result

PART 3 — CLARIFICATION QUESTION GENERATION
Add an LLM-powered clarification subsystem.

Use it only when:
- normalization confidence is low
- key fields are missing
- requirement ambiguity is high

Requirements:
- generate minimal clarifying questions
- questions should be concise and useful
- questions must map to missing planning fields
- include deterministic guardrails to avoid unnecessary questioning
- persist clarification suggestions in a structured way

PART 4 — LLM FOR ARCHITECTURE EXPLANATION
Do NOT use the LLM to decide the final architecture ranking.
Use it to explain already generated candidates.

For each SolutionCandidate, the LLM may generate:
- user-friendly summary
- why this option fits
- plain-language trade-offs
- when not to use this option
- data requirements explanation

Requirements:
- explanations must be derived from candidate metadata and deterministic score breakdown
- do not let the LLM invent architecture facts not present in the candidate
- keep generated explanation text clearly separated from actual scoring fields
- if LLM explanation fails, fallback to templated deterministic explanation

PART 5 — LLM FOR ONBOARDING GUIDANCE
Add LLM-powered guidance generation for onboarding tasks.

The LLM may generate:
- step explanations
- examples
- tips
- warnings
- suggested good inputs

Requirements:
- task structure still comes from TaskGraph
- LLM only enriches guidance content
- guidance must be contextual to architecture type, task type, and current project context
- fallback to static guidance if LLM generation fails

PART 6 — LLM FOR IMPROVEMENT SUGGESTIONS
Add a suggestion engine that uses LLMs to propose improvements after:
- onboarding validation errors
- weak evaluation results
- poor inference outcomes

Examples:
- suggest more representative data
- suggest using retrieval instead of only prompting
- suggest adding validator agent
- suggest reducing architecture complexity
- suggest better task instructions

Requirements:
- suggestions must be tagged by category
- suggestions must not directly overwrite project state
- suggestions should remain advisory
- include deterministic filters so unsafe or irrelevant suggestions are blocked

PART 7 — OPTIONAL ARCHITECTURE REFINEMENT ASSIST
Add an optional LLM-assisted refinement layer that proposes candidate modifications before final recommendation.

Examples:
- detect that retrieval + validation may be better than plain retrieval
- detect that a routing layer may help
- detect that a multi-step flow may need human approval

Requirements:
- this is advisory only
- deterministic candidate synthesis and scoring still remain authoritative
- refinement proposals should become structured candidate hints, not free-form decisions
- implement behind a feature flag if appropriate

PART 8 — OPTIONAL EVALUATION EXPLANATION
Add LLM-generated natural language summaries for evaluation results.

Requirements:
- input should be evaluation metrics and findings
- output should be a concise human-readable explanation
- no metric fabrication
- keep raw evaluation metrics untouched
- fallback to deterministic summary generation

PART 9 — ENGINEERING REQUIREMENTS
Implement this cleanly in the current codebase.

Do all of the following:
- identify existing modules to extend
- create new LLM-specific modules where appropriate
- keep domain/application/infrastructure boundaries clean
- add env vars/config strategy for LLM providers
- add prompt versioning strategy
- add schema validation for every structured LLM output
- add logging / tracing for LLM calls
- add retry/timeout handling
- add explicit fallback paths
- add tests for critical LLM integration points
- add docs for how to configure and extend the LLM layer

PART 10 — DELIVERABLE FORMAT
Work in this order:
A. explain the overall integration strategy
B. identify exact files/modules to add or change
C. explain the data flow changes
D. implement code
E. explain how to configure provider credentials
F. explain how to run and test
G. list future extension points
H. stop

Additional implementation guidance:
- prefer typed Pydantic models / strong schemas for structured outputs
- do not trust raw LLM text directly
- every LLM feature must degrade gracefully
- keep the LLM layer modular enough to later support multiple providers and model routing
- keep prompts isolated from orchestration logic
- avoid tight coupling between providers and business modules
- do not introduce agent frameworks unless clearly necessary
- if feature flags help isolate rollout, use them

Success criteria:
- platform can use LLMs to improve normalization, explanation, clarification, guidance, and suggestions
- platform still works if LLM provider is unavailable
- architecture recommendation remains explainable and controlled
- new LLM layer is modular, testable, and extendable

Now inspect the existing codebase and implement this LLM integration phase only.