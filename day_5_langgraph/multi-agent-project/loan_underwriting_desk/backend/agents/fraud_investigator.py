"""AGENT 3 · Fraud Investigator — hunts for red flags."""
from langchain.agents import create_agent              # builds a REAL agent (role + tools + ReAct loop)
from config import model                               # the shared AI brain
from tools.fraud_tools import income_multiple, check_watchlist   # the two tools this agent may use

fraud_investigator = create_agent(model, tools=[income_multiple, check_watchlist],   # build the agent with its tools
    system_prompt=("You are a Fraud Investigator. Use income_multiple and check_watchlist. A multiple over 60 or a "
                   "watchlist hit is suspicious. Finish with 'VERDICT: clear' or 'VERDICT: suspicious'."))
