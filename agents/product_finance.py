from pydantic import BaseModel, ValidationError
from agents.llm import call_gemini
import json
import re


class ProductFinanceOutput(BaseModel):
    core_features: list[str]
    mvp_scope: list[str]
    monetization_model: str
    estimated_monthly_burn: int
    estimated_runway_months: int
    scalability_risks: list[str]


def extract_json(text: str) -> str:
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)
    raise ValueError("No JSON found in response")


def product_finance_agent(state):
    validation_data = state.validation

    prompt = f"""
You are both a Product Manager and CFO.

The startup idea:
{state.idea}

Validation results:
{validation_data}

Based on the validation confidence score, design:

1. Core product features
2. MVP scope (must be realistic for early-stage)
3. Monetization model
4. Estimated monthly burn (integer USD)
5. Estimated runway in months (assume $250,000 seed funding)
6. Scalability risks

Return STRICT JSON only in this format:

{{
  "core_features": ["...", "..."],
  "mvp_scope": ["...", "..."],
  "monetization_model": "...",
  "estimated_monthly_burn": 0,
  "estimated_runway_months": 0,
  "scalability_risks": ["...", "..."]
}}
"""

    raw = call_gemini(prompt)

    try:
        json_str = extract_json(raw)
        parsed = json.loads(json_str)
        validated = ProductFinanceOutput(**parsed)
        state.product_plan = validated.model_dump()
    except (ValidationError, ValueError, json.JSONDecodeError) as e:
        print("ProductFinance parsing error:", e)
        state.product_plan = {
            "core_features": [],
            "mvp_scope": [],
            "monetization_model": "Unknown",
            "estimated_monthly_burn": 50000,
            "estimated_runway_months": 5,
            "scalability_risks": []
        }

    return state