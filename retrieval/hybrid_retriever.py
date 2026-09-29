# retrieval/hybrid_retriever.py
from llm import llm_call
from retrieval.graph_search import graph_expand
from retrieval.vector_search import vector_search

def is_multihop(question):
    prompt = f"""Classify the question as either "multihop" or "single".
    "single" = answerable from one direct fact.
    "multihop" = requires connecting through an intermediate entity (A relates to B, B relates to C).

    Examples:
    Q: "What does the A1C test measure?"
    A: single

    Q: "What treatments exist for conditions that the A1C test diagnoses?"
    A: multihop

Q: "{question}"
A:"""
    raw = llm_call(prompt, temperature=0.0).strip().lower()
    # check the LAST occurrence of either keyword, since the model reasons first then concludes
    if "multihop" in raw:
        return True
    if "single" in raw:
        return False
    return True  # default to attempting graph expansion if genuinely ambiguous

def extract_question_entities(question):
    prompt = f'List the named entities in this question as a JSON array of strings, nothing else.\nQuestion: "{question}"'
    from llm import safe_json_extract
    result = safe_json_extract(llm_call(prompt))
    return result if result else []

def hybrid_retrieve(question):
    vector_hits = vector_search(question)
    graph_hits = []
    if is_multihop(question):
        for entity in extract_question_entities(question):
            graph_hits += graph_expand(entity)
    return {"chunks": vector_hits, "graph_paths": graph_hits}