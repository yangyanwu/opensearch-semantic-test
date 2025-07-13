from opensearchpy import OpenSearch, helpers
import time
import csv

INDEX_NAME = "enron-1"

# ----------- Step 1: Setup ----------- #
# Set maximum field size limit (e.g., 2GB)
csv.field_size_limit(2 * 1024 * 1024 * 1024)

# Connect to OpenSearch
client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    #http_auth=('admin', 'admin'),  # adjust if needed
    use_ssl=False
)


# ----------- Step 2: Create Index ----------- #

# Delete index if exists
if not client.indices.exists(index=INDEX_NAME):
    #client.indices.delete(index=INDEX_NAME)

    # Create index with knn_vector
    client.indices.create(
        index=INDEX_NAME
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
        # if doc_count <= 257000:  # Skip first 1000 rows
        #     continue
        actions.append({
            "_index": INDEX_NAME,
            "_source": row
        })
        
        if len(actions) >= 10000:
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