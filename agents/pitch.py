from pydantic import BaseModel, ValidationError
from agents.llm import call_gemini
import json
import re


class PitchOutput(BaseModel):
    slides: list[str]


def extract_json(text: str) -> str:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)
    raise ValueError("No JSON found in response")


def pitch_agent(state):
    prompt = f"""
You are a startup pitch strategist.

Startup Idea:
{state.idea}

Validation:
{state.validation}

Product & Financial Plan:
{state.product_plan}

Create a concise 8-slide investor pitch.

Return STRICT JSON:
{{
  "slides": [
    "Slide 1: ...",
    "Slide 2: ...",
    ...
  ]
}}
"""

    raw = call_gemini(prompt)

    try:
        json_str = extract_json(raw)
        parsed = json.loads(json_str)
        validated = PitchOutput(**parsed)
        state.pitch = validated.model_dump()
    except (ValidationError, ValueError, json.JSONDecodeError):
        state.pitch = {"slides": []}

    return state