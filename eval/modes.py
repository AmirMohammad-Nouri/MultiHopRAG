# eval/modes.py
from retrieval.vector_search import vector_search
from retrieval.graph_search import graph_expand
from retrieval.hybrid_retriever import hybrid_retrieve, extract_question_entities

def retrieve_vector_only(question):
    return {"chunks": vector_search(question), "graph_paths": []}

def retrieve_graph_only(question):
    graph_hits = []
    for entity in extract_question_entities(question):
        graph_hits += graph_expand(entity)
    return {"chunks": [], "graph_paths": graph_hits}

def retrieve_hybrid(question):
    return hybrid_retrieve(question)

MODES = {
    "vector_only": retrieve_vector_only,
    "graph_only": retrieve_graph_only,
    "hybrid": retrieve_hybrid,
}