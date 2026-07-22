# what is a state?
# A state is a representation of the current condition or status of a system,
# object, or process at a specific point in time. It encompasses all relevant
# information that defines the system's behavior and characteristics, allowing
# for predictions and decisions based on that information. In programming and
# computer science, a state often refers to the values of variables, data structures,
# or objects that determine how a program operates at any given moment.

# state in langgraph!
# state is one shared box of information that all nodes can read from and write to.
# It is a shared memory space that allows nodes to communicate and share data with each other.
# The state can be used to store information about the current status of the system,
# such as the values of variables, the results of computations, or any other relevant data.
# By using a shared state, nodes can collaborate and coordinate their actions, enabling more
# complex and dynamic behaviors in the system.

from typing import TypedDict, NotRequired
from langgraph.graph import StateGraph, START, END

class LoadState(TypedDict):
    applicant: str
    income: float
    emi: float
    ratio: NotRequired[float]

def compute_ratio(state):
    return {"ratio": round(state["emi"] / state["income"], 2)}

b = StateGraph(LoadState)
b.add_node("compute_ratio", compute_ratio)
b.add_edge(START, "compute_ratio")
b.add_edge("compute_ratio", END)
graph = b.compile()

print(graph.invoke({"applicant": "John", "income": 50000, "emi": 1500}))
