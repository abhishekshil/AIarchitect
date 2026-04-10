"""Short architecture hints inlined into generated client code."""


def pattern_hint(pattern: str) -> str:
    return {
        "single_llm": "Direct model output; citations usually empty.",
        "rag": "Grounded answers; parse citations[] for sources.",
        "structured": "Prefer structured_output for machine-readable fields.",
        "hybrid": "Expect validator + agent traces and optional citations.",
    }.get(pattern, "See example_response for this graph shape.")
