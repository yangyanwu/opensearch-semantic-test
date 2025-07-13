from opensearchpy import OpenSearch, helpers
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
import time

# ----------- Step 1: Setup ----------- #

# Connect to OpenSearch
client = OpenSearch(
    hosts=[{'host': 'localhost', 'port': 9200}],
    #http_auth=('admin', 'admin'),  # adjust if needed
    use_ssl=False
)

INDEX_NAME = "test-semantic"
DIMENSION = 384  # For 'all-MiniLM-L6-v2'

# Load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# ----------- Step 2: Create Index ----------- #

# Delete index if exists
if client.indices.exists(index=INDEX_NAME):
    client.indices.delete(index=INDEX_NAME)

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

docs = [
    "Here is our forecast for Q2.",
    "Let’s schedule a call to review the budget.",
    "The meeting has been moved to Friday.",
    "We need to discuss the project timeline.",
    "I’m sharing the updated financial report.",
]

actions = []

for i, doc in enumerate(docs):
    vector = model.encode(doc).tolist()
    actions.append({
        "_index": INDEX_NAME,
        "_id": i,
        "_source": {
            "message": doc,
            "message_vector": vector
        }
    })

helpers.bulk(client, actions)

# Optional: wait for indexing to complete
time.sleep(1)

# ----------- Step 4: Semantic Search ----------- #

query_text = "What’s our plan for the next quarter?"
query_vector = model.encode(query_text).tolist()

search_body = {
    "size": 3,
    "query": {
        "knn": {
            "message_vector": {
                "vector": query_vector,
                "k": 3
            }
        }
    }
}

results = client.search(index=INDEX_NAME, body=search_body)

print(f"\nTop matches for: \"{query_text}\"\n")
for hit in results["hits"]["hits"]:
    print(f"- {hit['_source']['message']} (score: {hit['_score']:.4f})")

messages = [hit["_source"]["message"] for hit in results["hits"]["hits"]]

# ----------- Summarize with Gemini ----------- #
prompt = "Summarize the following email messages:\n\n"
for i, msg in enumerate(messages, 1):
    prompt += f"{i}. {msg}\n"
prompt += "\nSummary:"

GEMINI_API_KEY="AIzaSyDX0Looo6O92Y5Rxo2AL1ce31D0_timBic"
genai.configure(api_key=GEMINI_API_KEY)
gemini_model = genai.GenerativeModel('gemini-2.5-flash')


response = gemini_model.generate_content({
    "text": prompt
})

print("\n🧠 Gemini Summary:")
print(response.text)