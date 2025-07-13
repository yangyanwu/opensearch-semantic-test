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
# Basic indexing (creates traditional search index)
python ingest_enron_1.py

# Enhanced semantic search (with full-message embeddings)
python ingest_enron_semantic_1.py
```

### Option 2: Parsed Data Indexing
```bash
# Basic parsed data indexing
python ingest_enron_2.py

# Advanced semantic search (with separate subject/body embeddings)
python ingest_enron_semantic_2.py
```

## Workflow Summary
Choose either approach based on your search requirements:

1. **Basic Indexing**
   - Creates traditional search indexes
   - Faster ingestion
   - Good for exact-match queries

2. **Semantic Indexing** (For AI-powered search):
   - Generates vector embeddings for:
     - Option 1: Complete email messages
     - Option 2: Separate subject and body components
   - Enables similarity-based searches
   - Better for conceptual/contextual queries