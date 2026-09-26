# ingest/extract_graph.py
from neo4j import GraphDatabase
import json
import re   

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "testpassword"))

EXTRACTION_PROMPT = """Extract medical entities and relationships from this text, which is from an article titled "{title}".

Entity types: Condition, Symptom, Test, Treatment, Drug, BodyPart, RiskFactor
Relation types: diagnoses, treats, causes, symptom_of, measures, risk_factor_for, prevents

Return ONLY valid JSON, no explanation, no markdown fences.

Example:
Article title: "A1C"
Text: "A1C is a blood test for type 2 diabetes and prediabetes. It measures average blood glucose level over the past 3 months."
Output: {{"entities":[{{"id":"e1","name":"A1C","type":"Test"}},{{"id":"e2","name":"type 2 diabetes","type":"Condition"}},{{"id":"e3","name":"prediabetes","type":"Condition"}},{{"id":"e4","name":"blood glucose","type":"BodyPart"}}],"relations":[{{"source":"e1","target":"e2","type":"diagnoses"}},{{"source":"e1","target":"e3","type":"diagnoses"}},{{"source":"e1","target":"e4","type":"measures"}}]}}

Article title: "{title}"
Text: "{chunk}"
Output:"""

def safe_json_extract(raw_output):
    match = re.search(r'\{.*\}', raw_output, re.DOTALL)
    if not match:
        return None
    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None
    
def _resolve_name(extracted_name, doc_title):
    """If the extracted entity is basically the article's own subject
    (e.g. 'HbA1C', 'Glycohemoglobin' inside the A1C article), collapse it
    to the canonical article title instead of creating a near-duplicate node."""
    norm_extracted = extracted_name.lower().strip()
    norm_title = doc_title.lower().strip()
    if norm_extracted == norm_title:
        return doc_title
    # cheap substring heuristic; upgrade to fuzzy/embedding match later if needed
    if norm_extracted in norm_title or norm_title in norm_extracted:
        return doc_title
    return extracted_name


def extract_and_write(entities, relations, source_chunk_id, doc_title):
    """Write extracted entities/relations for one chunk into Neo4j.
    doc_title is used to resolve self-referential aliases to a canonical name."""
    resolved = {}  # maps original extracted id -> resolved name, for building relations

    with driver.session() as session:
        for e in entities:
            resolved_name = _resolve_name(e["name"], doc_title)
            resolved[e["id"]] = resolved_name
            session.run(
                "MERGE (n:Entity {name: $name}) SET n.type = $type",
                name=resolved_name, type=e["type"],
            )

        for r in relations:
            src_name = resolved.get(r["source"])
            tgt_name = resolved.get(r["target"])
            if not src_name or not tgt_name:
                continue  # relation refers to an entity id we never saw — skip safely
            session.run(
                """MATCH (a:Entity {name: $src}), (b:Entity {name: $tgt})
                   MERGE (a)-[rel:REL {type: $rtype}]->(b)
                   SET rel.source_chunk = $chunk_id""",
                src=src_name, tgt=tgt_name, rtype=r["type"], chunk_id=source_chunk_id,
            )