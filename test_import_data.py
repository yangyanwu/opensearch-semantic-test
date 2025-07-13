from opensearchpy import OpenSearch, helpers
import csv

# Set maximum field size limit (e.g., 2GB)
csv.field_size_limit(2 * 1024 * 1024 * 1024)

# Connect to OpenSearch
client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    #http_auth=('admin', 'admin'),  # change if needed
    use_ssl=False,  # Set to True if using HTTPS
)

# Define generator to convert CSV to documents
def generate_docs(csv_file_path):
    with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            yield {
                "_index": "enron-data",  # your index name
                "_source": row
            }

# Run bulk import
helpers.bulk(client, generate_docs('emails.csv'))
