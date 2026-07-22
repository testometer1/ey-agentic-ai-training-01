"""
The nodes that turn the agents' findings into a DECISION.
---------------------------------------------------------
The lending rule is plain code (so the decision is auditable); borderline cases
pause at the human gate.
"""
from langgraph.types import interrupt                     # lets the graph pause and wait for a person


def lending_rule(cibil: int, ratio: float, fraud_flag: str) -> str:   # the yes/no/maybe rule, in plain code
    """The final decision rule (plain code, so it is always auditable)."""
    if cibil >= 750 and ratio <= 0.40 and fraud_flag == "clear":   # strong on all three?
        return "approve"                                 # good enough to auto-approve
    if cibil < 650 or ratio > 0.50 or fraud_flag == "suspicious":   # weak on any one?
        return "decline"                                 # bad enough to auto-decline
    return "refer"                                           # anything in between → a human decides


def supervisor(state):                                       # the Chief Underwriter rules on the findings
    decision = lending_rule(state["cibil"], state["ratio"], state["fraud_flag"])   # apply the rule to the facts
    reason = f"CIBIL {state['cibil']} · EMI/income {state['ratio']} · fraud {state['fraud_flag']} → {decision}"   # a short human-readable why
    return {"recommendation": decision, "rationale": reason}   # save the recommendation + reason


def route(state) -> str:                                     # where to go after the ruling
    if state["recommendation"] == "refer":               # a borderline case?
        return "human_gate"                                  # borderline → ask a person
    return "auto_decide"                                     # clear → decide automatically


def auto_decide(state):                                  # finish a clear-cut case with no human
    approved = state["recommendation"] == "approve"      # was the recommendation "approve"?
    return {"decision": "APPROVED" if approved else "DECLINED"}   # turn it into the final decision


def human_gate(state):                                       # borderline: pause and let a person decide
    answer = interrupt({                                 # pause here; the UI sends back the human's choice
        "recommendation": state["recommendation"],
        "rationale": state["rationale"],
        "summary": f"{state['name']} · CIBIL {state['cibil']} · EMI/income {state['ratio']}",
    })
    approved = str(answer).startswith("approve")         # did the human approve?
    return {"decision": "APPROVED" if approved else "DECLINED"}   # record their final decision
