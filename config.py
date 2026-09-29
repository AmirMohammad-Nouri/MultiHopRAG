DATA_DIR = "data/medical/medlineplus_cluster"
NEO4J_URI = "bolt://localhost:7687"
NEO4J_AUTH = ("neo4j", "testpassword")
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "chunks"

LLM_MODEL = "qwen3:1.7b"
EMBED_MODEL = "nomic-embed-text"
EMBED_DIM = 768

ENTITY_TYPES = ["Condition", "Symptom", "Test", "Treatment", "Drug", "BodyPart", "RiskFactor"]
RELATION_TYPES = ["diagnoses", "treats", "causes", "symptom_of", "measures", "risk_factor_for", "prevents"]