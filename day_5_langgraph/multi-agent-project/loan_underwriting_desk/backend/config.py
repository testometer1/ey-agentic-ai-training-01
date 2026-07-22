"""
Shared setup — loaded once and reused by every agent.
-----------------------------------------------------
The AI model (for the agents' reasoning) and the embeddings (for the Policy
Officer's RAG search). Reading these from .env in ONE place keeps the rest tidy.
"""
import os                                              # lets us read settings from the computer / .env
from pydantic import SecretStr                         # a safe wrapper that hides a secret key
from langchain.chat_models import init_chat_model      # switches on an AI chat model
from langchain_openai import OpenAIEmbeddings          # turns text into vectors (for policy search)
from dotenv import load_dotenv                         # helper that loads the .env file

load_dotenv()                                          # read OPENROUTER_API_KEY etc. from .env
MODEL = os.environ.get("MODEL", "openai/gpt-4o-mini")  # which AI brain; change once in .env
model = init_chat_model(MODEL, model_provider="openrouter", temperature=0)   # 0 = steady answers

embeddings = OpenAIEmbeddings(                          # the vector maker for the policy RAG
    model=os.environ.get("EMBEDDING_MODEL", "openai/text-embedding-3-small"),
    base_url="https://openrouter.ai/api/v1",
    api_key=SecretStr(os.environ["OPENROUTER_API_KEY"]), check_embedding_ctx_length=False)
