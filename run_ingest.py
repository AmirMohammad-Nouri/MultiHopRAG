# ingest/run_ingest.py
from ingest.parse_medlineplus import load_all_docs
from ingest.chunk import chunk_doc
from ingest.embed import embed_and_store
from ingest.extract_graph import extract_and_write, safe_json_extract
from llm import llm_call
from ingest.extract_graph import EXTRACTION_PROMPT  # your prompt template

def run():
    docs = load_all_docs("data/medical/medlineplus/Sample")
    print(f"Loaded {len(docs)} documents")

    for doc in docs:
        print(f"Processing: {doc['doc_id']} (title: {doc['title']!r}, content length: {len(doc['content'])})")
        chunks = chunk_doc(doc)
        print(f"  {doc['title']}: {len(chunks)} chunks")

        # vector side
        embed_and_store(chunks, doc["doc_id"])

        # graph side
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc['doc_id']}_{i}"
            prompt = EXTRACTION_PROMPT.format(title=doc["title"], chunk=chunk["text"])
            raw = llm_call(prompt, temperature=0.0)
            parsed = safe_json_extract(raw)
            if parsed is None:
                print(f"    [WARN] extraction failed for {chunk_id}, skipping")
                continue
            extract_and_write(parsed.get("entities", []), parsed.get("relations", []), chunk_id, doc["title"])

if __name__ == "__main__":
    run()