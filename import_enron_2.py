from opensearchpy import OpenSearch, helpers
import time
import csv
import email
from email.policy import default
import pandas as pd

INDEX_NAME = "enron-2"

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
        index=INDEX_NAME,
        body={
            "settings": {
                "index": {
                    "knn": False
                }
            },
            "mappings": {
                "properties": {
                    "message": { "type": "object" }
                }
            }
        }
    )


# ----------- Step 3: Index Documents ----------- #
def parse_enron_email(s, file_path):
    """Parse a single Enron email"""
    msg = email.message_from_string(s, policy=default)
    
    email_data = {
        'file': file_path,
        'message-id': msg['Message-ID'],
        'from': msg['From'],
        'to': msg['To'],
        'x-to': msg['X-To'],
        'x-cc': msg['X-Cc'],
        'x-bcc': msg['X-Bcc'],
        'subject': msg['Subject'],
        'date': msg['Date'],
        'body': ''
    }
    
    # Extract plain text body
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == 'text/plain':
                email_data['body'] = part.get_payload(decode=True).decode('latin-1')
                break
    else:
        email_data['body'] = msg.get_payload(decode=True).decode('latin-1')
    
    return email_data
  
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
        try:
            doc = parse_enron_email(row['message'], row['file'])
        except Exception as e:
            print(f"Error parsing email: {e}")
            continue
        actions.append({
            "_index": INDEX_NAME,
            "_id": doc['message-id'],
            "_source": {
                "message": doc
            }
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