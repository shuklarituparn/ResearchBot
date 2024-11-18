import os

from langchain_community.embeddings import OllamaEmbeddings, GigaChatEmbeddings
from langchain_community.vectorstores import Chroma

from bot.utils.audio_summarizer import GIGACHAD_CREDENTIALS


async def save_to_chroma(chunks, chromadb):
    GIGACHAT_SCOPE= os.getenv("GIGACHAT_SCOPE")
    db = Chroma.from_documents(
        chunks, GigaChatEmbeddings(credentials=GIGACHAD_CREDENTIALS, scope=GIGACHAT_SCOPE, verify_ssl_certs=False), persist_directory=chromadb
    )
    db.persist()
    print(f"Saved {len(chunks)} chunks to {chromadb}.")