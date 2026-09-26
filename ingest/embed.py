# ingest/embed.py
import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from llm import embed

client = QdrantClient(url="http://localhost:6333")
client.recreate_collection("chunks", vectors_config=VectorParams(size=768, distance=Distance.COSINE))

NAMESPACE = uuid.NAMESPACE_DNS  # any fixed namespace works, just stay consistent

def make_point_id(string_id: str) -> str:
    return str(uuid.uuid5(NAMESPACE, string_id))

def embed_and_store(chunks, doc_id):
    points = []
    for i, c in enumerate(chunks):
        text = c["text"]
        if not text or not text.strip():
            print(f"[WARN] skipping empty chunk {doc_id}_{i}")
            continue

        chunk_str_id = f"{doc_id}_{i}"
        points.append(PointStruct(
            id=make_point_id(chunk_str_id),
            vector=embed(text),
            payload={**c, "chunk_idx": i, "chunk_id": chunk_str_id}  # keep readable id in payload
        ))
    client.upsert("chunks", points)