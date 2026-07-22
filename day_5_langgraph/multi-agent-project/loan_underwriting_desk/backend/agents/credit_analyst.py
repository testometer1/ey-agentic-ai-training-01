"""AGENT 1 · Credit Analyst — assesses creditworthiness."""
from langchain.agents import create_agent              # builds a REAL agent (role + tools + ReAct loop)
from config import model                               # the shared AI brain
from tools.credit_tools import calculate_emi, emi_to_income_ratio   # the two tools this agent may use

credit_analyst = create_agent(model, tools=[calculate_emi, emi_to_income_ratio],   # build the agent with its tools
    system_prompt=("You are a Credit Analyst. Use calculate_emi (assume 9% p.a.) then emi_to_income_ratio, "
                   "and judge creditworthiness against the CIBIL score. Finish with 'VERDICT: low/medium/high risk'."))
