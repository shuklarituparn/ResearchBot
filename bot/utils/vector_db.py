from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma


async def save_to_chroma(chunks, chromadb):
    db = Chroma.from_documents(
        chunks, OllamaEmbeddings(model="llama3"), persist_directory=chromadb
    )
    db.persist()
    print(f"Saved {len(chunks)} chunks to {chromadb}.")