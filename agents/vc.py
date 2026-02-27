from pydantic import BaseModel, ValidationError
from agents.llm import call_gemini
import json
import re


class VCDecision(BaseModel):
    score: int
    funded: bool
    key_concerns: list[str]


def extract_json(text: str) -> str:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)
    raise ValueError("No JSON found in response")


def vc_agent(state):
    prompt = f"""
You are a skeptical venture capitalist.

Evaluate the following startup:

Pitch:
{state.pitch}

Product Plan:
{state.product_plan}

Score it from 0-100.

Fund only if score >= 70.

Return STRICT JSON:
{{
  "score": 0,
  "funded": true/false,
  "key_concerns": ["...", "..."]
}}
"""

    raw = call_gemini(prompt)

    try:
        json_str = extract_json(raw)
        parsed = json.loads(json_str)
        validated = VCDecision(**parsed)

        score = validated.score

        # --- DETERMINISTIC ADJUSTMENTS ---

        burn = state.product_plan.get("estimated_monthly_burn", 0)
        runway = state.product_plan.get("estimated_runway_months", 0)

        # Penalize high burn
        if burn > 40000:
            score -= 10

        # Penalize short runway
        if runway < 6:
            score -= 10

        # Reward long runway
        if runway > 12:
            score += 5

        # Penalize too-narrow TAM
        if "1%" in state.idea.lower():
            score -= 5

        score = max(0, min(100, score))

        funded = score >= 70

        state.vc_decision = {
            "score": score,
            "funded": funded,
            "key_concerns": validated.key_concerns
        }

    except:
        state.vc_decision = {
            "score": 50,
            "funded": False,
            "key_concerns": []
        }

    return state