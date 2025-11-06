from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from typing import List, Dict
from core.configuration import settings
import uuid


def get_qdrant_client(host: str = None, port: int = None):
    host = host or settings.QDRANT_HOST
    port = port or settings.QDRANT_PORT
    return QdrantClient(host=host, port=port)


def ensure_collection(client: QdrantClient, collection_name: str, vector_size: int = 384):
    existing = [c.name for c in client.get_collections().collections]
    if collection_name not in existing:
        print(f"Creating Qdrant collection '{collection_name}' (size={vector_size})")
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
        )
    else:
        print(f"Collection '{collection_name}' already exists ")

def init_qdrant_collection(
    collection_name: str = "documents",
    vector_size: int = 384,
    qdrant_host: str = None,
    qdrant_port: int = None
):

    client = get_qdrant_client(host=qdrant_host, port=qdrant_port)
    ensure_collection(client, collection_name, vector_size)
    return client


def store_embeddings(chunks: List[Dict], embeddings: List, doc_id: str, collection_name: str = "documents"):
    client = get_qdrant_client()
    ensure_collection(client, collection_name, vector_size=len(embeddings[0]))

    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=embedding,
            payload={
                "document_id": doc_id,
                "chunk_index": chunk['chunk_index'],
                "text": chunk['text'],
                "strategy": chunk['strategy'],
                "char_count": chunk['char_count']
            }
        )
        for chunk, embedding in zip(chunks, embeddings)
    ]
    client.upsert(collection_name=collection_name, points=points)
    print(f"Stored {len(points)} embeddings in '{collection_name}'")


def search_similar_chunks(query_embedding, top_k: int = 5, collection_name: str = "documents") -> List[Dict]:
    client = get_qdrant_client()
    results = client.search(collection_name=collection_name, query_vector=query_embedding.tolist(), limit=top_k)

    return [
        {
            "id": r.id,
            "score": r.score,
            "text": r.payload["text"],
            "document_id": r.payload["document_id"],
            "chunk_index": r.payload["chunk_index"]
        }
        for r in results
    ]
