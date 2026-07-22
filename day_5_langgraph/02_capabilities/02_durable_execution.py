# what is durable execution?
# Durable execution in langgraph refers to the ability of a graph to maintain
# its state and progress even in the face of interruptions or failures. This means that if a graph execution is paused, stopped, or encounters an error, it can be resumed from the last known state without losing any data or progress. Durable execution is particularly useful in long-running processes, workflows, or tasks that require reliability and fault tolerance.

from typing import TypedDict, Annotated
from operator import add
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig

class S(TypedDict):
    done: Annotated[list, add] # 'add' is a reducer -> new items appended to the list

def step_a(state):
    return {"done": ["A"]}

def step_b(state):
    return {"done": ["B"]}

b = StateGraph(S)
b.add_node("step_a", step_a)
b.add_node("step_b", step_b)
b.add_edge(START, "step_a")
b.add_edge("step_a", "step_b")
b.add_edge("step_b", END)
graph = b.compile(checkpointer=InMemorySaver())

cfg: RunnableConfig = {"configurable": {"thread_id": "loan-42"}}
graph.invoke({"done": []}, cfg, durablility="sync")
print("state read back from the checkpoint:", graph.get_state(cfg).values["done"])