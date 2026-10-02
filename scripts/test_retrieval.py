# scripts/test_retrieval.py
from retrieval.hybrid_retriever import hybrid_retrieve
from synthesis.answer import synthesize

question = "What treatments are used for conditions that the A1C test diagnoses?"
result = hybrid_retrieve(question)

print("Vector hits:", len(result["chunks"]))
print("Graph paths:", len(result["graph_paths"]))

answer = synthesize(question, result)
print("\nAnswer:", answer)