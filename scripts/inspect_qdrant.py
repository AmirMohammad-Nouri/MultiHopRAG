# scripts/inspect_qdrant.py
from qdrant_client import QdrantClient
from llm import embed

client = QdrantClient(url="http://localhost:6333")

info = client.get_collection("chunks")
print("Total points stored:", info.points_count)

print("\nSample stored points:")
results, _ = client.scroll(collection_name="chunks", limit=5, with_payload=True, with_vectors=False)
for point in results:
    print(" -", point.payload.get("title"), "|", point.payload.get("text", "")[:80], "...")

print("\nTest search:")
query_vec = embed("What does the A1C test measure?")
hits = client.search(collection_name="chunks", query_vector=query_vec, limit=3)
for h in hits:
    print(f"  score={h.score:.3f} | {h.payload['title']} | {h.payload['text'][:80]}...")