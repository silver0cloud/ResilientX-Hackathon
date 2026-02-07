"""
Main RAG Pipeline
Integrates document processing, embeddings, vector DB, and reasoning
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
from loguru import logger
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

from config import config
from document_processor import DocumentManager
from google_drive_client import DriveManager
from api_fetchers import APIDataManager
from news_scraper import NewsManager
from chunking import ChunkingManager, TextChunk
from embeddings import EmbeddingManager
from vector_db import VectorDBManager
from reasoning import ReasoningManager, ReasoningResult


class RAGPipeline:
    """
    Complete RAG pipeline with parallel search and reasoning
    """
    
    def __init__(self):
        # Initialize all components
        logger.info("Initializing RAG Pipeline...")
        
        self.doc_manager = DocumentManager()
        self.chunking_manager = ChunkingManager()
        self.embedding_manager = EmbeddingManager(use_cache=True)
        
        # Get embedding dimension
        embedding_dim = self.embedding_manager.get_dimension()
        
        self.vector_db_manager = VectorDBManager(dimension=embedding_dim)
        self.reasoning_manager = ReasoningManager()
        
        # Optional components
        self.drive_manager = None
        self.api_manager = None
        self.news_manager = None
        
        self.is_initialized = False
        
        logger.info("RAG Pipeline initialized successfully")
    
    def initialize_data_sources(self, use_drive: bool = False, use_apis: bool = False, 
                                use_news: bool = False):
        """Initialize optional data sources"""
        if use_drive:
            try:
                self.drive_manager = DriveManager(use_auth=True)
                logger.info("Google Drive integration enabled")
            except Exception as e:
                logger.warning(f"Google Drive init failed: {e}")
        
        if use_apis:
            self.api_manager = APIDataManager()
            logger.info("API data sources enabled")
        
        if use_news:
            self.news_manager = NewsManager()
            logger.info("News scraping enabled")
    
    def ingest_documents(self, file_paths: List[str], use_ocr: bool = True) -> int:
        """
        Ingest documents and add to vector database
        
        Args:
            file_paths: List of file paths to process
            use_ocr: Whether to use OCR for PDFs
        
        Returns:
            Number of chunks added
        """
        logger.info(f"Ingesting {len(file_paths)} documents...")
        
        all_chunks = []
        
        # Process documents
        for file_path in file_paths:
            logger.info(f"Processing: {file_path}")
            
            doc = self.doc_manager.process_document(file_path)
            if doc:
                # Chunk the document
                chunks = self.chunking_manager.contextual_chunker.chunk_document(doc)
                all_chunks.extend(chunks)
                logger.info(f"Created {len(chunks)} chunks from {Path(file_path).name}")
        
        if all_chunks:
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(all_chunks)} chunks...")
            embeddings = self.embedding_manager.embed_chunks(all_chunks, show_progress=True)
            
            # Add to vector database
            self.vector_db_manager.add_documents(all_chunks, embeddings)
            
            self.is_initialized = True
            logger.info(f"Ingestion complete: {len(all_chunks)} chunks added")
            
            return len(all_chunks)
        else:
            logger.warning("No chunks created from documents")
            return 0
    
    def ingest_from_google_drive(self, folder_id: Optional[str] = None, 
                                 sync_dir: Optional[str] = None) -> int:
        """Ingest documents from Google Drive"""
        if not self.drive_manager:
            self.initialize_data_sources(use_drive=True)
        
        if not self.drive_manager:
            logger.error("Google Drive not available")
            return 0
        
        sync_dir = sync_dir or str(config.data_dir / "google_drive")
        
        # Sync folder
        if folder_id:
            sync_result = self.drive_manager.sync_drive_folder(folder_id, sync_dir)
            logger.info(f"Synced: {sync_result.get('total_synced', 0)} files")
        else:
            # Download all files
            files = self.drive_manager.get_all_documents('all', sync_dir)
            logger.info(f"Downloaded {len(files)} files from Drive")
        
        # Get all files in sync directory
        file_paths = list(Path(sync_dir).glob('**/*'))
        file_paths = [str(f) for f in file_paths if f.is_file()]
        
        # Ingest files
        return self.ingest_documents(file_paths)
    
    def ingest_from_apis(self, countries: List[str]) -> int:
        """Fetch and ingest data from APIs"""
        if not self.api_manager:
            self.initialize_data_sources(use_apis=True)
        
        logger.info(f"Fetching API data for {len(countries)} countries...")
        
        # Fetch data
        api_data = self.api_manager.fetch_all_country_data(countries)
        
        # Convert to text
        text_data = self.api_manager.export_to_text(api_data)
        
        if text_data:
            # Chunk the text
            chunks = self.chunking_manager.chunk_text_simple(
                text_data,
                metadata={'source': 'APIs', 'type': 'structured_data'}
            )
            
            # Embed and add to DB
            embeddings = self.embedding_manager.embed_chunks(chunks)
            self.vector_db_manager.add_documents(chunks, embeddings)
            
            logger.info(f"Ingested {len(chunks)} chunks from API data")
            return len(chunks)
        
        return 0
    
    def ingest_news(self, countries: Optional[List[str]] = None) -> int:
        """Scrape and ingest news articles"""
        if not self.news_manager:
            self.initialize_data_sources(use_news=True)
        
        logger.info("Scraping news articles...")
        
        # Get news data
        news_data = self.news_manager.get_resilience_news(countries)
        
        all_chunks = []
        
        # Process metric news
        for metric, articles in news_data['metric_news'].items():
            for article in articles:
                text = article.to_text()
                metadata = {
                    'source': 'news',
                    'metric': metric,
                    'url': article.url,
                    'date': article.publish_date.isoformat() if article.publish_date else None
                }
                chunks = self.chunking_manager.chunk_text_simple(text, metadata)
                all_chunks.extend(chunks)
        
        # Process country news
        for country, articles in news_data['country_news'].items():
            for article in articles:
                text = article.to_text()
                metadata = {
                    'source': 'news',
                    'country': country,
                    'metric': article.metric,
                    'url': article.url
                }
                chunks = self.chunking_manager.chunk_text_simple(text, metadata)
                all_chunks.extend(chunks)
        
        if all_chunks:
            # Embed and add to DB
            embeddings = self.embedding_manager.embed_chunks(all_chunks)
            self.vector_db_manager.add_documents(all_chunks, embeddings)
            
            logger.info(f"Ingested {len(all_chunks)} chunks from news")
            return len(all_chunks)
        
        return 0
    
    def ingest_custom_urls(self, urls: List[str]) -> int:
        """Ingest content from custom URLs"""
        if not self.news_manager:
            self.news_manager = NewsManager()
        
        logger.info(f"Extracting content from {len(urls)} URLs...")
        
        # Extract content
        contents = self.news_manager.extract_custom_urls(urls)
        
        all_chunks = []
        for content in contents:
            if content.get('success') and content.get('text'):
                metadata = {
                    'source': 'custom_url',
                    'url': content['url'],
                    'title': content.get('title', '')
                }
                chunks = self.chunking_manager.chunk_text_simple(content['text'], metadata)
                all_chunks.extend(chunks)
        
        if all_chunks:
            embeddings = self.embedding_manager.embed_chunks(all_chunks)
            self.vector_db_manager.add_documents(all_chunks, embeddings)
            
            logger.info(f"Ingested {len(all_chunks)} chunks from URLs")
            return len(all_chunks)
        
        return 0
    
    def query(self, query_text: str, top_k: int = 5, search_algorithm: str = "hybrid",
             reasoning_mode: str = "full") -> Dict[str, Any]:
        """
        Query the RAG pipeline with parallel search and reasoning
        
        Args:
            query_text: User query
            top_k: Number of documents to retrieve
            search_algorithm: 'semantic', 'keyword', or 'hybrid'
            reasoning_mode: 'full' for 3-step reasoning, 'simple' for quick analysis
        
        Returns:
            Dict with retrieved docs and reasoning result
        """
        if not self.is_initialized:
            logger.warning("Pipeline not initialized with data")
            return {'error': 'Pipeline not initialized. Please ingest documents first.'}
        
        logger.info(f"Processing query: {query_text[:100]}...")
        
        # Embed query
        query_embedding = self.embedding_manager.embed_query(query_text)
        
        # Search vector database
        logger.info(f"Searching with {search_algorithm} algorithm...")
        retrieved_docs = self.vector_db_manager.search(
            query_embedding,
            k=top_k,
            algorithm=search_algorithm,
            query_text=query_text
        )
        
        logger.info(f"Retrieved {len(retrieved_docs)} documents")
        
        # Parallel reasoning
        logger.info(f"Starting {reasoning_mode} reasoning...")
        reasoning_result = self.reasoning_manager.process_query(
            query_text,
            retrieved_docs,
            mode=reasoning_mode
        )
        
        return {
            'query': query_text,
            'retrieved_documents': retrieved_docs,
            'reasoning': reasoning_result,
            'readiness_score': reasoning_result.readiness_score,
            'readiness_explanation': reasoning_result.readiness_explanation,
            'final_answer': reasoning_result.final_answer
        }
    
    def batch_query(self, queries: List[str], max_workers: int = 3) -> List[Dict[str, Any]]:
        """Process multiple queries in parallel"""
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_query = {
                executor.submit(self.query, query): query 
                for query in queries
            }
            
            for future in as_completed(future_to_query):
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    query = future_to_query[future]
                    logger.error(f"Query failed for '{query}': {e}")
                    results.append({'query': query, 'error': str(e)})
        
        return results
    
    def save_knowledge_base(self, name: str = "default"):
        """Save the vector database"""
        self.vector_db_manager.save(name)
        logger.info(f"Knowledge base saved: {name}")
    
    def load_knowledge_base(self, name: str = "default") -> bool:
        """Load a saved vector database"""
        success = self.vector_db_manager.load(name)
        if success:
            self.is_initialized = True
            logger.info(f"Knowledge base loaded: {name}")
        return success
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics"""
        stats = self.vector_db_manager.get_stats()
        stats['is_initialized'] = self.is_initialized
        stats['drive_enabled'] = self.drive_manager is not None
        stats['api_enabled'] = self.api_manager is not None
        stats['news_enabled'] = self.news_manager is not None
        
        return stats
    
    def reset(self):
        """Reset the pipeline (clear all data)"""
        embedding_dim = self.embedding_manager.get_dimension()
        self.vector_db_manager = VectorDBManager(dimension=embedding_dim)
        self.is_initialized = False
        logger.info("Pipeline reset")


class ResilienceAssessmentPipeline(RAGPipeline):
    """
    Specialized RAG pipeline for resilience assessment
    Includes country-specific analysis
    """
    
    def __init__(self, countries: List[str]):
        super().__init__()
        self.countries = countries
        logger.info(f"Resilience Assessment Pipeline initialized for: {', '.join(countries)}")
    
    def build_knowledge_base(self, data_sources: Dict[str, Any]):
        """
        Build knowledge base from multiple sources
        
        Args:
            data_sources: Dict with keys 'pdfs', 'drive_folder', 'use_apis', 'use_news', 'custom_urls'
        """
        total_chunks = 0
        
        # Ingest PDFs
        if 'pdfs' in data_sources and data_sources['pdfs']:
            total_chunks += self.ingest_documents(data_sources['pdfs'])
        
        # Ingest from Google Drive
        if 'drive_folder' in data_sources and data_sources['drive_folder']:
            total_chunks += self.ingest_from_google_drive(data_sources['drive_folder'])
        
        # Ingest API data
        if data_sources.get('use_apis', False):
            total_chunks += self.ingest_from_apis(self.countries)
        
        # Ingest news
        if data_sources.get('use_news', False):
            total_chunks += self.ingest_news(self.countries)
        
        # Ingest custom URLs
        if 'custom_urls' in data_sources and data_sources['custom_urls']:
            total_chunks += self.ingest_custom_urls(data_sources['custom_urls'])
        
        logger.info(f"Knowledge base built with {total_chunks} total chunks")
        return total_chunks
    
    def assess_scenario(self, scenario: str, country: Optional[str] = None) -> Dict[str, Any]:
        """
        Assess a crisis scenario's impact on resilience
        
        Args:
            scenario: Description of the crisis/shock
            country: Specific country to analyze (optional)
        
        Returns:
            Assessment with readiness scores and impacts
        """
        # Enhance query with country context if provided
        if country:
            enhanced_query = f"Analyze the impact of the following scenario on {country}'s resilience: {scenario}"
        else:
            enhanced_query = f"Analyze the resilience impact of: {scenario}"
        
        # Query the pipeline
        result = self.query(enhanced_query, top_k=10, reasoning_mode="full")
        
        return {
            'scenario': scenario,
            'country': country,
            'assessment': result['final_answer'],
            'readiness_score': result['readiness_score'],
            'readiness_explanation': result['readiness_explanation'],
            'supporting_evidence': result['retrieved_documents'][:5],
            'reasoning_details': {
                'analysis': result['reasoning'].analysis.content,
                'critique': result['reasoning'].critique.content,
                'synthesis': result['reasoning'].synthesis.content
            }
        }
    
    def compare_countries(self, scenario: str) -> Dict[str, Any]:
        """Compare how scenario affects different countries"""
        comparisons = {}
        
        for country in self.countries:
            logger.info(f"Assessing scenario for {country}...")
            assessment = self.assess_scenario(scenario, country)
            comparisons[country] = assessment
        
        return {
            'scenario': scenario,
            'country_assessments': comparisons,
            'timestamp': time.time()
        }
