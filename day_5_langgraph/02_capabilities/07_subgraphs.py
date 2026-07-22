from typing import TypedDict, NotRequired
from langgraph.graph import StateGraph, START, END

class S(TypedDict):
    applicant: str
    kyc_ok: NotRequired[bool]
    decision: NotRequired[str]

def check_id(state):
    return {"kyc_ok": True}

# subgraph
sub = StateGraph(S)
sub.add_node("check_id", check_id)
sub.add_edge(START, "check_id")
sub.add_edge("check_id", END)
kyc = sub.compile()

def decide(state):
    return {"decision": "approved" if state["kyc_ok"] else "rejected"}

# parent graph
parent = StateGraph(S)
parent.add_node("kyc", kyc)
parent.add_node("decide", decide)
parent.add_edge(START, "kyc")
parent.add_edge("kyc", "decide")
parent.add_edge("decide", END)
graph = parent.compile()

print(graph.invoke({"applicant": "Alice"}))