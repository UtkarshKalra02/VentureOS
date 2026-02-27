from pydantic import BaseModel
from typing import Optional, Dict


class StartupState(BaseModel):
    idea: str

    validation: Optional[Dict] = None
    product_plan: Optional[Dict] = None
    pitch: Optional[Dict] = None
    vc_decision: Optional[Dict] = None

    pivot_reason: Optional[str] = None
    cycle_count: int = 0

    # NEW FINANCIAL STATE
    cash_balance: int = 250000  # seed funding