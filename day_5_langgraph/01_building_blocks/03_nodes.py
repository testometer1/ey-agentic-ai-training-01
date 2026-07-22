# What is node in langgraph?
# A node in langgraph is a fundamental building block that
# represents a specific operation or computation within a graph.
# It encapsulates a function or a set of instructions that can be
# executed to process data and produce an output. Nodes can be connected
# to form a directed graph, allowing for the flow of information and the
# execution of complex workflows.

import os
from typing import TypedDict, NotRequired, Literal, cast
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END

load_dotenv()
model = init_chat_model(
    os.environ.get("MODEL", "google/gemini-3.1-flash-lite"),
    model_provider="openrouter",
    temperature=0,
)

class App(TypedDict):
    message: str
    intent: NotRequired[str]
    reply: NotRequired[str]

class Intent(BaseModel):
    intent: Literal["apply", "complain", "enquire"]

def classify(state):
    result = cast(Intent, model.with_structured_output(Intent).invoke(
        "Classify the customer's intent: " + state["message"]
    ))
    return {"intent": result.intent}

def respond(state):
    replies = {
        "apply": "Starting your application process.",
        "complain": "Logging your complaint. We will get back to you shortly.",
        "enquire": "Here is the information you requested.",
    }
    return {"reply": replies[state["intent"]]}

b = StateGraph(App)
b.add_node("classify", classify)
b.add_node("respond", respond)
b.add_edge(START, "classify")
b.add_edge("classify", "respond")
b.add_edge("respond", END)
graph = b.compile()

print(graph.invoke({'message': "I want to open a home loan account."}))