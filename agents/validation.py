from pydantic import BaseModel, ValidationError
from agents.llm import call_gemini
import json
import re


class ValidationOutput(BaseModel):
    problem_clarity: str
    target_user: str
    market_potential: str
    key_risks: list[str]
    confidence_score: int


def extract_json(text: str) -> str:
    """Extract JSON block from Gemini output."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)
    raise ValueError("No JSON found in response")


def validation_agent(state):
    prompt = f"""
You are a startup validation expert.

Analyze the following startup idea:

{state.idea}

Return STRICT JSON only. No markdown. No explanation.

Format:
{{
  "problem_clarity": "...",
  "target_user": "...",
  "market_potential": "...",
  "key_risks": ["...", "..."],
  "confidence_score": 0-100
}}
"""

    raw = call_gemini(prompt)

    try:
        json_str = extract_json(raw)
        parsed = json.loads(json_str)
        validated = ValidationOutput(**parsed)
        state.validation = validated.model_dump()
    except (ValidationError, ValueError, json.JSONDecodeError) as e:
        print("Validation parsing error:", e)
        state.validation = {
            "problem_clarity": "Parsing failed",
            "target_user": "Unknown",
            "market_potential": "Unknown",
            "key_risks": [],
            "confidence_score": 50
        }

    return state