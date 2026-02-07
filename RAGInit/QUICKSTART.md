# Quick Start Guide - ResilientX RAG Pipeline

## 🚀 30-Second Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Setup Ollama
curl https://ollama.ai/install.sh | sh
ollama serve &
ollama pull deepseek-r1:8b

# 3. Run verification
python setup_verification.py

# 4. Try examples
python examples.py
```

## 📝 Basic Usage (3 lines of code!)

```python
from rag_pipeline import RAGPipeline

pipeline = RAGPipeline()
pipeline.ingest_documents(['document.pdf'])
result = pipeline.query("Your question here")

print(result['final_answer'])
```

## 🎯 Hackathon Workflow

### Step 1: Initialize for Your Countries

```python
from rag_pipeline import ResilienceAssessmentPipeline

countries = ['India', 'China', 'USA', 'UK', 'Japan', 
             'Pakistan', 'Nepal', 'Bangladesh', 'Sri Lanka', 'Russia']

pipeline = ResilienceAssessmentPipeline(countries)
```

### Step 2: Build Knowledge Base

```python
# From PDFs
pipeline.ingest_documents([
    'reports/imf_report.pdf',
    'reports/world_bank_data.pdf',
    'reports/country_profiles.pdf'
])

# From Google Drive (after setting up credentials)
pipeline.ingest_from_google_drive(folder_id='YOUR_FOLDER_ID')

# From APIs (after adding API keys to .env)
pipeline.ingest_from_apis(countries)

# From News
pipeline.ingest_news(countries)

# Save for later use
pipeline.save_knowledge_base("my_kb")
```

### Step 3: Assess Scenarios

```python
# Final day scenario
scenario = """
A major cyberattack has disrupted critical infrastructure 
in Japan, affecting power grids and communication networks.
"""

assessment = pipeline.assess_scenario(scenario, country="Japan")

print(f"Readiness Score: {assessment['readiness_score']}")
print(f"Explanation: {assessment['readiness_explanation']}")
print(f"\nDetailed Analysis:\n{assessment['assessment']}")
```

### Step 4: Launch Dashboard

```bash
streamlit run streamlit_app.py
```

## 🔧 Configuration

### Quick Config Changes

```python
from config import config

# Adjust chunking
config.chunking.chunk_size = 1024
config.chunking.chunk_overlap = 256

# Adjust search
config.search.top_k = 10
config.search.search_algorithm = "hybrid"

# Adjust LLM
config.llm.temperature = 0.5
config.llm.max_tokens = 4096
```

## 📊 Key Features for Judges

### 1. Multi-Step Reasoning ✓
```python
result = pipeline.query(query, reasoning_mode="full")
# Analysis → Critique → Synthesis
```

### 2. Hybrid Search ✓
```python
result = pipeline.query(query, search_algorithm="hybrid")
# Combines semantic (FAISS) + keyword (BM25)
```

### 3. Readiness Scoring ✓
```python
assessment = pipeline.assess_scenario(scenario)
print(assessment['readiness_score'])  # 0-100
print(assessment['readiness_explanation'])  # Why?
```

### 4. Causal Reasoning ✓
```python
# The reasoning engine explains cascading effects
# Energy shock → Industrial decline → Economic crisis → Debt increase
```

### 5. Evidence-Based ✓
```python
# Every answer includes supporting evidence
for doc in result['retrieved_documents']:
    print(f"Source: {doc['metadata']['source']}")
    print(f"Relevance: {doc['score']}")
```

## 🎨 Streamlit Dashboard Features

- 📝 Interactive scenario assessment
- 📊 Real-time readiness scoring
- 🔍 Knowledge base search
- 📈 Multi-country comparison
- 📚 Evidence visualization
- ⚙️ Developer tools

## 🐛 Common Issues

### "Ollama connection failed"
```bash
ollama serve
# In another terminal:
ollama pull deepseek-r1:8b
```

### "No module named 'faiss'"
```bash
pip install faiss-cpu
```

### "Pipeline not initialized"
```python
pipeline.ingest_documents(['some_file.pdf'])
# OR
pipeline.load_knowledge_base("my_kb")
```

## 📞 Need Help?

1. Run: `python setup_verification.py`
2. Check: `logs/` directory
3. Try: `python examples.py` and select Example 6

## 🏆 Winning Features

✅ **Handles ambiguous scenarios** - Multi-step reasoning
✅ **Cross-sector spillovers** - Causal chain analysis  
✅ **Contradictory information** - Critique step identifies issues
✅ **Explainability** - SHAP-style evidence attribution
✅ **Scalability** - Add unlimited documents without retraining
✅ **Real-time updates** - Parallel search + reasoning
✅ **Professional UI** - Streamlit dashboard
✅ **Developer-friendly** - Full backend access

## 📝 File Structure Cheatsheet

```
rag_pipeline/
├── config.py              # All settings
├── rag_pipeline.py        # Main pipeline
├── examples.py            # Usage examples
├── streamlit_app.py       # Frontend
├── developer_interface.py # Backend access
├── setup_verification.py  # System check
└── README.md             # Full documentation
```

## ⚡ Performance Tips

```python
# For demos/judges (fast)
result = pipeline.query(query, 
    reasoning_mode="simple",
    top_k=3
)

# For final submission (comprehensive)
result = pipeline.query(query,
    reasoning_mode="full",
    top_k=10,
    search_algorithm="hybrid"
)
```

---

**You're ready! Good luck with the hackathon! 🚀**
