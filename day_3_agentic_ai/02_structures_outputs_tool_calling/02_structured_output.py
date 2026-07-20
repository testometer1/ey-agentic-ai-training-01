import os
from openai import OpenAI
from pydantic import BaseModel, Field # tools for describing structured outputs
from dotenv import load_dotenv

load_dotenv() # reads the .env file and loads the environment variables

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.environ["OPENROUTER_API_KEY"]
)
MODEL = os.environ.get("MODEL", "openai/gpt-oss-120b") # The model to use for the API call

# 1. Declare the exact shape you want back from the model using Pydantic models
class LoadEnquiry(BaseModel):
    intent: str = Field(description="e.g. apply, enquire, complain")
    product: str
    amount: float | None = Field(default=None, description="loana amount if stated, else null")
    tenure_years: int | None = None
    application_name: str | None = None

message = ("Hi, I am Vaibhav Suryavanshi. I'd like to apply for a home loan of 50 lakhs for 20 years. ")

# 2. Ask for structured output from the model using the parse method, which will validate the output against the Pydantic model
completion = client.beta.chat.completions.parse(
    model=MODEL,
    messages=[{"role": "system", "content": "Extract the loan inquiry into the given schema. "
                                            "use now for anything not stated. Amount in rupees "
                                            "(e.g. 50 lakhs = 5000000). Return only the JSON object, no other text."},
              {"role": "user", "content": message}
               ],
    response_format=LoadEnquiry,
)

# 3. The output is now a Pydantic model instance, which you can access like a normal Python object
inquiry = completion.choices[0].message.parsed
if inquiry is None:
    raise RuntimeError("Failed to parse the model output into the LoadEnquiry schema.")
print("parsed object: ", inquiry)
print("product      : ", inquiry.product)
print("amount       : ", inquiry.amount)
print("as JSON      : ", inquiry.model_dump_json(indent=2))