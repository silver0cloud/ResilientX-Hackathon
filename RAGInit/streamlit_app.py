"""
Streamlit Frontend for RAG Pipeline
Provides interactive UI for resilience assessment
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
import time

# Import pipeline (will be imported when Streamlit runs)
try:
    from rag_pipeline import ResilienceAssessmentPipeline
    from config import config
except ImportError:
    st.error("Please ensure all dependencies are installed")
    st.stop()


# Page configuration
st.set_page_config(
    page_title="ResilientX Assessment Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .scenario-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'pipeline' not in st.session_state:
    st.session_state.pipeline = None
if 'kb_loaded' not in st.session_state:
    st.session_state.kb_loaded = False
if 'query_history' not in st.session_state:
    st.session_state.query_history = []


def initialize_pipeline():
    """Initialize the RAG pipeline"""
    with st.spinner("Initializing pipeline..."):
        countries = [
            'India', 'China', 'Pakistan', 'Nepal', 'Bangladesh',
            'Sri Lanka', 'USA', 'Russia', 'Japan', 'UK'
        ]
        st.session_state.pipeline = ResilienceAssessmentPipeline(countries)
        return True


def load_knowledge_base():
    """Load or build knowledge base"""
    if st.session_state.kb_loaded:
        return True
    
    # Try to load existing KB
    if st.session_state.pipeline.load_knowledge_base("resilience_kb"):
        st.session_state.kb_loaded = True
        st.success("Knowledge base loaded successfully!")
        return True
    else:
        st.warning("No existing knowledge base found. Please build one in the Data Management section.")
        return False


def main():
    """Main Streamlit app"""
    
    # Header
    st.markdown('<div class="main-header">🛡️ ResilientX Assessment Engine</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.title("⚙️ Configuration")
        
        # Initialize button
        if st.button("🚀 Initialize Pipeline", use_container_width=True):
            if initialize_pipeline():
                st.success("Pipeline initialized!")
        
        st.markdown("---")
        
        # System status
        st.subheader("📊 System Status")
        if st.session_state.pipeline:
            stats = st.session_state.pipeline.get_stats()
            st.metric("Total Vectors", stats.get('total_vectors', 0))
            st.metric("Total Chunks", stats.get('total_chunks', 0))
            st.metric("Embedding Dim", stats.get('dimension', 0))
            
            if stats.get('is_initialized'):
                st.success("✓ Ready")
            else:
                st.warning("⚠ Not initialized")
        else:
            st.info("Pipeline not initialized")
        
        st.markdown("---")
        
        # Settings
        st.subheader("🔧 Settings")
        search_algo = st.selectbox(
            "Search Algorithm",
            ["hybrid", "semantic", "keyword"],
            index=0
        )
        
        top_k = st.slider("Top K Results", 1, 20, 5)
        
        reasoning_mode = st.selectbox(
            "Reasoning Mode",
            ["full", "simple"],
            index=0
        )
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📝 Scenario Assessment",
        "📊 Data Management",
        "🔍 Search & Explore",
        "⚙️ Developer Tools"
    ])
    
    # Tab 1: Scenario Assessment
    with tab1:
        st.header("Crisis Scenario Assessment")
        
        if not st.session_state.pipeline:
            st.warning("Please initialize the pipeline first (sidebar)")
        elif not st.session_state.kb_loaded:
            if st.button("Load Knowledge Base"):
                load_knowledge_base()
        else:
            # Scenario input
            col1, col2 = st.columns([2, 1])
            
            with col1:
                scenario_text = st.text_area(
                    "Enter Crisis Scenario",
                    placeholder="Example: A regional conflict disrupts 40% of Pakistan's energy imports",
                    height=100
                )
            
            with col2:
                country = st.selectbox(
                    "Target Country (Optional)",
                    ["All Countries"] + [
                        'India', 'China', 'Pakistan', 'Nepal', 'Bangladesh',
                        'Sri Lanka', 'USA', 'Russia', 'Japan', 'UK'
                    ]
                )
            
            if st.button("🔍 Assess Scenario", type="primary", use_container_width=True):
                if scenario_text:
                    with st.spinner("Analyzing scenario..."):
                        target_country = None if country == "All Countries" else country
                        
                        start_time = time.time()
                        assessment = st.session_state.pipeline.assess_scenario(
                            scenario_text,
                            country=target_country
                        )
                        elapsed = time.time() - start_time
                        
                        # Display results
                        st.markdown('<div class="scenario-box">', unsafe_allow_html=True)
                        st.markdown(f"**Scenario:** {scenario_text}")
                        if target_country:
                            st.markdown(f"**Country:** {target_country}")
                        st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Readiness score
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            readiness_score = assessment.get('readiness_score', 'N/A')
                            if readiness_score != 'N/A':
                                st.metric("Readiness Score", f"{readiness_score:.1f}/100")
                            else:
                                st.metric("Readiness Score", "N/A")
                        
                        with col2:
                            st.metric("Analysis Time", f"{elapsed:.2f}s")
                        
                        with col3:
                            evidence_count = len(assessment.get('supporting_evidence', []))
                            st.metric("Evidence Docs", evidence_count)
                        
                        # Reasoning details
                        with st.expander("📋 Detailed Analysis", expanded=True):
                            st.markdown("**Analysis:**")
                            st.write(assessment['reasoning_details']['analysis'])
                            
                            st.markdown("**Critical Evaluation:**")
                            st.write(assessment['reasoning_details']['critique'])
                            
                            st.markdown("**Final Synthesis:**")
                            st.write(assessment['reasoning_details']['synthesis'])
                        
                        # Evidence
                        with st.expander("📚 Supporting Evidence"):
                            for i, evidence in enumerate(assessment.get('supporting_evidence', [])[:5], 1):
                                st.markdown(f"**Evidence {i}:**")
                                st.text(evidence['text'][:300] + "...")
                                st.markdown(f"*Source: {evidence['metadata'].get('source', 'Unknown')}*")
                                st.markdown("---")
                        
                        # Save to history
                        st.session_state.query_history.append({
                            'scenario': scenario_text,
                            'country': target_country,
                            'score': readiness_score,
                            'time': elapsed
                        })
                else:
                    st.warning("Please enter a scenario")
            
            # Query history
            if st.session_state.query_history:
                with st.expander("📜 Assessment History"):
                    df = pd.DataFrame(st.session_state.query_history)
                    st.dataframe(df, use_container_width=True)
    
    # Tab 2: Data Management
    with tab2:
        st.header("Knowledge Base Management")
        
        if not st.session_state.pipeline:
            st.warning("Please initialize the pipeline first")
        else:
            # Upload files
            st.subheader("📤 Upload Documents")
            uploaded_files = st.file_uploader(
                "Upload PDF, CSV, or Excel files",
                accept_multiple_files=True,
                type=['pdf', 'csv', 'xlsx', 'xls']
            )
            
            if uploaded_files and st.button("Process Uploaded Files"):
                with st.spinner("Processing documents..."):
                    file_paths = []
                    for uploaded_file in uploaded_files:
                        # Save to temp directory
                        temp_path = Path("temp") / uploaded_file.name
                        temp_path.parent.mkdir(exist_ok=True)
                        
                        with open(temp_path, 'wb') as f:
                            f.write(uploaded_file.getbuffer())
                        
                        file_paths.append(str(temp_path))
                    
                    # Ingest
                    chunks = st.session_state.pipeline.ingest_documents(file_paths)
                    st.success(f"✓ Processed {len(uploaded_files)} files, created {chunks} chunks")
            
            st.markdown("---")
            
            # Build knowledge base
            st.subheader("🏗️ Build Knowledge Base")
            
            col1, col2 = st.columns(2)
            
            with col1:
                use_apis = st.checkbox("Fetch API Data (IMF, World Bank, EIA, Ember)")
                use_news = st.checkbox("Scrape Recent News")
            
            with col2:
                drive_folder_id = st.text_input("Google Drive Folder ID (optional)")
            
            if st.button("🚀 Build Knowledge Base", type="primary"):
                with st.spinner("Building knowledge base..."):
                    data_sources = {
                        'pdfs': [],  # Already uploaded
                        'use_apis': use_apis,
                        'use_news': use_news
                    }
                    
                    if drive_folder_id:
                        data_sources['drive_folder'] = drive_folder_id
                    
                    total_chunks = st.session_state.pipeline.build_knowledge_base(data_sources)
                    st.success(f"✓ Knowledge base built with {total_chunks} chunks")
                    
                    # Save
                    st.session_state.pipeline.save_knowledge_base("resilience_kb")
                    st.session_state.kb_loaded = True
                    st.success("✓ Knowledge base saved")
    
    # Tab 3: Search & Explore
    with tab3:
        st.header("Search Knowledge Base")
        
        if not st.session_state.pipeline or not st.session_state.kb_loaded:
            st.warning("Please load knowledge base first")
        else:
            search_query = st.text_input("Enter search query")
            
            if search_query and st.button("🔍 Search"):
                with st.spinner("Searching..."):
                    result = st.session_state.pipeline.query(
                        search_query,
                        top_k=top_k,
                        search_algorithm=search_algo,
                        reasoning_mode="simple"
                    )
                    
                    st.subheader("Results")
                    for i, doc in enumerate(result['retrieved_documents'], 1):
                        with st.expander(f"Result {i} (Score: {doc['score']:.4f})"):
                            st.markdown(f"**Source:** {doc['metadata'].get('source', 'Unknown')}")
                            st.text(doc['text'])
    
    # Tab 4: Developer Tools
    with tab4:
        st.header("Developer Tools")
        
        if not st.session_state.pipeline:
            st.warning("Please initialize pipeline first")
        else:
            # Stats
            st.subheader("📊 Pipeline Statistics")
            stats = st.session_state.pipeline.get_stats()
            st.json(stats)
            
            # Export
            st.subheader("📥 Export Data")
            if st.button("Export Knowledge Base Metadata"):
                from developer_interface import DeveloperInterface
                dev = DeveloperInterface(st.session_state.pipeline)
                dev.export_knowledge_base("kb_export.json")
                st.success("Exported to kb_export.json")
            
            # Configuration
            st.subheader("⚙️ Configuration")
            
            with st.expander("Embedding Configuration"):
                st.text(f"Model: {config.embedding.model_name}")
                st.text(f"Dimension: {config.embedding.dimension}")
                st.text(f"Batch Size: {config.embedding.batch_size}")
            
            with st.expander("LLM Configuration"):
                st.text(f"Model: {config.llm.model_name}")
                st.text(f"Temperature: {config.llm.temperature}")
                st.text(f"Max Tokens: {config.llm.max_tokens}")
            
            with st.expander("Search Configuration"):
                st.text(f"Top K: {config.search.top_k}")
                st.text(f"Algorithm: {config.search.search_algorithm}")
                st.text(f"Use Reranking: {config.search.use_reranking}")


if __name__ == "__main__":
    main()
