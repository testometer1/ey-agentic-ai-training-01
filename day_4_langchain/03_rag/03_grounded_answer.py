import os
from importlib import import_module
from langchain.chat_models import init_chat_model
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()
MODEL = os.environ.get("MODEL", "gpt-4o-mini")
ingest = import_module("01_ingestion_chunking")
store = ingest.build_strore()
model = init_chat_model(MODEL, model_provider="openrouter", temperature=0.0)

GROUNDED_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are Meridian Bank's assistant. Answers questions USING ONLY the context below."
     "cite the source ID in square brackets after each fact, example: [hl-001]."
     "if the context does not contain the answer reply exactly:"
     "\"I don't have that in our policy I'll escalate to a human.\""
     "Do not use outside knowledge.\n\n"
     "CONTEXT:\n{context}\n\n"),
     ("user", "{question}")
    ]
)

def format_context(docs) -> str:
    return "n".join(f" [{d.metadata['id']}] {d.page_content}" for d in docs)

def answer(question: str) -> str:
    docs = store.similarity_search(question, k=3)
    chain = GROUNDED_PROMPT | model
    return chain.invoke({"context": format_context(docs), "question": question}).text

# In-policy quesiton -> cited answer
print("Q: what documents do I need for a home loan?")
print("A:", answer("what documents do I need for a home loan?"), "\n")

# Out-of-policy question -> fallback answer
print("Q: what is the interest rate on a car loan?")
print("A:", answer("what is the interest rate on a car loan?"))