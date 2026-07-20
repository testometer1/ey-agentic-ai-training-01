import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from typing import cast
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionToolParam

load_dotenv()  # Load environment variables from .env file

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"]
)
# MODEL = os.environ.get("MODEL", "openai/gpt-oss-120b")  # The model to use for the API call
MODEL = "openai/gpt-4o-mini"  # The model to use for the API call

# 1. A real python function we want the model to call
def calculate_emi(principal: float, annual_rate: float, years: int) -> dict:
    """Calculate the Equated Monthly Installment (EMI) for a loan."""
    r = annual_rate / 100 / 12  # monthly interest rate
    n = years * 12  # total number of monthly payments
    if r == 0:
        emi = principal / n
    else:
        emi = principal * r * (1 + r) ** n / ((1 + r) ** n - 1) # usual EMI formula
    return {"emi": round(emi, 2), "total_payment": round(emi * n, 2)}

# 2. Describe the tool to the model
tools: list[ChatCompletionToolParam] = [{
    "type": "function",
    "function": {
        "name": "calculate_emi",
        "description": "Calculate the Equated Monthly Installment (EMI) for a loan",
        "parameters": {
            "type": "object",
            "properties": {
                "principal": {"type": "number", "description": "loan amount in rupees"},
                "annual_rate": {"type": "number", "description": "annual interest rate in percentage"},
                "years": {"type": "integer", "description": "loan tenure in years"},
            },
            "required": ["principal", "annual_rate", "years"],
        },
    },
}]

messages: list[ChatCompletionMessageParam] = [
    {"role": "system", "content": "What is the EMI on 50 lakh home loan at 8.4 percentage for 25 years"}]

# 3 First call: the model decides to call the tool
first = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
msg = first.choices[0].message

messages.append(cast(ChatCompletionMessageParam, msg))

if msg.tool_calls:
    for tc in msg.tool_calls:
        if tc.type != "function":
            continue
        args = json.loads(tc.function.arguments)
        print("model wanst to call: ", tc.function.name, "with args: ", args)
        result = calculate_emi(**args)

        # 4. return the result to the model in a new message
        messages.append({
            "role": "tool",
            "tool_call_id": tc.id,
            "content": json.dumps(result)
        })

# 5. Second call: the model now has the tool's output and can respond to the user
final = client.chat.completions.create(model=MODEL, messages=messages, tools=tools)
print("=== Final Response ===")
print(final.choices[0].message.content)