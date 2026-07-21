import os
from dotenv import load_dotenv
from pydantic import SecretStr

import json
from pathlib import Path
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

load_dotenv()
EMBEDDING_MODEL = os.environ.get("EMBEB_MODEL", "openai/text-embedding-3-small")
embeddings = OpenAIEmbeddings(
    model=EMBEDDING_MODEL, 
    base_url="https://openrouter.ai/api/v1",
    api_key=SecretStr(os.environ["OPENROUTER_API_KEY"]),
    check_embedding_ctx_length=False,
)

KB = Path(__file__).resolve().parents[1] / "data" / "meridian_kb.json" 
CHROMA_DIR = str(Path(__file__).with_name("rag_chroma_db"))

def load_and_chunk() -> list[Document]:
    entries = json.loads(KB.read_text())["documents"]
    base_docs = [
        Document(page_content=e["text"],
                 metadata={"id": e["id"], "category": e["category"], "title": e["title"]})
        for e in entries
    ]

    splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
    chunks = splitter.split_documents(base_docs)
    return chunks

def build_strore() -> Chroma:
    chunks = load_and_chunk()
    print(f"{len(chunks)} chunks created from {KB}")
    store = Chroma(
        collection_name="meridian_rag",
        embedding_function=embeddings,
        persist_directory=CHROMA_DIR)
    if not store.get()["ids"]:
        store.add_documents(chunks)
        print("ingested chunks into Chroma store")
    else:
        print("Chroma store already has data, skipping ingestion")
    return store

if __name__ == "__main__":
    store = build_strore()
    for d in store.similarity_search("home loan documents", k=2):
        print(f" [{d.metadata['id']}] {d.page_content[:100]}...")

