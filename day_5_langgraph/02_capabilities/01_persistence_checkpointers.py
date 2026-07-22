import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import RunnableConfig

load_dotenv()
model = init_chat_model(
    os.environ.get("MODEL", "google/gemini-3.1-flash-lite"),
    model_provider="openrouter",
    temperature=0,
)

def chat(state):
    return {"messages": [model.invoke(state["messages"])]}

b = StateGraph(MessagesState)
b.add_node("chat", chat)
b.add_edge(START, "chat")
b.add_edge("chat", END)
graph = b.compile(checkpointer=InMemorySaver())

alice: RunnableConfig = {"configurable": {"thread_id": "alice"}}
graph.invoke({"messages": [HumanMessage("Hi, my name is Alice.")]}, alice)
answer = graph.invoke({"messages": [HumanMessage("What is my name?")]}, alice)
print("same thread:", answer["messages"][-1].content)

stranger: RunnableConfig = {"configurable": {"thread_id": "stranger"}}
fresh = graph.invoke({"messages": [HumanMessage("What is my name?")]}, stranger)
print("new thread:", fresh["messages"][-1].content)