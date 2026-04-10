from __future__ import annotations

from typing import Any

from solution_planning_api.application.ports.llm import LLMTask, PromptRegistry, PromptTemplate


class InMemoryPromptRegistry(PromptRegistry):
    def __init__(self) -> None:
        self._prompts: dict[LLMTask, PromptTemplate] = {
            LLMTask.REQUIREMENT_UNDERSTANDING: PromptTemplate(
                prompt_id="requirement_understanding",
                purpose="Extract structured requirement and constraint hints from raw requirement text.",
                version="1.0",
                expected_schema="RequirementUnderstandingOutput",
                fallback_notes="Fallback to heuristic normalizer if malformed/low confidence/unavailable.",
                system_prompt=(
                    "You are an AI planning analyst. Extract fields conservatively. "
                    "Do not invent facts not present in user text. Respond as JSON only."
                ),
                user_prompt_template=(
                    "Analyze this requirement text and return strict JSON:\n"
                    "{raw_text}\n\n"
                    "Return keys: business_goal, primary_task_type, secondary_task_types, "
                    "grounding_requirement, behavior_specialization_requirement, "
                    "privacy_level, security_sensitivity, latency_sensitivity, cost_sensitivity, "
                    "human_in_loop_requirement, agentic_decomposition_helpful, confidence_score, "
                    "ambiguity_signals."
                ),
            ),
            LLMTask.CLARIFICATION_QUESTIONS: PromptTemplate(
                prompt_id="clarification_questions",
                purpose="Generate minimal clarification questions for missing/ambiguous requirement fields.",
                version="1.0",
                expected_schema="ClarificationQuestionsOutput",
                fallback_notes="Return empty list if confidence is high or model fails.",
                system_prompt=(
                    "You generate concise clarification questions for product requirement intake."
                ),
                user_prompt_template=(
                    "Requirement text:\n{raw_text}\n\n"
                    "Known ambiguity signals:\n{ambiguity_signals}\n\n"
                    "Generate at most 4 concise questions. Each question must map to one planning field."
                ),
            ),
            LLMTask.CANDIDATE_EXPLANATION: PromptTemplate(
                prompt_id="candidate_explanation",
                purpose="Explain deterministic candidate results without changing scores.",
                version="1.0",
                expected_schema="CandidateExplanationOutput",
                fallback_notes="Keep deterministic summary/reasoning if generation fails.",
                system_prompt=(
                    "Explain architecture options from provided metadata only. "
                    "Never fabricate capabilities or scores."
                ),
                user_prompt_template=(
                    "Candidate metadata JSON:\n{candidate_json}\n\n"
                    "Produce a concise explanation with fit, trade-offs, when-not-to-use."
                ),
            ),
            LLMTask.ONBOARDING_GUIDANCE: PromptTemplate(
                prompt_id="onboarding_guidance",
                purpose="Enrich onboarding task guidance with examples/tips.",
                version="1.0",
                expected_schema="OnboardingGuidanceOutput",
                fallback_notes="Keep static hints if generation fails.",
                system_prompt="Generate practical onboarding task guidance grounded in supplied task metadata.",
                user_prompt_template=(
                    "Task JSON:\n{task_json}\n\n"
                    "Current static suggestions:\n{suggestions_json}\n\n"
                    "Return enriched concise suggestions and an improved example placeholder."
                ),
            ),
        }

    def get(self, task: LLMTask) -> PromptTemplate:
        return self._prompts[task]

    def render(self, task: LLMTask, values: dict[str, Any]) -> tuple[PromptTemplate, str]:
        prompt = self.get(task)
        return prompt, prompt.user_prompt_template.format(**values)
