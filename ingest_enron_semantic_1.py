from opensearchpy import OpenSearch, helpers
from sentence_transformers import SentenceTransformer
import time
import csv

INDEX_NAME = "enron-semantic-1"
DIMENSION = 384  # For 'all-MiniLM-L6-v2'
EMBEDDING_MODEL = 'all-MiniLM-L6-v2'

# ----------- Step 1: Setup ----------- #
# Set maximum field size limit (e.g., 2GB)
csv.field_size_limit(2 * 1024 * 1024 * 1024)

# Connect to OpenSearch
client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    #http_auth=('admin', 'admin'),  # adjust if needed
    use_ssl=False
)

# Load embedding model
model = SentenceTransformer(EMBEDDING_MODEL)

# ----------- Step 2: Create Index ----------- #

# Delete index if exists
if not client.indices.exists(index=INDEX_NAME):
    #client.indices.delete(index=INDEX_NAME)

    # Create index with knn_vector
    client.indices.create(
        index=INDEX_NAME,
        body={
            "settings": {
                "index": {
                    "knn": True
                }
            },
            "mappings": {
                "properties": {
                    "file": { "type": "text" },
                    "message": { "type": "text" },
                    "message_vector": {
                        "type": "knn_vector",
                        "dimension": DIMENSION
                    }
                }
            }
        }
    )


# ----------- Step 3: Index Documents ----------- #
# Define generator to convert CSV to documents
csv_file_path = "emails.csv"
actions = []

doc_count = 0
with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        doc_count += 1
        message_vector = model.encode(row['message']).tolist()
        actions.append({
            "_index": INDEX_NAME,
            "_source": {
                "file": row['file'],
                "message": row['message'],
                "message_vector": message_vector,
            }
        })
        time.sleep(0.03) # Throttle to avoid overwhelming the server
        
        if len(actions) >= 1000:
            try:
                helpers.bulk(client, actions)
            except Exception as e:
                print(f"Error indexing batch: {e}")
            actions = []
            print(f"Indexed {doc_count} documents...")

if len(actions) >= 1:
    try:
        helpers.bulk(client, actions)
    except Exception as e:
        print(f"Error indexing final batch: {e}")
    actions = []
    print(f"Indexed {doc_count} documents...")

# Optional: wait for indexing to complete
time.sleep(1)
print("All documents indexed successfully.")