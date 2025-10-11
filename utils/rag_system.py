"""
RAG System using FAISS for vector similarity search.
Simple and educational implementation for CS203 lab.
"""

import os
import pickle
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np
import tempfile

# Suppress PyTorch warnings that conflict with Streamlit
import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="torch")
warnings.filterwarnings("ignore", category=FutureWarning, module="torch")
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")

# Fix tokenizers parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

try:
    import PyPDF2
except ImportError:
    PyPDF2 = None

# Lazy imports to avoid PyTorch conflicts
faiss = None
SentenceTransformer = None
CrossEncoder = None


def _lazy_imports():
    """Lazy import of heavy dependencies."""
    global faiss, SentenceTransformer,CrossEncoder
    if faiss is None:
        # Additional environment setup to prevent conflicts
        os.environ["OMP_NUM_THREADS"] = "1"
        os.environ["TOKENIZERS_PARALLELISM"] = "false"

        import faiss as _faiss  # type: ignore
        faiss = _faiss
    if SentenceTransformer is None:
        from sentence_transformers import SentenceTransformer as _ST  # type: ignore
        SentenceTransformer = _ST
    if CrossEncoder is None:
        try:
            from sentence_transformers import CrossEncoder as _CE
            CrossEncoder = _CE
        except ImportError:
            print("Warning: CrossEncoder not available. Re-ranking will be disabled.")
            CrossEncoder = None


class SimpleRAGSystem:
    """
    A simple RAG system using FAISS for vector similarity search.
    Educational implementation with clear, understandable code.
    """

    def __init__(self, data_dir: str = "rag_data", embedding_model: str = "all-MiniLM-L6-v2",reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2",
                 use_reranker: bool = True):
        """
        Initialize the RAG system.

        Args:
            data_dir: Directory to store FAISS index and metadata
            embedding_model: SentenceTransformer model name
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)

        # Lazy initialization to avoid PyTorch conflicts with Streamlit
        self.model = None
        self.reranker = None
        self.embedding_model = embedding_model
        self.reranker_model = reranker_model
        self.use_reranker = use_reranker
        self.embedding_dimension = None
        self.index = None

        # Storage for documents and metadata
        self.documents: List[str] = []
        self.metadata: List[Dict[str, Any]] = []

        # Try to load existing data
        self.load_index()

    def _ensure_model_loaded(self):
        """Lazy load the model to avoid PyTorch conflicts with Streamlit."""
        if self.model is None:
            _lazy_imports()
            print(f"Loading embedding model: {self.embedding_model}")
            self.model = SentenceTransformer(self.embedding_model)
            self.embedding_dimension = self.model.get_sentence_embedding_dimension()

            if self.index is None:
                # Initialize FAISS index (L2 distance)
                self.index = faiss.IndexFlatL2(self.embedding_dimension)

        #Load re-ranker if enabled
        if self.use_reranker and self.reranker is None:
            _lazy_imports()
            print(f"Loading re-ranker model: {self.reranker_model}")
            self.reranker = CrossEncoder(self.reranker_model)
                

    def add_text_document(self, text: str, doc_id: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Add a text document to the RAG system.
        """
        print(f"🔍 Starting add_text_document for: {doc_id}")
    
        try:
        # Step 1: Ensure model is loaded
            print("📦 Loading model...")
            self._ensure_model_loaded()
            print(f"✅ Model loaded: {self.model is not None}")
            print(f"✅ Index created: {self.index is not None}")
        
        # Step 2: Split text into chunks
            print("✂️ Chunking text...")
            chunks = self._chunk_text(text)
            print(f"✅ Created {len(chunks)} chunks")
        
        # Step 3: Process each chunk
            added_chunks = 0
            for i, chunk in enumerate(chunks):
                if len(chunk.strip()) < 10:
                    print(f"⏭️ Skipping chunk {i} (too short)")
                    continue
            
                try:
                # Create embeddings
                    print(f"🔢 Creating embedding for chunk {i}...")
                    embedding = self.model.encode([chunk])
                
                # Normalize for cosine similarity
                    faiss.normalize_L2(embedding)
                
                # Add to index
                    self.index.add(embedding.astype('float32'))
                
                # Store metadata
                    chunk_metadata = metadata.copy() if metadata else {}
                    chunk_metadata.update({
                        "doc_id": doc_id,
                        "chunk_id": f"{doc_id}_chunk_{i}",
                        "chunk_index": i
                    })
                
                    self.documents.append(chunk)
                    self.metadata.append(chunk_metadata)
                    added_chunks += 1
                    print(f"✅ Added chunk {i}")
                
                except Exception as chunk_error:
                    print(f"❌ Error processing chunk {i}: {str(chunk_error)}")
                    import traceback
                    traceback.print_exc()
        
        # Step 4: Save index
            print("💾 Saving index...")
            self.save_index()
            print("✅ Index saved")
        
            result = f"✅ Added document '{doc_id}' with {added_chunks}/{len(chunks)} chunks"
            print(result)
            return result
        
        except Exception as e:
            error_msg = f"❌ Error adding document '{doc_id}': {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return error_msg

    def add_pdf_document(self, pdf_path: str, doc_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None):
        """
        Add a PDF document to the RAG system.

        Args:
            pdf_path: Path to the PDF file
            doc_id: Optional document ID (uses filename if not provided)
            metadata: Optional metadata dictionary
        """

        if PyPDF2 is None:
            return "Error: PyPDF2 not installed. Please install with: pip install PyPDF2"

        try:
            # Extract text from PDF
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    if 'abstract' in page.extract_text().lower() or 'บทคัดย่อ' in page.extract_text() or 'กิตติกรรมประกาศ' in page.extract_text() or 'สารบัญ' in page.extract_text():
                        continue

                    if 'reference' in page.extract_text().lower() or 'เอกสารอ้างอิง' in page.extract_text():
                        break
                        
                    text += page.extract_text() + "\n"

            # Use filename as doc_id if not provided
            if doc_id is None:
                doc_id = Path(pdf_path).stem

            # Add metadata about the PDF
            pdf_metadata = metadata.copy() if metadata else {}
            pdf_metadata.update({
                "source_type": "pdf",
                "source_path": pdf_path,
                "num_pages": len(pdf_reader.pages)
            })
            return self.add_text_document(text, doc_id, pdf_metadata)

        except Exception as e:
            return f"Error processing PDF: {str(e)}"

    def search(self, query: str, n_results: int = 5, use_reranker: Optional[bool] = None) -> List[Dict[str, Any]]:
        """
        Search for relevant documents using FAISS

        Args:
            query: Search query text
            n_results: Number of results to return

        Returns:
            List of search results with content and metadata
        """
        try:
            if len(self.documents) == 0:
                return [{"error": "No documents in the system"}]

            # Ensure model is loaded
            self._ensure_model_loaded()

            # Determine whether to use re-ranker
            should_rerank = use_reranker if use_reranker is not None else self.use_reranker

            # Step 1: Initial retrieval (get more candidates for re-ranking)
            initial_k = n_results * 3 if should_rerank else n_results
            initial_k = min(initial_k, len(self.documents))

            # Create embedding for query
            query_embedding = self.model.encode([query])
            # Normalize for cosine similarity
            faiss.normalize_L2(query_embedding)

            scores, indices = self.index.search(
                query_embedding.astype('float32'), initial_k)

            # Search using FAISS
            candidates = []
            for score, idx in zip(scores[0], indices[0]):
                if idx >= 0:
                    candidates.append({
                        "content": self.documents[idx],
                        "metadata": self.metadata[idx],
                        "initial_score": float(score),
                        "index": int(idx)
                    })

            # Step 2: Re-rank if enabled
            if should_rerank and self.reranker is not None and candidates:
                print(f"Re-ranking {len(candidates)} candidates...")
                
                # Prepare query-document pairs for re-ranker
                pairs = [[query, candidate["content"]] for candidate in candidates]
                
                # Get re-ranking scores
                rerank_scores = self.reranker.predict(pairs)
                
                # Add re-ranking scores and sort
                for candidate, rerank_score in zip(candidates, rerank_scores):
                    candidate["rerank_score"] = float(rerank_score)
                
                # Sort by re-ranking score (higher is better for cross-encoder)
                candidates.sort(key=lambda x: x["rerank_score"], reverse=True)
                
                # Take top n_results
                candidates = candidates[:n_results]
                
                # Add final rank
                for i, candidate in enumerate(candidates):
                    candidate["rank"] = i + 1
                    candidate["score"] = candidate["rerank_score"]  # Use rerank score as final score
            else:
                # No re-ranking, just take top n_results and use initial scores
                candidates = candidates[:n_results]
                for i, candidate in enumerate(candidates):
                    candidate["rank"] = i + 1
                    candidate["score"] = candidate["initial_score"]

            # Clean up results
            search_results = []
            for candidate in candidates:
                result = {
                    "content": candidate["content"],
                    "metadata": candidate["metadata"],
                    "score": candidate["score"],
                    "rank": candidate["rank"]
                }
                if should_rerank and "rerank_score" in candidate:
                    result["rerank_score"] = candidate["rerank_score"]
                    result["initial_score"] = candidate["initial_score"]
                
                search_results.append(result)

            return search_results

        except Exception as e:
            return [{"error": f"Search failed: {str(e)}"}]


    def get_context_for_query(self, query: str, max_context_length: int = 2000, use_reranker: Optional[bool] = None) -> str:
        """
        Get relevant context for a query, formatted for LLM consumption.

        Args:
            query: The user's query
            max_context_length: Maximum length of context to return

        Returns:
            Formatted context string
        """
        search_results = self.search(query, n_results=5, use_reranker=use_reranker)

        if not search_results or "error" in search_results[0]:
            return "No relevant context found."

        context_parts = []
        current_length = 0

        for result in search_results:
            if "error" in result:
                continue

            content = result["content"]
            metadata = result.get("metadata", {})
            doc_id = metadata.get("doc_id", "unknown")
            score = result.get("score", 0)

            # Format the context piece
            context_piece = f"[Source: {doc_id} | Relevance: {score:.3f}]\n{content}\n"

            # Check if adding this piece would exceed the limit
            if current_length + len(context_piece) > max_context_length:
                break

            context_parts.append(context_piece)
            current_length += len(context_piece)

        if context_parts:
            return "Relevant context:\n\n" + "\n---\n".join(context_parts)
        else:
            return "No relevant context found."

    def list_documents(self) -> List[Dict[str, Any]]:
        """List all documents in the RAG system with their metadata."""
        doc_info = {}

        # Group chunks by document ID
        for i, meta in enumerate(self.metadata):
            doc_id = meta.get('doc_id', f'unknown_{i}')
            if doc_id not in doc_info:
                doc_info[doc_id] = {
                    'doc_id': doc_id,
                    'chunks': 0,
                    'metadata': meta.copy()
                }
                # Remove chunk-specific metadata for display
                doc_info[doc_id]['metadata'].pop('chunk_id', None)
                doc_info[doc_id]['metadata'].pop('chunk_index', None)

            doc_info[doc_id]['chunks'] += 1

        return list(doc_info.values())

    def delete_document(self, doc_id: str) -> str:
        """Delete a document and all its chunks from the RAG system."""
        try:
            # Find indices of chunks belonging to this document
            indices_to_remove = []
            for i, meta in enumerate(self.metadata):
                if meta.get('doc_id') == doc_id:
                    indices_to_remove.append(i)

            if not indices_to_remove:
                return f"Document '{doc_id}' not found"

            # Remove chunks in reverse order to maintain indices
            for i in sorted(indices_to_remove, reverse=True):
                del self.documents[i]
                del self.metadata[i]

            # Rebuild the FAISS index
            self._rebuild_index()

            # Save the updated data
            self.save_index()

            return f"Successfully deleted document '{doc_id}' ({len(indices_to_remove)} chunks)"

        except Exception as e:
            return f"Error deleting document '{doc_id}': {str(e)}"

    def _rebuild_index(self):
        """Rebuild the FAISS index from current documents."""
        if not self.documents:
            # Create empty index if no documents
            self._ensure_model_loaded()
            self.index = faiss.IndexFlatL2(
                self.embedding_dimension)  # type: ignore
            return

        # Ensure model is loaded
        self._ensure_model_loaded()

        # Create new index
        self.index = faiss.IndexFlatL2(
            self.embedding_dimension)  # type: ignore

        # Generate embeddings for all documents
        embeddings = self.model.encode(self.documents)
        # Normalize for cosine similarity
        faiss.normalize_L2(embeddings)  # type: ignore
        # Add to index
        self.index.add(embeddings.astype('float32'))  # type: ignore

    def _chunk_text(self, text: str, chunk_size: int = 350, overlap: int = 35) -> List[str]:
        """
        Split text into overlapping chunks.

        Args:
            text: Input text to chunk
            chunk_size: Target size of each chunk
            overlap: Number of characters to overlap between chunks

        Returns:
            List of text chunks
        """
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size

            # Try to end at a sentence boundary
            if end < len(text):
                # Look for sentence endings near the chunk boundary
                for i in range(end, max(start + chunk_size - 100, start), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break

            while end < len(text) and text[end] != ' ':
                end += 1

            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)

            start = end - overlap

            while start >= 0 and start < len(text) and text[start] != ' ':
                start -= 1

            # Prevent infinite loops
            if start >= end:
                start = end

        return chunks

    def save_index(self):
        """Save the FAISS index and metadata to disk."""
        try:
            if self.index is not None:
                # Save FAISS index
                index_path = self.data_dir / "faiss_index.bin"
                faiss.write_index(self.index, str(index_path))

            # Save documents and metadata
            data_path = self.data_dir / "documents.pkl"
            with open(data_path, 'wb') as f:
                pickle.dump({
                    'documents': self.documents,
                    'metadata': self.metadata,
                    'embedding_dimension': self.embedding_dimension,
                    'embedding_model': self.embedding_model,
                    'reranker_model': self.reranker_model,
                    'use_reranker': self.use_reranker
                }, f)

        except Exception as e:
            print(f"Error saving index: {e}")

    def load_index(self):
        """Load the FAISS index and metadata from disk."""
        try:
            index_path = self.data_dir / "faiss_index.bin"
            data_path = self.data_dir / "documents.pkl"

            if data_path.exists():
                # Load documents and metadata
                with open(data_path, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data.get('documents', [])
                    self.metadata = data.get('metadata', [])
                    self.embedding_dimension = data.get('embedding_dimension')
                    saved_model = data.get('embedding_model')
                    self.reranker_model = data.get('reranker_model', self.reranker_model)
                    self.use_reranker = data.get('use_reranker', self.use_reranker)

                    # Check if model changed
                    if saved_model != self.embedding_model:
                        print(
                            f"Model changed from {saved_model} to {self.embedding_model}")
                        return

                # Load FAISS index if it exists
                if index_path.exists() and self.embedding_dimension:
                    _lazy_imports()
                    self.index = faiss.read_index(str(index_path))
                    print(f"Loaded {len(self.documents)} documents from disk")

        except Exception as e:
            print(f"Error loading index: {e}")
            self.documents = []
            self.metadata = []

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the RAG system."""
        doc_ids = set()
        for meta in self.metadata:
            if 'doc_id' in meta:
                doc_ids.add(meta['doc_id'])

        return {
            "total_chunks": len(self.documents),
            "total_documents": len(doc_ids),
            "embedding_model": self.embedding_model,
            "reranker_model": self.reranker_model,
            "use_reranker": self.use_reranker,
            "embedding_dimension": self.embedding_dimension,
            "has_index": self.index is not None,
            "data_directory": str(self.data_dir)
        }


def load_sample_documents(rag_system: SimpleRAGSystem, data_dir: str = "./data"):
    """
    Load sample documents into the RAG system for testing.
    """
    data_path = Path(data_dir)
    if not data_path.exists():
        print(f"Sample data directory {data_dir} not found")
        return

    # Load sample text documents
    for txt_file in data_path.glob("*.txt"):
        print(f"Loading {txt_file.name}...")
        with open(txt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        rag_system.add_text_document(
            content,
            txt_file.stem,
            {"source_type": "text", "source_path": str(txt_file)}
        )

    # Load sample PDF documents
    for pdf_file in data_path.glob("*.pdf"):
        print(f"Loading {pdf_file.name}...")
        rag_system.add_pdf_document(str(pdf_file))

    print("Sample documents loaded!")


def load_sample_documents_for_demo(rag_system: SimpleRAGSystem, data_dir: str = "./data"):
    """Load sample documents for demonstration"""
    data_path = Path(data_dir)
    data_path.mkdir(exist_ok=True)

    # Create sample documents
    sample_docs = [
        {
            "id": "insomnia",
            "title": "the disorder that make you hard to sleep",
            "content": """
            Insomnia is the most common sleep disorder affecting the population and is the most common
            disease encountered in the practice of sleep medicine.Insomniacs complain of difficulty initiating and
            maintaining sleep, including early morning awakening and non-restorative sleep occurring 3-4 times per week
            persisting for more than a month and associated with an impairment of daytime function. Acute insomnia may
            be associated with an identifiable stressful situation. Most cases of insomnia are chronic and co-morbid
            with other conditions which include psychiatric, medical and neurological disorders or drug and alcohol
            abuse31. In some cases, no cause is found and the condition is labelled idiopathic or primary insomnia or
            psychophysiological insomnia.
            """
        },
        
    ]

    for doc in sample_docs:
        rag_system.add_text_document(
            text=doc["content"],
            doc_id=doc["id"],
            metadata={"title": doc["title"], "type": "sample_document"}
        )

    return f"Loaded {len(sample_docs)} sample documents into RAG system"


# Example usage
if __name__ == "__main__":
    # Create RAG system
    rag = SimpleRAGSystem()
    load_sample_documents(rag,'./data')
    # Add some sample text
    #add_text_document(self, text: str, doc_id: str, metadata: Optional[Dict[str, Any]] = None)
    #add_pdf_document(self, pdf_path: str, doc_id: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None)
    # rag.add_pdf_document(
    #     "/home/dana456/Desktop/PROJECT-LLM/rag_data/ibyt10i2p126.pdf",
    #     "sleeping disorder",
    #     {"topic": "sleeping disorder"}
    # )

    # Search for relevant content
    # results = rag.search("sleep", n_results=3)
    # for result in results:
    #     print(f"Score: {result['score']:.3f}")
    #     print(f"Content: {result['content'][:100]}...")
    #     print(f"Metadata: {result['metadata']}")
    #     print()
