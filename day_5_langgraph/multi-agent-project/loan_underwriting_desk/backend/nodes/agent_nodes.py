"""
The nodes that RUN each specialist agent.
-----------------------------------------
The fiddly bits — running an agent, listing its tool calls, the fraud rule — are
the small helpers at the top, so each NODE below reads like plain English.
"""
from calc import monthly_emi                             # the EMI maths helper
from agents.credit_analyst import credit_analyst         # agent 1
from agents.policy_officer import policy_officer         # agent 2
from agents.fraud_investigator import fraud_investigator  # agent 3
from tools.fraud_tools import WATCHLIST                  # the shared fraud name list


# ----- small helpers (the "how") -----

def brief(state) -> str:                                 # write a plain-English summary of the applicant
    """The one-line application summary every agent is asked to judge."""
    return (f"Applicant {state['name']}: CIBIL {state['cibil']}, "   # glue the facts into one sentence
            f"income {state['income']:.0f}/month, wants a {state['purpose']} "
            f"loan of {state['amount']:.0f} over {state['tenure']} years.")


def list_tool_calls(messages) -> list:                   # collect every tool the agent used, for the UI
    """List the tools an agent used, so the UI can show its working."""
    steps = []                                           # start an empty list to fill
    for m in messages:                                   # look at every message the agent produced
        for call in getattr(m, "tool_calls", None) or []:    # the agent asked to use a tool
            steps.append(f"🔧 {call['name']}({call['args']})")   # note the tool name + its inputs
        if getattr(m, "type", "") == "tool":                 # a tool returned a result
            steps.append(f"↳ {str(m.content)[:90]}")         # note the (trimmed) result
    return steps                                         # hand back the list of steps


def run_agent(agent, state):                             # run one agent and read its answer
    """Run one agent on the application; return its verdict text + the tools it used."""
    result = agent.invoke({"messages": [{"role": "user", "content": brief(state)}]})   # ask the agent about this applicant
    messages = result["messages"]                        # every message it produced
    verdict = messages[-1].content                           # the agent's final written answer
    return verdict, list_tool_calls(messages)            # give back the answer + the tools it used


def check_fraud(state) -> str:                           # a hard code rule for the fraud flag
    """A hard rule: suspicious if the loan dwarfs the income, or the name is watchlisted."""
    too_big = state["amount"] > 60 * state["income"]     # loan bigger than 60 months of income?
    watchlisted = state["name"].strip().lower() in WATCHLIST   # name on the watchlist?
    return "suspicious" if (too_big or watchlisted) else "clear"   # either one makes it suspicious


# ----- the agent nodes (the "what") -----

def credit_node(state):                                      # AGENT 1 · Credit Analyst
    verdict, tools = run_agent(credit_analyst, state)    # let the Credit Analyst reason
    emi = monthly_emi(state["amount"], 9.0, state["tenure"])   # work out the EMI (code, not the AI)
    ratio = round(emi / state["income"], 2)              # what fraction of income the EMI takes
    return {"emi": emi, "ratio": ratio, "credit": verdict, "credit_trace": tools}   # save these into the state


def policy_node(state):                                      # AGENT 2 · Policy Officer
    verdict, tools = run_agent(policy_officer, state)    # let the Policy Officer check compliance
    return {"policy": verdict, "policy_trace": tools}    # save its finding + tool trace


def fraud_node(state):                                       # AGENT 3 · Fraud Investigator
    verdict, tools = run_agent(fraud_investigator, state)   # let the Fraud Investigator look for red flags
    return {"fraud_flag": check_fraud(state), "fraud": verdict, "fraud_trace": tools}   # save the flag + finding
