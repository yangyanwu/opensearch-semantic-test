Here's an improved and well-formatted version of your README in Markdown:

```markdown
# 📧 Enron Email Indexing with OpenSearch & Gemini

This project provides scripts to ingest and semantically index the Enron email dataset using OpenSearch with Google Gemini embeddings.

## 🚀 Quick Start

### Prerequisites
- Podman (or Docker) installed
- Python 3.8+
- Kaggle account (to download dataset)
- Google Gemini API key

### 1. Start OpenSearch
```bash
podman compose --file docker-compose.yaml up --detach
```

Access the OpenSearch dashboard at:  
🔗 [http://localhost:5601/](http://localhost:5601/)

### 2. Setup Environment
1. Download the Enron dataset:
   - Get `emails.csv` from [Kaggle](https://www.kaggle.com/datasets/wcukierski/enron-email-dataset)
   - Place it in the project root directory

2. Create `.env` file:
   ```env
   GEMINI_API_KEY=your_api_key_here
   ```

3. Set up Python environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # OR
   venv\Scripts\activate    # Windows
   
   pip install opensearch-py sentence-transformers google-generativeai
   ```

## 📂 Data Ingestion Pipeline

### Option 1: Raw Data Indexing
```bash
python ingest_enron_1.py        # Basic indexing
python ingest_enron_semantic_1.py  # Semantic indexing with message embeddings
```

### Option 2: Parsed Data Indexing
```bash
python ingest_enron_2.py        # Basic indexing of parsed data
python ingest_enron_semantic_2.py  # Semantic indexing with subject/body embeddings
```

## Workflow Summary
1. **Basic Indexing**: Stores raw email data
2. **Semantic Indexing**: Creates vector embeddings for:
   - Full message content (Option 1)
   - Separate subject and body embeddings (Option 2)

Note: Run the basic indexing scripts before their semantic counterparts for each dataset version.
```

Key improvements:
1. Better organization with clear sections
2. Added prerequisites section
3. More detailed Python environment setup
4. Clearer workflow explanation
5. Better formatting for commands and paths
6. Added emojis for better visual scanning
7. Fixed the duplicate semantic script reference in original
8. Added note about execution order