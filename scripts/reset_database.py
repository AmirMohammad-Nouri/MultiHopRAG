# scripts/reset_databases.py
from qdrant_client import QdrantClient
from neo4j import GraphDatabase

def reset_qdrant():
    client = QdrantClient(url="http://localhost:6333")
    try:
        client.delete_collection("chunks")
        print("Qdrant: collection 'chunks' deleted")
    except Exception as e:
        print(f"Qdrant: nothing to delete or error — {e}")

def reset_neo4j():
    driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "testpassword"))
    with driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    driver.close()
    print("Neo4j: all nodes and relationships deleted")

if __name__ == "__main__":
    confirm = input("This will WIPE both databases. Type 'yes' to continue: ")
    if confirm.strip().lower() == "yes":
        reset_qdrant()
        reset_neo4j()
        print("Both databases cleared. Re-run ingestion when ready.")
    else:
        print("Aborted.")