# synthesis/answer.py
from llm import llm_call

SYNTH_PROMPT = """Answer the question using ONLY the facts below. Be concise (1-3 sentences).
If the facts don't contain enough information to answer, say so clearly instead of guessing.
Mention which fact(s) you used (e.g. "based on the graph fact..." or "based on the retrieved passage...").

Graph facts:
{graph_facts}

Retrieved passages:
{chunks}

Question: {question}
Answer:"""


def format_path(path):
    """
    Turn a neo4j Path object into a readable string like:
    'A1C -[diagnoses]-> Diabetes -[treats]<- Metformin'
    """
    parts = []
    nodes = path.nodes
    rels = path.relationships

    parts.append(nodes[0].get("name", "Unknown"))
    for i, rel in enumerate(rels):
        rel_type = rel.get("type", rel.type)
        target_node = nodes[i + 1]
        target_name = target_node.get("name", "Unknown")

        # direction: does the relationship start at the node we just came from?
        if rel.start_node.element_id == nodes[i].element_id:
            parts.append(f"-[{rel_type}]-> {target_name}")
        else:
            parts.append(f"<-[{rel_type}]- {target_name}")

    return " ".join(parts)


def format_chunk(chunk_tuple):
    """
    chunk_tuple: (text, score) as returned by vector_search
    """
    text, score = chunk_tuple
    return text.strip()


def synthesize(question, retrieval_result, max_chunks=5, max_graph_facts=10):
    graph_paths = retrieval_result.get("graph_paths", [])[:max_graph_facts]
    chunks = retrieval_result.get("chunks", [])[:max_chunks]

    if graph_paths:
        graph_facts_str = "\n".join(f"- {format_path(p)}" for p in graph_paths)
    else:
        graph_facts_str = "None"

    if chunks:
        chunks_str = "\n---\n".join(format_chunk(c) for c in chunks)
    else:
        chunks_str = "None"

    prompt = SYNTH_PROMPT.format(
        graph_facts=graph_facts_str,
        chunks=chunks_str,
        question=question,
    )

    return llm_call(prompt, temperature=0.0)