"""Tools for the Policy Officer agent — a RAG search over the lending policy."""
import json                                               # to read the policy file (JSON text → Python)
from pathlib import Path                                  # a tidy way to build file paths
from langchain.tools import tool                          # marks a function as an agent tool
from langchain_core.vectorstores import InMemoryVectorStore   # a tiny in-memory search store (no DB)
from langchain_core.documents import Document             # wraps a piece of text so it can be searched
from config import embeddings                             # the shared text→vector maker

# data/ lives one level up from this tools/ folder
POLICIES = json.loads((Path(__file__).parent.parent / "data" / "lending_policy.json").read_text())["policies"]   # load the policy clauses
_store = None                                             # will hold the search store once it is built


def policy_store() -> InMemoryVectorStore:             # build the policy search store once, then reuse
    global _store                                        # use the one shared store variable above
    if _store is None:                                   # not built yet?
        _store = InMemoryVectorStore(embeddings)         # make an empty searchable store
        _store.add_documents([Document(page_content=p["text"], metadata={"id": p["id"]}) for p in POLICIES])   # load every clause into it
    return _store                                        # give back the ready store


@tool                                                    # turn the function below into an agent tool
def search_lending_policy(query: str) -> str:            # find the policy clauses that match a question
    """Search Meridian Bank's lending policy; returns relevant clauses with their ids."""
    docs = policy_store().similarity_search(query, k=2)  # find the 2 closest clauses
    return "\n".join(f"[{d.metadata['id']}] {d.page_content}" for d in docs)   # return them as "[id] text" lines
