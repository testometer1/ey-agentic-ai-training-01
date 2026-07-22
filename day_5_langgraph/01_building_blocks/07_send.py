import os
from typing import TypedDict, Annotated, Literal, cast
from operator import add
from pydantic import BaseModel
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

load_dotenv()
model = init_chat_model(
    os.environ.get("MODEL", "google/gemini-3.1-flash-lite"),
    model_provider="openrouter",
    temperature=0,
) 

class S(TypedDict):
    applicants: str
    results: Annotated[list, add] # every worker adds its verdict here

class Verdict(BaseModel):
    decision: Literal["approve", "review", "decline"]

def dispatch(state):
    return [Send("score_one", a) for a in state["applicants"]]

def score_one(state):
    verdict = cast(Verdict, model.with_structured_output(Verdict).invoke(
        f"Loan verdict for {state['name']}: {state['profile']}"
    ))
    return {"results": [f"{state['name']}: {verdict.decision}"]}

b = StateGraph(S)
b.add_node("score_one", score_one)
b.add_conditional_edges(START, dispatch, ["score_one"])
b.add_edge("score_one", END)
graph = b.compile()

people = [
    {"name": "Sanju", "profile": "Income: 2 lakhs/month, CIBIL Score: 780"},
    {"name": "Shivam", "profile": "Income: 1 lakh/month, CIBIL Score: 650"},
    {"name": "Sachin", "profile": "Income: 3 lakhs/month, CIBIL Score: 720"},
]

print(graph.invoke({"applicants": people, "results": []})["results"])