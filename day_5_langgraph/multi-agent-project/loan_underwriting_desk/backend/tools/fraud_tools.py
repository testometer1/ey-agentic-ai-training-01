"""Tools for the Fraud Investigator agent + the shared watchlist."""
from langchain.tools import tool                          # marks a function as an agent tool

WATCHLIST = {"john doe", "acme shell ltd"}             # a tiny mock fraud watchlist


@tool                                                    # turn the function below into an agent tool
def income_multiple(loan_amount: float, monthly_income: float) -> dict:   # loan size vs income, as a signal
    """How many months of income the loan equals — a fraud signal."""
    return {"multiple": round(loan_amount / monthly_income, 1)}   # e.g. 80 = loan is 80 months of income


@tool                                                    # turn the function below into an agent tool
def check_watchlist(name: str) -> dict:                  # is this applicant's name flagged?
    """Check whether an applicant's name is on the fraud watchlist."""
    return {"on_watchlist": name.strip().lower() in WATCHLIST}   # True if the (lowercased) name is listed
