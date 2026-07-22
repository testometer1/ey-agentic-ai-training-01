"""
The graph — wires the nodes together into one runnable workflow.
----------------------------------------------------------------
This file is now tiny on purpose: the tools, agents and node logic each live in
their own file. Here we just connect them.

  START → credit_node → policy_node → fraud_node → supervisor
                                                       │
                              approve/decline ─────────┤───── refer
                                    │                          │
                               auto_decide                 human_gate  → (pause for a person)
                                    └────────────┬─────────────┘
                                               END
"""
from langgraph.graph import StateGraph, START, END       # the graph builder + start/end markers
from langgraph.checkpoint.memory import InMemorySaver     # remembers a paused run so it can resume
from state import LoanState                               # the shape of the data flowing through
from nodes import (credit_node, policy_node, fraud_node,  # bring in all six workflow steps
                   supervisor, route, auto_decide, human_gate)


def build_graph():                                      # add the nodes, connect the edges, compile
    b = StateGraph(LoanState)                           # a new empty graph that carries LoanState
    for name, fn in [("credit_node", credit_node), ("policy_node", policy_node), ("fraud_node", fraud_node),   # register each node under a name
                     ("supervisor", supervisor), ("auto_decide", auto_decide), ("human_gate", human_gate)]:
        b.add_node(name, fn)                            # add one node to the graph
    b.add_edge(START, "credit_node"); b.add_edge("credit_node", "policy_node")   # run the specialists in turn
    b.add_edge("policy_node", "fraud_node"); b.add_edge("fraud_node", "supervisor")   # ...then hand to the supervisor
    b.add_conditional_edges("supervisor", route, ["auto_decide", "human_gate"])   # branch on the recommendation
    b.add_edge("auto_decide", END); b.add_edge("human_gate", END)   # both endings finish the graph
    return b.compile(checkpointer=InMemorySaver())      # the checkpointer lets the human pause resume
