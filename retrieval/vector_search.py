# retrieval/vector_search.py
from qdrant_client import QdrantClient
from llm import embed

client = QdrantClient(url="http://localhost:6333")

def vector_search(query, top_k=5):
    result = client.query_points(
        collection_name="chunks",
        query=embed(query),
        limit=top_k
    )
    return [(point.payload["text"], point.score) for point in result.points]