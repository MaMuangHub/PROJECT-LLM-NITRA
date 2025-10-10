"""
Improved utility modules for NITRA application
"""

# ========== security.py ==========
import re
import hashlib
from typing import Optional
import secrets

class SecurityManager:
    """Manage security aspects of the application"""
    
    def __init__(self):
        self.injection_patterns = [
            r"<script.*?>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"eval\s*\(",
            r"exec\s*\(",
            r"__import__",
            r"subprocess",
            r"os\.system",
        ]
    
    def detect_injection(self, text: str) -> bool:
        """Detect potential injection attacks"""
        for pattern in self.injection_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def generate_session_id(self) -> str:
        """Generate secure session ID"""
        return secrets.token_urlsafe(32)
    
    def hash_api_key(self, key: str) -> str:
        """Hash API key for secure storage"""
        return hashlib.sha256(key.encode()).hexdigest()


class InputValidator:
    """Validate and sanitize user inputs"""
    
    def sanitize(self, text: str) -> str:
        """Sanitize user input"""
        # Remove control characters
        text = ''.join(char for char in text if char.isprintable() or char.isspace())
        
        # Strip excessive whitespace
        text = ' '.join(text.split())
        
        # Escape HTML
        text = text.replace('<', '&lt;').replace('>', '&gt;')
        
        return text.strip()
    
    def validate_length(self, text: str, max_length: int) -> bool:
        """Validate text length"""
        return len(text) <= max_length


# ========== language_detector.py ==========
from typing import Dict, Optional
import re
from sentence_transformers import SentenceTransformer
import numpy as np

class LanguageDetector:
    """Improved language detection and topic classification"""
    
    def __init__(self):
        self.model = None
        self.sleep_embeddings = None
        self._initialize_embeddings()
    
    def _initialize_embeddings(self):
        """Lazy load embeddings model"""
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Pre-compute sleep topic embeddings
            sleep_terms = [
                "sleep", "insomnia", "sleeping disorder", "sleep quality", "rest",
                "dream", "nightmare", "snoring", "sleep apnea", "circadian rhythm",
                "melatonin", "sleep cycle", "REM sleep", "deep sleep", "sleep deprivation",
                "นอน", "หลับ", "นอนไม่หลับ", "ฝัน", "กรน", "พักผ่อน"
            ]
            
            self.sleep_embeddings = self.model.encode(sleep_terms)
        except:
            pass
    
    def detect(self, text: str) -> str:
        """Detect language of text"""
        # Thai character range
        if re.search(r'[\u0E00-\u0E7F]', text):
            return "Thai"
        return "English"
    
    def is_topic_related(self, query: str, topic: str = "sleep", threshold: float = 0.3) -> bool:
        """Check if query is related to a topic using semantic similarity"""
        if not self.model or self.sleep_embeddings is None:
            # Fallback to keyword matching
            return self._keyword_based_detection(query)
        
        try:
            # Compute query embedding
            query_embedding = self.model.encode([query])
            
            # Calculate similarities
            similarities = np.dot(self.sleep_embeddings, query_embedding.T).flatten()
            max_similarity = np.max(similarities)
            
            return max_similarity > threshold
        except:
            return self._keyword_based_detection(query)
    
    def _keyword_based_detection(self, query: str) -> bool:
        """Fallback keyword-based detection"""
        sleep_keywords = [
            'sleep', 'insomnia', 'dream', 'snore', 'rest', 'bed', 'wake',
            'นอน', 'หลับ', 'ฝัน', 'กรน', 'พักผ่อน'
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in sleep_keywords)


# ========== performance_monitor.py ==========
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

class PerformanceMonitor:
    """Monitor application performance"""
    
    def __init__(self, log_file: str = "performance.jsonl"):
        self.log_file = Path(log_file)
    
    def log_metrics(self, metrics: Dict[str, Any]):
        """Log performance metrics"""
        try:
            entry = {
                "timestamp": datetime.now().isoformat(),
                **metrics
            }
            
            with open(self.log_file, "a") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            print(f"Error logging metrics: {e}")
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get summary of performance metrics"""
        try:
            if not self.log_file.exists():
                return {}
            
            metrics = []
            with open(self.log_file, "r") as f:
                for line in f:
                    metrics.append(json.loads(line))
            
            if not metrics:
                return {}
            
            # Calculate summary
            total_queries = sum(m.get("total_queries", 0) for m in metrics)
            avg_response_time = np.mean([m.get("avg_response_time", 0) for m in metrics])
            
            return {
                "total_queries_all_time": total_queries,
                "avg_response_time_all_time": avg_response_time,
                "last_updated": metrics[-1].get("timestamp")
            }
        except:
            return {}


# ========== cache_manager.py ==========
import pickle
import time
from pathlib import Path
from typing import Any, Optional

class CacheManager:
    """Manage application caching"""
    
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.memory_cache = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        # Check memory cache first
        if key in self.memory_cache:
            entry = self.memory_cache[key]
            if entry["expiry"] > time.time():
                return entry["value"]
            else:
                del self.memory_cache[key]
        
        # Check disk cache
        cache_file = self.cache_dir / f"{key}.pkl"
        if cache_file.exists():
            try:
                with open(cache_file, "rb") as f:
                    entry = pickle.load(f)
                    if entry["expiry"] > time.time():
                        # Load to memory cache
                        self.memory_cache[key] = entry
                        return entry["value"]
                    else:
                        cache_file.unlink()
            except:
                pass
        
        return None
    
    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL"""
        entry = {
            "value": value,
            "expiry": time.time() + ttl
        }
        
        # Set in memory cache
        self.memory_cache[key] = entry
        
        # Persist to disk
        cache_file = self.cache_dir / f"{key}.pkl"
        try:
            with open(cache_file, "wb") as f:
                pickle.dump(entry, f)
        except:
            pass
    
    def clear(self):
        """Clear all cache"""
        self.memory_cache.clear()
        for cache_file in self.cache_dir.glob("*.pkl"):
            cache_file.unlink()


# ========== improved_llm_client.py ==========
import os
from typing import Dict, List, Any, Optional
import litellm
from dotenv import load_dotenv
import time
import logging

load_dotenv()
logger = logging.getLogger(__name__)

class ImprovedLLMClient:
    """Improved LLM client with retry logic and error handling"""
    
    def __init__(
        self, 
        model: Optional[str] = None, 
        temperature: float = 0.7, 
        max_tokens: int = 1000,
        retry_attempts: int = 3,
        retry_delay: float = 1.0
    ):
        self.model = model or os.getenv("DEFAULT_MODEL", "gpt-3.5-turbo")
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        
        self._setup_api_keys()
    
    def _setup_api_keys(self):
        """Setup API keys securely"""
        api_keys = {
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
            "ANTHROPIC_API_KEY": os.getenv("ANTHROPIC_API_KEY"),
            "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY"),
            "GROQ_API_KEY": os.getenv("GROQ_API_KEY")
        }
        
        for key, value in api_keys.items():
            if value:
                os.environ[key] = value
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Send chat request with retry logic"""
        for attempt in range(self.retry_attempts):
            try:
                response = litellm.completion(
                    model=self.model,
                    messages=messages,
                    temperature=kwargs.get('temperature', self.temperature),
                    max_tokens=kwargs.get('max_tokens', self.max_tokens),
                    timeout=30,
                    **kwargs
                )
                return response.choices[0].message.content
                
            except Exception as e:
                logger.warning(f"LLM request attempt {attempt + 1} failed: {str(e)}")
                
                if attempt < self.retry_attempts - 1:
                    time.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                else:
                    logger.error(f"All LLM request attempts failed: {str(e)}")
                    return f"I apologize, but I'm having trouble processing your request. Please try again."


# ========== improved_rag_system.py ==========
import os
import pickle
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer, CrossEncoder
import hashlib
import logging

logger = logging.getLogger(__name__)

class ImprovedRAGSystem:
    """Improved RAG system with better performance and error handling"""
    
    def __init__(
        self,
        data_dir: str = "rag_data",
        embedding_model: str = "all-MiniLM-L6-v2",
        reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
        use_reranker: bool = True,
        cache_embeddings: bool = True
    ):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        self.embedding_model_name = embedding_model
        self.reranker_model_name = reranker_model
        self.use_reranker = use_reranker
        self.cache_embeddings = cache_embeddings
        
        self.model = None
        self.reranker = None
        self.index = None
        self.embedding_dimension = None
        
        self.documents: List[str] = []
        self.metadata: List[Dict[str, Any]] = []
        self.embedding_cache = {}
        
        self.load_index()
    
    def _ensure_models_loaded(self):
        """Lazy load models"""
        if self.model is None:
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.model = SentenceTransformer(self.embedding_model_name)
            self.embedding_dimension = self.model.get_sentence_embedding_dimension()
            
            if self.index is None:
                self.index = faiss.IndexFlatL2(self.embedding_dimension)
        
        if self.use_reranker and self.reranker is None:
            logger.info(f"Loading reranker model: {self.reranker_model_name}")
            try:
                self.reranker = CrossEncoder(self.reranker_model_name)
            except Exception as e:
                logger.warning(f"Failed to load reranker: {e}")
                self.use_reranker = False
    
    def add_text_document(
        self,
        text: str,
        doc_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        batch_size: int = 32
    ):
        """Add text document with batch processing"""
        self._ensure_models_loaded()
        
        try:
            # Chunk text
            chunks = self._smart_chunk_text(text)
            
            # Batch encode for efficiency
            embeddings = []
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                batch_embeddings = self.model.encode(batch, show_progress_bar=False)
                embeddings.extend(batch_embeddings)
            
            # Normalize embeddings
            embeddings = np.array(embeddings).astype('float32')
            faiss.normalize_L2(embeddings)
            
            # Add to index
            self.index.add(embeddings)
            
            # Store documents and metadata
            for i, chunk in enumerate(chunks):
                chunk_metadata = metadata.copy() if metadata else {}
                chunk_metadata.update({
                    "doc_id": doc_id,
                    "chunk_id": f"{doc_id}_chunk_{i}",
                    "chunk_index": i
                })
                
                self.documents.append(chunk)
                self.metadata.append(chunk_metadata)
            
            self.save_index()
            logger.info(f"Added document '{doc_id}' with {len(chunks)} chunks")
            return f"Successfully added document '{doc_id}' with {len(chunks)} chunks"
            
        except Exception as e:
            logger.error(f"Error adding document: {e}")
            return f"Error adding document: {str(e)}"
    
    def _smart_chunk_text(
        self,
        text: str,
        chunk_size: int = 400,
        overlap: int = 50,
        min_chunk_size: int = 100
    ) -> List[str]:
        """Improved text chunking with sentence boundaries"""
        if len(text) <= chunk_size:
            return [text] if len(text) >= min_chunk_size else []
        
        # Split by sentences first
        sentences = text.replace('!', '.').replace('?', '.').split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            if current_length + sentence_length <= chunk_size:
                current_chunk.append(sentence)
                current_length += sentence_length
            else:
                if current_chunk:
                    chunk_text = '. '.join(current_chunk) + '.'
                    if len(chunk_text) >= min_chunk_size:
                        chunks.append(chunk_text)
                
                # Start new chunk with overlap
                if overlap > 0 and current_chunk:
                    overlap_sentences = []
                    overlap_length = 0
                    for s in reversed(current_chunk):
                        if overlap_length + len(s) <= overlap:
                            overlap_sentences.insert(0, s)
                            overlap_length += len(s)
                        else:
                            break
                    current_chunk = overlap_sentences + [sentence]
                    current_length = overlap_length + sentence_length
                else:
                    current_chunk = [sentence]
                    current_length = sentence_length
        
        # Add remaining chunk
        if current_chunk:
            chunk_text = '. '.join(current_chunk) + '.'
            if len(chunk_text) >= min_chunk_size:
                chunks.append(chunk_text)
        
        return chunks
    
    def search(
        self,
        query: str,
        n_results: int = 5,
        use_reranker: Optional[bool] = None
    ) -> List[Dict[str, Any]]:
        """Improved search with caching"""
        if not self.documents:
            return []
        
        self._ensure_models_loaded()
        
        # Check cache
        cache_key = hashlib.md5(f"{query}_{n_results}".encode()).hexdigest()
        if self.cache_embeddings and cache_key in self.embedding_cache:
            return self.embedding_cache[cache_key]
        
        try:
            # Encode query
            query_embedding = self.model.encode([query], show_progress_bar=False)
            faiss.normalize_L2(query_embedding)
            
            # Search
            k = min(n_results * 3 if self.use_reranker else n_results, len(self.documents))
            scores, indices = self.index.search(query_embedding.astype('float32'), k)
            
            # Build results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0 and idx < len(self.documents):
                    results.append({
                        "content": self.documents[idx],
                        "metadata": self.metadata[idx],
                        "score": float(score),
                        "index": int(idx)
                    })
            
            # Rerank if enabled
            if self.use_reranker and self.reranker and results:
                pairs = [[query, r["content"]] for r in results]
                rerank_scores = self.reranker.predict(pairs)
                
                for result, rerank_score in zip(results, rerank_scores):
                    result["rerank_score"] = float(rerank_score)
                
                results.sort(key=lambda x: x.get("rerank_score", 0), reverse=True)
                results = results[:n_results]
            
            # Cache results
            if self.cache_embeddings:
                self.embedding_cache[cache_key] = results
            
            return results
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def get_context_for_query(
        self,
        query: str,
        max_context_length: int = 2000,
        use_reranker: Optional[bool] = None
    ) -> str:
        """Get formatted context for query"""
        results = self.search(query, n_results=5, use_reranker=use_reranker)
        
        if not results:
            return "No relevant context found."
        
        context_parts = []
        current_length = 0
        
        for result in results:
            content = result["content"]
            doc_id = result.get("metadata", {}).get("doc_id", "unknown")
            
            context_piece = f"[Source: {doc_id}]\n{content}\n"
            
            if current_length + len(context_piece) > max_context_length:
                break
            
            context_parts.append(context_piece)
            current_length += len(context_piece)
        
        return "\n---\n".join(context_parts) if context_parts else "No relevant context found."
    
    def save_index(self):
        """Save index and data"""
        try:
            if self.index:
                faiss.write_index(self.index, str(self.data_dir / "faiss_index.bin"))
            
            with open(self.data_dir / "data.pkl", 'wb') as f:
                pickle.dump({
                    'documents': self.documents,
                    'metadata': self.metadata,
                    'embedding_dimension': self.embedding_dimension
                }, f)
            
        except Exception as e:
            logger.error(f"Error saving index: {e}")
    
    def load_index(self):
        """Load index and data"""
        try:
            index_path = self.data_dir / "faiss_index.bin"
            data_path = self.data_dir / "data.pkl"
            
            if data_path.exists():
                with open(data_path, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data.get('documents', [])
                    self.metadata = data.get('metadata', [])
                    self.embedding_dimension = data.get('embedding_dimension')
                
                if index_path.exists() and self.embedding_dimension:
                    self.index = faiss.read_index(str(index_path))
                    logger.info(f"Loaded {len(self.documents)} documents")
                    
        except Exception as e:
            logger.error(f"Error loading index: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        doc_ids = set(m.get('doc_id') for m in self.metadata if 'doc_id' in m)
        
        return {
            "total_documents": len(doc_ids),
            "total_chunks": len(self.documents),
            "cache_size": len(self.embedding_cache),
            "index_loaded": self.index is not None
        }


# ========== improved_search_tools.py ==========
import requests
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class ImprovedWebSearchTool:
    """Improved web search with better error handling"""
    
    def __init__(self):
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
    
    def search(
        self,
        query: str,
        num_results: int = 5,
        timeout: int = 10
    ) -> List[Dict[str, Any]]:
        """Search with automatic fallback"""
        
        # Try Serper first
        if self.serper_api_key:
            results = self._search_serper(query, num_results, timeout)
            if results:
                return results
        
        # Fallback to Tavily
        if self.tavily_api_key:
            results = self._search_tavily(query, num_results, timeout)
            if results:
                return results
        
        logger.warning("No search API available")
        return []
    
    def _search_serper(
        self,
        query: str,
        num_results: int,
        timeout: int
    ) -> List[Dict[str, Any]]:
        """Search using Serper API"""
        try:
            response = requests.post(
                "https://google.serper.dev/search",
                json={"q": query, "num": num_results},
                headers={"X-API-KEY": self.serper_api_key},
                timeout=timeout
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get("organic", []):
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                    "link": item.get("link", "")
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Serper search error: {e}")
            return []
    
    def _search_tavily(
        self,
        query: str,
        num_results: int,
        timeout: int
    ) -> List[Dict[str, Any]]:
        """Search using Tavily API"""
        try:
            response = requests.post(
                "https://api.tavily.com/search",
                json={
                    "api_key": self.tavily_api_key,
                    "query": query,
                    "max_results": num_results
                },
                timeout=timeout
            )
            response.raise_for_status()
            
            data = response.json()
            results = []
            
            for item in data.get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "snippet": item.get("content", ""),
                    "link": item.get("url", "")
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Tavily search error: {e}")
            return []


# Export functions
def get_available_models() -> List[str]:
    """Get available LLM models"""
    return [
        "gpt-3.5-turbo",
        "gpt-4",
        "gpt-4-turbo-preview",
        "groq/llama-3.3-70b-versatile"
    ]

def load_sample_documents(rag_system: ImprovedRAGSystem):
    """Load sample documents"""
    sample_docs = [
        {
            "id": "sleep_basics",
            "content": """Sleep is a naturally recurring state of mind and body, characterized by altered consciousness, 
            relatively inhibited sensory activity, reduced muscle activity and reduced interactions with surroundings. 
            Adults need 7-9 hours of sleep per night. Good sleep hygiene includes maintaining a consistent sleep schedule, 
            creating a comfortable sleep environment, and avoiding screens before bedtime."""
        },
        {
            "id": "insomnia",
            "content": """Insomnia is a sleep disorder where people have trouble sleeping. They may have difficulty 
            falling asleep, or staying asleep as long as desired. Insomnia is typically followed by daytime sleepiness, 
            low energy, irritability, and a depressed mood. Treatment includes cognitive behavioral therapy, sleep hygiene 
            improvements, and sometimes medication under medical supervision."""
        }
    ]
    
    for doc in sample_docs:
        rag_system.add_text_document(
            text=doc["content"],
            doc_id=doc["id"],
            metadata={"type": "sample"}
        )
    
    return f"Loaded {len(sample_docs)} sample documents"