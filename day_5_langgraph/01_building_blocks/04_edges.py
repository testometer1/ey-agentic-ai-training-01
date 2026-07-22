# What is an edge in langgraph?
# An edge in langgraph is a connection between two nodes that defines the flow of data and
# the order of execution within a graph. It represents a directed relationship between
# the source node (the starting point) and the target node (the endpoint).

from typing import TypedDict, Annotated
from operator import add
from langgraph.graph import StateGraph, START, END

class S(TypedDict):
    steps: Annotated[list, add] # 'add' is a reducer -> new items appended to the list

def intake(state):
    return {"steps": ["intake"]}

def price(state):
    return {"steps": ["price"]}

def notify(state):
    return {"steps": ["notify"]}

b = StateGraph(S)
b.add_node("intake", intake)
b.add_node("price", price)
b.add_node("notify", notify)
b.add_edge(START, "intake")
b.add_edge("intake", "price")
b.add_edge("price", "notify")
b.add_edge("notify", END)
graph = b.compile()

print(graph.invoke({"steps": []})["steps"])