from graph import graph
from state import StartupState

initial_state = StartupState(idea="AI fitness app for busy professionals")

result = graph.invoke(initial_state)

print(result)
print("Cash remaining:", result.cash_balance)
print("Final VC Score:", result.vc_decision["score"])