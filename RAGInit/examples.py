"""
Example Usage Script
Demonstrates all features of the RAG pipeline
"""

import os
from pathlib import Path
from loguru import logger

# Import pipeline components
from rag_pipeline import RAGPipeline, ResilienceAssessmentPipeline
from developer_interface import DeveloperInterface
from config import config


def example_1_basic_usage():
    """Example 1: Basic RAG pipeline usage"""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic RAG Pipeline")
    print("="*60 + "\n")
    
    # Initialize pipeline
    pipeline = RAGPipeline()
    
    # Ingest documents
    pdf_files = [
        "/mnt/user-data/uploads/PS1.pdf",
        "/mnt/user-data/uploads/Team_-_ResilientX.pdf",
        "/mnt/user-data/uploads/Tools.pdf",
        "/mnt/user-data/uploads/Expectations.pdf"
    ]
    
    print("Ingesting documents...")
    chunks_added = pipeline.ingest_documents(pdf_files, use_ocr=True)
    print(f"✓ Ingested {chunks_added} chunks from {len(pdf_files)} documents")
    
    # Save knowledge base
    pipeline.save_knowledge_base("basic_kb")
    print("✓ Knowledge base saved\n")
    
    # Query the pipeline
    query = "What are the 7 resilience metrics for country assessment?"
    print(f"Query: {query}\n")
    
    result = pipeline.query(query, top_k=5, reasoning_mode="simple")
    
    print("Answer:")
    print(result['final_answer'])
    print(f"\n✓ Query processed successfully\n")
    
    return pipeline


def example_2_resilience_assessment():
    """Example 2: Full resilience assessment pipeline"""
    print("\n" + "="*60)
    print("EXAMPLE 2: Resilience Assessment Pipeline")
    print("="*60 + "\n")
    
    # Define countries
    countries = [
        'India', 'China', 'Pakistan', 'Nepal', 'Bangladesh',
        'Sri Lanka', 'USA', 'Russia', 'Japan', 'UK'
    ]
    
    # Initialize resilience pipeline
    pipeline = ResilienceAssessmentPipeline(countries)
    
    # Build knowledge base from multiple sources
    data_sources = {
        'pdfs': [
            "/mnt/user-data/uploads/PS1.pdf",
            "/mnt/user-data/uploads/Team_-_ResilientX.pdf"
        ],
        # 'drive_folder': 'YOUR_FOLDER_ID_HERE',  # Uncomment when you have folder ID
        'use_apis': False,  # Set to True after adding API keys
        'use_news': False,  # Set to True to scrape news (takes time)
        # 'custom_urls': ['https://example.com/report']
    }
    
    print("Building knowledge base...")
    total_chunks = pipeline.build_knowledge_base(data_sources)
    print(f"✓ Knowledge base built with {total_chunks} chunks\n")
    
    # Assess a scenario
    scenario = "A regional conflict disrupts 40% of Pakistan's energy imports"
    print(f"Scenario: {scenario}\n")
    
    print("Analyzing scenario...")
    assessment = pipeline.assess_scenario(scenario, country="Pakistan")
    
    print(f"\nReadiness Score: {assessment['readiness_score']}")
    print(f"Explanation: {assessment['readiness_explanation']}")
    print(f"\n✓ Assessment complete\n")
    
    return pipeline


def example_3_multi_source_ingestion():
    """Example 3: Ingest from multiple data sources"""
    print("\n" + "="*60)
    print("EXAMPLE 3: Multi-Source Data Ingestion")
    print("="*60 + "\n")
    
    pipeline = RAGPipeline()
    
    # 1. Ingest PDFs
    print("1. Ingesting PDFs...")
    pdf_chunks = pipeline.ingest_documents([
        "/mnt/user-data/uploads/PS1.pdf"
    ])
    print(f"   ✓ {pdf_chunks} chunks from PDFs\n")
    
    # 2. Ingest custom URLs (example - won't work without real URLs)
    # print("2. Ingesting custom URLs...")
    # url_chunks = pipeline.ingest_custom_urls([
    #     "https://www.worldbank.org/en/country/india",
    #     "https://www.imf.org/en/Countries/IND"
    # ])
    # print(f"   ✓ {url_chunks} chunks from URLs\n")
    
    # 3. Stats
    stats = pipeline.get_stats()
    print("Pipeline Statistics:")
    print(f"   Total vectors: {stats['total_vectors']}")
    print(f"   Total chunks: {stats['total_chunks']}")
    print(f"   Embedding dimension: {stats['dimension']}")
    print(f"   ✓ Complete\n")
    
    return pipeline


def example_4_advanced_search():
    """Example 4: Advanced search algorithms"""
    print("\n" + "="*60)
    print("EXAMPLE 4: Advanced Search Algorithms")
    print("="*60 + "\n")
    
    # Create pipeline and load existing knowledge base
    pipeline = RAGPipeline()
    
    # Try to load existing KB, or create new one
    if not pipeline.load_knowledge_base("basic_kb"):
        print("Creating new knowledge base...")
        pipeline.ingest_documents([
            "/mnt/user-data/uploads/PS1.pdf",
            "/mnt/user-data/uploads/Tools.pdf"
        ])
    
    query = "What tools are needed for causal reasoning?"
    
    # Test different search algorithms
    print(f"Query: {query}\n")
    
    for algorithm in ['semantic', 'hybrid']:
        print(f"\n{algorithm.upper()} Search:")
        print("-" * 40)
        
        result = pipeline.query(query, top_k=3, search_algorithm=algorithm, reasoning_mode="simple")
        
        print(f"Top result: {result['retrieved_documents'][0]['text'][:150]}...")
        print(f"Relevance score: {result['retrieved_documents'][0]['score']:.4f}")
    
    print("\n✓ Search comparison complete\n")
    
    return pipeline


def example_5_developer_interface():
    """Example 5: Using the developer interface"""
    print("\n" + "="*60)
    print("EXAMPLE 5: Developer Interface")
    print("="*60 + "\n")
    
    # Initialize developer interface
    dev = DeveloperInterface()
    
    # Initialize pipeline
    countries = ['India', 'China', 'USA', 'UK']
    dev.initialize_pipeline(countries)
    
    # Ingest some data
    dev.add_data_source('pdf', '/mnt/user-data/uploads/PS1.pdf')
    
    # Get stats
    stats = dev.get_pipeline_stats()
    print("Pipeline Stats:")
    print(f"   Total vectors: {stats.get('total_vectors', 0)}")
    print(f"   Initialized: {stats.get('is_initialized', False)}\n")
    
    # Test search
    print("Testing search...")
    results = dev.test_search("resilience metrics", k=2)
    print(f"   Found {len(results)} results")
    print(f"   Top result score: {results[0]['score']:.4f}\n")
    
    # Export metadata
    dev.export_knowledge_base("kb_metadata.json")
    print("   ✓ Metadata exported\n")
    
    print("✓ Developer interface demo complete\n")
    
    return dev


def example_6_full_workflow():
    """Example 6: Complete workflow for hackathon"""
    print("\n" + "="*60)
    print("EXAMPLE 6: Full Hackathon Workflow")
    print("="*60 + "\n")
    
    # Step 1: Setup
    print("Step 1: Initialize Resilience Pipeline")
    print("-" * 40)
    countries = ['India', 'China', 'Pakistan', 'Nepal', 'Bangladesh',
                 'Sri Lanka', 'USA', 'Russia', 'Japan', 'UK']
    pipeline = ResilienceAssessmentPipeline(countries)
    print(f"✓ Initialized for {len(countries)} countries\n")
    
    # Step 2: Build Knowledge Base
    print("Step 2: Build Knowledge Base")
    print("-" * 40)
    
    data_sources = {
        'pdfs': [
            "/mnt/user-data/uploads/PS1.pdf",
            "/mnt/user-data/uploads/Team_-_ResilientX.pdf",
            "/mnt/user-data/uploads/Tools.pdf",
            "/mnt/user-data/uploads/Expectations.pdf"
        ],
        'use_apis': False,  # Enable after adding API keys
        'use_news': False   # Enable for news data
    }
    
    total_chunks = pipeline.build_knowledge_base(data_sources)
    print(f"✓ Knowledge base: {total_chunks} chunks\n")
    
    # Step 3: Save Knowledge Base
    print("Step 3: Save Knowledge Base")
    print("-" * 40)
    pipeline.save_knowledge_base("resilience_kb")
    print("✓ Knowledge base saved\n")
    
    # Step 4: Test Scenarios
    print("Step 4: Test Crisis Scenarios")
    print("-" * 40)
    
    scenarios = [
        "A cyberattack targets critical infrastructure in Japan",
        "Economic sanctions reduce China's access to energy markets",
        "Major earthquake disrupts Nepal's healthcare system"
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\nScenario {i}: {scenario}")
        assessment = pipeline.assess_scenario(scenario[:100])  # Truncate for demo
        print(f"   Readiness Score: {assessment.get('readiness_score', 'N/A')}")
        print(f"   Retrieved {len(assessment.get('supporting_evidence', []))} evidence documents")
    
    print("\n✓ Scenario testing complete\n")
    
    # Step 5: Compare Countries
    print("Step 5: Multi-Country Comparison")
    print("-" * 40)
    test_scenario = "Global pandemic affects healthcare systems"
    print(f"Scenario: {test_scenario}")
    
    # Note: This would take a long time for all countries
    # For demo, we'll just show the structure
    print("✓ Comparison framework ready\n")
    
    print("="*60)
    print("WORKFLOW COMPLETE - Ready for Hackathon!")
    print("="*60 + "\n")
    
    return pipeline


def main():
    """Main function to run examples"""
    print("\n" + "="*60)
    print("RAG PIPELINE - COMPREHENSIVE EXAMPLES")
    print("="*60)
    
    print("\nAvailable Examples:")
    print("1. Basic RAG Pipeline")
    print("2. Resilience Assessment Pipeline")
    print("3. Multi-Source Data Ingestion")
    print("4. Advanced Search Algorithms")
    print("5. Developer Interface")
    print("6. Full Hackathon Workflow")
    print("A. Run All Examples")
    
    choice = input("\nSelect example (1-6, A, or Q to quit): ").strip().upper()
    
    if choice == 'Q':
        return
    
    examples = {
        '1': example_1_basic_usage,
        '2': example_2_resilience_assessment,
        '3': example_3_multi_source_ingestion,
        '4': example_4_advanced_search,
        '5': example_5_developer_interface,
        '6': example_6_full_workflow
    }
    
    if choice == 'A':
        for func in examples.values():
            try:
                func()
            except Exception as e:
                logger.error(f"Example failed: {e}")
                print(f"\n⚠ Example failed: {e}\n")
    elif choice in examples:
        try:
            examples[choice]()
        except Exception as e:
            logger.error(f"Example failed: {e}")
            print(f"\n⚠ Example failed: {e}\n")
    else:
        print("Invalid choice")


if __name__ == "__main__":
    # Setup logging
    logger.add("examples.log", rotation="10 MB")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nExiting...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"\n⚠ Fatal error: {e}\n")
