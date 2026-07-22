"""
A tiny maths helper — shared by the Credit Analyst's tool and the credit node.
Keeping the formula in code means the numbers are always right, on any model.
"""
def monthly_emi(principal: float, annual_rate: float, years: int) -> float:   # standard EMI formula
    r = annual_rate / 100 / 12          # yearly percent -> plain monthly rate
    n = years * 12                      # total number of monthly payments
    return round(principal * r * (1 + r) ** n / ((1 + r) ** n - 1), 2)   # the monthly payment, rounded
