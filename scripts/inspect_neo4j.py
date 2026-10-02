# scripts/inspect_neo4j.py
from neo4j import GraphDatabase

driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "testpassword"))

with driver.session() as session:
    node_count = session.run("MATCH (n) RETURN count(n) AS c").single()["c"]
    rel_count = session.run("MATCH ()-[r]->() RETURN count(r) AS c").single()["c"]
    print(f"Nodes: {node_count}, Relationships: {rel_count}")

    print("\nSample nodes:")
    for record in session.run("MATCH (n) RETURN n.name, n.type LIMIT 10"):
        print(" ", record["n.name"], "-", record["n.type"])

    print("\nRelation types used:")
    for record in session.run("MATCH ()-[r]->() RETURN DISTINCT r.type, count(*) AS c ORDER BY c DESC"):
        print(" ", record["r.type"], ":", record["c"])