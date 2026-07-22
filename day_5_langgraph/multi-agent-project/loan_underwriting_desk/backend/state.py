"""
LoanState — the shared 'folder' of data that flows through the graph.
Every node reads it and returns a small update that merges back in.
"""
from typing import TypedDict, NotRequired   # tools for describing the shape of our data


class LoanState(TypedDict):
    # --- the application (filled in by the form, always present) ---
    name: str                          # the applicant's name
    income: float                      # monthly income
    cibil: int                         # credit score
    amount: float                      # loan amount requested
    tenure: int                        # loan length in years
    purpose: str                       # what the loan is for

    # --- facts worked out in code (added by the nodes) ---
    emi: NotRequired[float]            # the monthly payment
    ratio: NotRequired[float]          # EMI as a fraction of income
    fraud_flag: NotRequired[str]       # "clear" or "suspicious"

    # --- each agent's written finding ---
    credit: NotRequired[str]           # the Credit Analyst's verdict
    policy: NotRequired[str]           # the Policy Officer's verdict
    fraud: NotRequired[str]            # the Fraud Investigator's verdict

    # --- the tools each agent used (for the live UI log) ---
    credit_trace: NotRequired[list]    # Credit Analyst's tool calls
    policy_trace: NotRequired[list]    # Policy Officer's tool calls
    fraud_trace: NotRequired[list]     # Fraud Investigator's tool calls

    # --- the ruling and the final decision ---
    recommendation: NotRequired[str]   # approve / refer / decline (the rule's call)
    rationale: NotRequired[str]        # a short human-readable "why"
    decision: NotRequired[str]         # "APPROVED" or "DECLINED" (the final word)
