from pydantic import BaseModel, ValidationError
from agents.llm import call_gemini
import json
import re


class PivotOutput(BaseModel):
    pivot_strategy: str
    new_positioning: str
    reasoning: str


def extract_json(text: str) -> str:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)
    raise ValueError("No JSON found in response")


def pivot_agent(state):
    prompt = f"""
You are a strategic turnaround consultant.

The startup was rejected by a VC.

Original Idea:
{state.idea}

VC Concerns:
{state.vc_decision['key_concerns']}

Design a realistic pivot strategy.

The pivot must:
- Address at least two VC concerns
- Modify target market OR pricing OR product focus
- Remain logically feasible

Return STRICT JSON:
{{
  "pivot_strategy": "...",
  "new_positioning": "...",
  "reasoning": "..."
}}
"""

    raw = call_gemini(prompt)

    try:
        json_str = extract_json(raw)
        parsed = json.loads(json_str)
        validated = PivotOutput(**parsed)

        state.pivot_reason = validated.reasoning
        state.idea = validated.new_positioning
        state.cycle_count += 1

    except (ValidationError, ValueError, json.JSONDecodeError):
        state.cycle_count += 1
        state.pivot_reason = "Fallback pivot applied"
        state.idea = state.idea + " (Refocused niche positioning)"

    return state