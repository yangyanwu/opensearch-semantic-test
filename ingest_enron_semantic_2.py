from opensearchpy import OpenSearch, helpers
from sentence_transformers import SentenceTransformer
import time
import csv
import email
from email.policy import default
import logging

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Starting Enron Semantic Ingestion...")

INDEX_NAME = "enron-semantic-2"
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
                    "message": { "type": "object" },
                    "subject_vector": {
                        "type": "knn_vector",
                        "dimension": DIMENSION
                    },
                    "body_vector": {
                        "type": "knn_vector",
                        "dimension": DIMENSION
                    }
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
        try:
            doc = parse_enron_email(row['message'], row['file'])
        except Exception as e:
            logger.error(f"Error parsing email: {e}")
            continue
        subject_vector = model.encode(doc['subject'], show_progress_bar = False).tolist()
        body_vector = model.encode(doc['body'], show_progress_bar = False).tolist()
        actions.append({
            "_index": INDEX_NAME,
            "_id": doc['message-id'],
            "_source": {
                "message": doc,
                "subject_vector": subject_vector,
                "body_vector": body_vector,
            }
        })
        time.sleep(0.03) # Throttle to avoid overwhelming the server
        
        if len(actions) >= 1000:
            try:
                helpers.bulk(client, actions)
            except Exception as e:
                logger.error(f"Error indexing batch: {e}")
            actions = []
            logger.info(f"Indexed {doc_count} documents...")

if len(actions) >= 1:
    try:
        helpers.bulk(client, actions)
    except Exception as e:
        logger.error(f"Error indexing final batch: {e}")
    actions = []
    logger.info(f"Indexed {doc_count} documents...")

# Optional: wait for indexing to complete
time.sleep(1)
logger.info("All documents indexed successfully.")