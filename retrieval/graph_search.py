# retrieval/graph_search.py
from neo4j import Driver


def graph_expand(entity_name, hops=2):
    with Driver.session() as session:
        result = session.run(
            f"MATCH path = (a:Entity {{name: $name}})-[:REL*1..{hops}]-(b) RETURN path LIMIT 25",
            name=entity_name
        )
        return [r["path"] for r in result]