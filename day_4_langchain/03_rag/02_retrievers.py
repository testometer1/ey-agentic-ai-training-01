from importlib import import_module

ingest = import_module("01_ingestion_chunking")
store = ingest.build_strore()

query = "home loan interest and fees"

print("=== Type 1. Similarity (k=3) ===")
sim = store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
for d in sim.invoke(query):
    print(f" [{d.metadata['id']}] {d.page_content[:100]}...")

print("\n=== Type 2. Maximal Marginal Relevance (MMR) (k=3, diverse) ===")
mmr = store.as_retriever(search_type="mmr", search_kwargs={"k": 3, "fetch_k": 10})
for d in mmr.invoke(query):
    print(f" [{d.metadata['id']}] {d.page_content[:100]}...")

print("\n=== Type 3. Metadata-Filtered (category = credit card) ===")
filtered = store.as_retriever(search_kwargs={"k": 2, "filter": {"category": "credit_card"}})
for d in filtered.invoke("fee"):
    print(f" [{d.metadata['id']}] {d.page_content[:100]}...")