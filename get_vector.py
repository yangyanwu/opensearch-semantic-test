from sentence_transformers import SentenceTransformer

# ----------- Step 1: Setup ----------- #

INDEX_NAME = "test-semantic"
DIMENSION = 384  # For 'all-MiniLM-L6-v2'

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

query_text = "dicuss forecast"
query_vector = model.encode(query_text).tolist()
print(f"Query vector: {query_vector}")
