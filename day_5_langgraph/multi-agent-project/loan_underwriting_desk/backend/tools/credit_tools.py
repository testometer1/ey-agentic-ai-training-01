"""Tools for the Credit Analyst agent — the credit maths."""
from langchain.tools import tool                          # marks a function as a tool an agent can call
from calc import monthly_emi                              # the shared EMI formula


@tool                                                    # turn the function below into an agent tool
def calculate_emi(principal: float, annual_rate: float, years: int) -> dict:   # work out the monthly EMI
    """Monthly EMI for a loan. principal in rupees, annual_rate percent, years whole."""
    return {"emi": monthly_emi(principal, annual_rate, years)}   # hand the number back to the agent


@tool                                                    # turn the function below into an agent tool
def emi_to_income_ratio(emi: float, monthly_income: float) -> dict:   # EMI as a share of income
    """What fraction of monthly income the EMI uses (0.4 means 40%)."""
    return {"ratio": round(emi / monthly_income, 2)}      # e.g. 0.4 means the EMI eats 40% of income
