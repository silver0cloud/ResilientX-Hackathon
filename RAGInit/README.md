# RAG Pipeline for Resilience Assessment

A comprehensive Retrieval-Augmented Generation (RAG) pipeline built for the **ResilientX Adaptive Country Resilience Stress-Test Engine** hackathon project.

## 🎯 Project Overview

This pipeline implements a state-of-the-art RAG system with:
- **FAISS Vector Database** for efficient similarity search
- **BGE-small-en-v1.5** embeddings for semantic understanding
- **DeepSeek-R1** (Distill-Llama-8B) for multi-step reasoning via Ollama
- **Parallel Search & Reasoning** architecture
- **Multi-source data ingestion** (PDFs, APIs, News, Google Drive)
- **Intelligent recursive chunking** with OCR support
- **Hybrid search** (semantic + keyword)
- **Developer interface** for backend access

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER QUERY                              │
└─────────────────┬───────────────────────────────────────────┘
                  │
        ┌─────────┴──────────┐
        │                    │
    ┌───▼────┐         ┌────▼─────┐
    │ SEARCH │         │ REASONING│
    │ ENGINE │         │  ENGINE  │
    └───┬────┘         └────┬─────┘
        │                   │
    ┌───▼────────────┐      │
    │  FAISS VectorDB│      │
    │  + BM25        │      │
    └───┬────────────┘      │
        │                   │
        └────────┬──────────┘
                 │
        ┌────────▼──────────┐
        │  DEEPSEEK-R1      │
        │  3-Step Reasoning │
        │  1. Analysis      │
        │  2. Critique      │
        │  3. Synthesis     │
        └────────┬──────────┘
                 │
        ┌────────▼──────────┐
        │ FINAL ANSWER +    │
        │ READINESS SCORE   │
        └───────────────────┘
```

## 📋 Features

### Core Features
- ✅ **Multi-format document processing**: PDFs (with OCR), CSV, XLSX, XLSB
- ✅ **Google Drive integration**: Automatic sync and ingestion
- ✅ **API data fetching**: IMF, World Bank, EIA, Ember
- ✅ **News scraping**: Newspaper3k for real-time resilience news
- ✅ **Recursive context chunking**: Maintains semantic integrity
- ✅ **OCR support**: Extract text from images and graphs in PDFs
- ✅ **Hybrid search**: Combines semantic (FAISS) and keyword (BM25) search
- ✅ **Multi-step reasoning**: Analysis → Critique → Synthesis
- ✅ **Readiness scoring**: Automated resilience assessment
- ✅ **Parallel processing**: Search and reasoning work simultaneously
- ✅ **Developer interface**: Full backend access and configuration
- ✅ **Persistent storage**: Save/load knowledge bases
- ✅ **Flexible & extensible**: Easy to add new data sources

### Advanced Features
- 🔍 Multiple search algorithms (semantic, keyword, hybrid)
- 🧠 Three-step reasoning process with confidence intervals
- 📊 Structured data handling (automatic DataFrame to text conversion)
- 🌐 Custom URL scraping with fallback mechanisms
- 💾 Embedding caching for performance
- 📈 Pipeline monitoring and health checks
- 🔧 Hot-swappable configuration
- 🎛️ Interactive developer console

## 🚀 Quick Start

### 1. Prerequisites

```bash
# Python 3.9+
python --version

# Install Ollama (for DeepSeek-R1)
curl https://ollama.ai/install.sh | sh

# Pull DeepSeek-R1 model
ollama pull deepseek-r1:8b

# Start Ollama server
ollama serve
```

### 2. Installation

```bash
# Clone the repository
cd rag_pipeline

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.template .env
# Edit .env and add your API keys
```

### 3. Google Drive Setup (Optional)

If using Google Drive integration:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Google Drive API
4. Create OAuth 2.0 credentials
5. Download `credentials.json` and place in project root
6. First run will open browser for authentication

### 4. Basic Usage

```python
from rag_pipeline import RAGPipeline

# Initialize pipeline
pipeline = RAGPipeline()

# Ingest documents
pipeline.ingest_documents([
    'path/to/document1.pdf',
    'path/to/document2.xlsx'
])

# Query the system
result = pipeline.query(
    "What are the key resilience metrics?",
    top_k=5,
    search_algorithm="hybrid",
    reasoning_mode="full"
)

print(result['final_answer'])
print(f"Readiness Score: {result['readiness_score']}")

# Save knowledge base
pipeline.save_knowledge_base("my_kb")
```

### 5. Resilience Assessment

```python
from rag_pipeline import ResilienceAssessmentPipeline

# Initialize for specific countries
countries = ['India', 'China', 'USA', 'UK', 'Japan']
pipeline = ResilienceAssessmentPipeline(countries)

# Build knowledge base
data_sources = {
    'pdfs': ['reports/imf_data.pdf', 'reports/world_bank.pdf'],
    'drive_folder': 'YOUR_FOLDER_ID',
    'use_apis': True,
    'use_news': True
}

pipeline.build_knowledge_base(data_sources)

# Assess a crisis scenario
scenario = "A cyberattack disrupts 30% of energy infrastructure"
assessment = pipeline.assess_scenario(scenario, country="Japan")

print(f"Readiness Score: {assessment['readiness_score']}")
print(f"Explanation: {assessment['readiness_explanation']}")
```

## 📁 Project Structure

```
rag_pipeline/
├── config.py                 # Configuration management
├── document_processor.py     # PDF, CSV, XLSX processing + OCR
├── google_drive_client.py    # Google Drive integration
├── api_fetchers.py          # IMF, World Bank, EIA, Ember APIs
├── news_scraper.py          # News scraping with Newspaper3k
├── chunking.py              # Recursive text chunking
├── embeddings.py            # BGE embeddings with caching
├── vector_db.py             # FAISS vector database + hybrid search
├── reasoning.py             # DeepSeek-R1 reasoning engine
├── rag_pipeline.py          # Main RAG pipeline
├── developer_interface.py   # Developer backend access
├── examples.py              # Usage examples
├── requirements.txt         # Python dependencies
└── .env.template           # Environment variables template
```

## 🔧 Configuration

Edit `config.py` or use environment variables:

```python
from config import config

# Update embedding settings
config.embedding.model_name = "BAAI/bge-small-en-v1.5"
config.embedding.batch_size = 32

# Update chunking settings
config.chunking.chunk_size = 512
config.chunking.chunk_overlap = 128

# Update LLM settings
config.llm.temperature = 0.7
config.llm.max_tokens = 2048

# Update search settings
config.search.top_k = 5
config.search.search_algorithm = "hybrid"
```

## 🎮 Developer Interface

Access the full backend through the developer interface:

```python
from developer_interface import DeveloperInterface

dev = DeveloperInterface()
dev.initialize_pipeline(['India', 'China', 'USA'])

# Interactive mode
dev.interactive_mode()

# Or use programmatically
dev.add_data_source('pdf', 'document.pdf')
results = dev.test_search("energy security")
dev.export_knowledge_base("metadata.json")
```

### Available Commands

```
stats         - Show pipeline statistics
config        - Show current configuration
search <query> - Test search
reason <query> - Test reasoning
add <type> <path> - Add data source
save <name>    - Save knowledge base
load <name>    - Load knowledge base
export <file>  - Export metadata
```

## 📊 Data Sources

### 1. PDF Documents
```python
pipeline.ingest_documents([
    'path/to/doc.pdf'
], use_ocr=True)
```

### 2. Google Drive
```python
pipeline.ingest_from_google_drive(
    folder_id='YOUR_FOLDER_ID',
    sync_dir='./data/drive'
)
```

### 3. API Data
```python
countries = ['India', 'China', 'USA']
pipeline.ingest_from_apis(countries)
```

### 4. News Articles
```python
pipeline.ingest_news(countries=['India', 'USA'])
```

### 5. Custom URLs
```python
urls = [
    'https://www.worldbank.org/report',
    'https://www.imf.org/analysis'
]
pipeline.ingest_custom_urls(urls)
```

## 🔍 Search Algorithms

### Semantic Search
Uses FAISS vector similarity:
```python
result = pipeline.query(query, search_algorithm="semantic")
```

### Keyword Search
Uses BM25 algorithm:
```python
result = pipeline.query(query, search_algorithm="keyword")
```

### Hybrid Search (Recommended)
Combines both approaches:
```python
result = pipeline.query(query, search_algorithm="hybrid")
```

## 🧠 Reasoning Modes

### Full Reasoning (3-Step)
```python
result = pipeline.query(query, reasoning_mode="full")
# Steps: Analysis → Critique → Synthesis
```

### Simple Reasoning (Fast)
```python
result = pipeline.query(query, reasoning_mode="simple")
# Single-pass analysis
```

## 📈 Performance Tips

1. **Use caching**: Embedding caching is enabled by default
2. **Batch processing**: Use `batch_query()` for multiple queries
3. **Adjust chunk size**: Larger chunks = more context, slower search
4. **Choose right index**: IndexFlatIP for <100k vectors, IndexIVFFlat for more
5. **Reranking**: Enable for better precision (slower)

## 🐛 Troubleshooting

### Ollama Connection Failed
```bash
# Make sure Ollama is running
ollama serve

# Check if model is available
ollama list

# Pull model if needed
ollama pull deepseek-r1:8b
```

### Google Drive Authentication
```bash
# Delete token and re-authenticate
rm token.json
# Run pipeline again, browser will open
```

### Out of Memory
```python
# Reduce batch size
config.embedding.batch_size = 16
config.chunking.chunk_size = 256
```

### Slow Performance
```python
# Use simple reasoning mode
result = pipeline.query(query, reasoning_mode="simple")

# Reduce top_k
result = pipeline.query(query, top_k=3)
```

## 🎯 Hackathon-Specific Features

### 7 Resilience Metrics Support
1. Economic Stability
2. Defense & Strategic Security
3. Healthcare & Biological Readiness
4. Cyber Resilience & Digital Infrastructure
5. Demographic & Social Stability
6. Energy Security
7. Debt & Fiscal Sustainability

### Country Assessment
```python
pipeline.assess_scenario(
    "Major earthquake in Nepal",
    country="Nepal"
)
```

### Multi-Country Comparison
```python
pipeline.compare_countries(
    "Global pandemic affecting healthcare"
)
```

### Readiness Scoring
- Automatic score extraction (0-100)
- Confidence intervals
- Causal explanation

## 🚢 Deployment

### Streamlit Integration (Coming Soon)
```python
# Will be added for frontend visualization
import streamlit as st
from rag_pipeline import RAGPipeline

pipeline = RAGPipeline()
# Streamlit UI code here
```

## 📝 Examples

Run the examples:
```bash
python examples.py
```

Available examples:
1. Basic RAG Pipeline
2. Resilience Assessment Pipeline
3. Multi-Source Data Ingestion
4. Advanced Search Algorithms
5. Developer Interface
6. Full Hackathon Workflow

## 🤝 Contributing

To extend the pipeline:

1. Add new data source in `api_fetchers.py` or `news_scraper.py`
2. Create custom chunking strategy in `chunking.py`
3. Implement new search algorithm in `vector_db.py`
4. Add reasoning templates in `reasoning.py`

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- FAISS by Facebook AI
- Sentence Transformers by UKPLab
- DeepSeek-R1 by DeepSeek AI
- Ollama for local LLM hosting
- Newspaper3k for news extraction

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review examples.py
3. Use developer interface for debugging
4. Check logs in `logs/` directory

---

**Built for ResilientX Hackathon - PS1: Adaptive Country Resilience Stress-Test Engine**
