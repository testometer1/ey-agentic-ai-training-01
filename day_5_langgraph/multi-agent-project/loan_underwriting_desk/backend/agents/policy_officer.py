"""AGENT 2 · Policy Officer — checks the application against lending policy (RAG)."""
from langchain.agents import create_agent              # builds a REAL agent (role + tools + ReAct loop)
from config import model                               # the shared AI brain
from tools.policy_tools import search_lending_policy   # the RAG search tool this agent may use

policy_officer = create_agent(model, tools=[search_lending_policy],   # build the agent with its one tool
    system_prompt=("You are a Policy Officer. Search the lending policy and decide if the application complies, "
                   "citing policy ids. Finish with 'VERDICT: compliant' or 'VERDICT: not compliant'."))
