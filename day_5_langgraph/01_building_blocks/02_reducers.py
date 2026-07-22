# what is a reducer in programming?
# A reducer is a function that takes an input (often an array or collection of data)
# and processes it to produce a single output value. It "reduces" the input data into
# a more concise form, often by applying a specific operation or transformation.
# Reducers are commonly used in functional programming and data processing tasks,
# such as aggregating values, filtering data, or transforming collections.

from typing import TypedDict, Annotated
from operator import add
from langgraph.graph import StateGraph, START, END

class S(TypedDict):
    audit: Annotated[list, add] # 'add' is a reducer -> new items appended to the list
    status: str                 # no reducer -> new value overwrites the old value

def receive(state):
    return {"audit": ["received"], "status": "in_review"}

def decide(state):
    return {"audit": ["approved"], "status": "approved"}

b = StateGraph(S)
b.add_node("receive", receive)
b.add_node("decide", decide)
b.add_edge(START, "receive")
b.add_edge("receive", "decide")
b.add_edge("decide", END)
graph = b.compile()

print(graph.invoke({"audit": ["created"], "status": "new"}))