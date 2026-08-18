"""Vector index building and retrieval utilities."""
import chromadb
from langchain_chroma import Chroma
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings

import config


def build_index(chunks: list, collection_name: str | None = None) -> Chroma:
    if collection_name is None:
        collection_name = config.COLLECTION_NAME

    client = chromadb.Client()
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass

    embedding_model = FastEmbedEmbeddings(model_name=config.EMBEDDING_MODEL)
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_model,
        collection_name=collection_name,
        collection_metadata={"hnsw:space": "cosine"},
    )
    return vectorstore


def retrieve(vectorstore: Chroma, question: str, k: int | None = None):
    if k is None:
        k = config.TOP_K
    return vectorstore.similarity_search_with_relevance_scores(question, k=k)
