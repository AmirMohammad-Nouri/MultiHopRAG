# ingest/chunk.py

def chunk_doc(doc, size=250, overlap=40):
    """
    doc: dict with keys 'content', 'doc_id', 'title', 'url' 
         (as produced by parse_medline_file)
    Returns: list of chunk dicts, each carrying doc-level metadata.
    """
    words = doc["content"].split()
    chunks = []
    for i in range(0, len(words), size - overlap):
        chunk_text = " ".join(words[i:i + size])
        if not chunk_text.strip():
            continue  # skip empty trailing chunks
        chunks.append({
            "text": chunk_text,
            "doc_id": doc["doc_id"],
            "title": doc["title"],
            "url": doc["url"],
        })
    return chunks