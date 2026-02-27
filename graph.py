from langgraph.graph import StateGraph, END
from state import StartupState
from agents.validation import validation_agent
from agents.product_finance import product_finance_agent
from agents.pitch import pitch_agent
from agents.vc import vc_agent
from agents.pivot import pivot_agent


def validation_node(state):
    return validation_agent(state)


def product_node(state):
    return product_finance_agent(state)


def pitch_node(state):
    return pitch_agent(state)


def vc_node(state):
    state = vc_agent(state)

    # Deduct one month of burn after full cycle
    if state.product_plan:
        burn = state.product_plan.get("estimated_monthly_burn", 0)
        state.cash_balance -= burn

    return state


def decision_router(state):
    # Bankruptcy check first
    if state.cash_balance <= 0:
        print("Startup ran out of cash.")
        return "end"

    if state.vc_decision["funded"]:
        return "end"

    elif state.cycle_count < 1:
        return "pivot"

    else:
        return "end"


def pivot_node(state):
    return pivot_agent(state)


builder = StateGraph(StartupState)

builder.add_node("validation", validation_node)
builder.add_node("product", product_node)
builder.add_node("pitch", pitch_node)
builder.add_node("vc", vc_node)
builder.add_node("pivot", pivot_node)

builder.set_entry_point("validation")

builder.add_edge("validation", "product")
builder.add_edge("product", "pitch")
builder.add_edge("pitch", "vc")

builder.add_conditional_edges(
    "vc",
    decision_router,
    {
        "pivot": "pivot",
        "end": END,
    },
)

builder.add_edge("pivot", "validation")

graph = builder.compile()