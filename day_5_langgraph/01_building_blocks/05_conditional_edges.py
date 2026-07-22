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

class S(TypedDict):
    message: str
    reply: NotRequired[str]

class Desk(BaseModel):
    desk: Literal["loans", "cards", "fraud"]

def route(state):
    choice = cast(Desk, model.with_structured_output(Desk).invoke(
        "Which desk should handle this message:\n" + state["message"]
    ))
    return choice.desk

def loans(state):
    return {"reply": "[loan desk] happy to help you with your loan application."}

def cards(state):
    return {"reply": "[card desk] let's assist you with your card-related query."}

def fraud(state):
    return {"reply": "[fraud desk] we'll secure your account and investigate the issue."}

b = StateGraph(S)
b.add_node("loans", loans)
b.add_node("cards", cards)
b.add_node("fraud", fraud)
b.add_conditional_edges(START, route, ["loans", "cards", "fraud"])
b.add_edge("loans", END)
b.add_edge("cards", END)
b.add_edge("fraud", END)
graph = b.compile()

for msg in ["I want to apply for a home loan.", "I lost my credit card.", "I think my account has been compromised."]:
    print(msg, "-> ", graph.invoke({"message": msg})["reply"])