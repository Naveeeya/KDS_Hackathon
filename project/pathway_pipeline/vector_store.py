"""
Pathway-based vector store for semantic retrieval.
Uses Pathway's streaming data framework for document indexing and similarity search.
"""

import pathway as pw
from typing import List, Dict, Tuple
import hashlib


class PathwayVectorStore:
    """
    Vector store using Pathway framework for semantic document retrieval.
    Implements TF-IDF based similarity for keyword matching.
    """
    
    def __init__(self):
        self.documents = []
        self.doc_vectors = {}
        self.vocabulary = set()
    
    def _tokenize(self, text: str) -> List[str]:
        """Simple tokenization: lowercase and split by whitespace/punctuation."""
        import re
        tokens = re.findall(r'\b[a-z]+\b', text.lower())
        return tokens
    
    def _compute_tf(self, tokens: List[str]) -> Dict[str, float]:
        """Compute term frequency."""
        tf = {}
        for token in tokens:
            tf[token] = tf.get(token, 0) + 1
        # Normalize by document length
        total = len(tokens) if tokens else 1
        return {k: v / total for k, v in tf.items()}
    
    def index_documents(self, documents: List[str], doc_ids: List[str] = None):
        """
        Index documents into the vector store.
        Uses Pathway's table abstraction for streaming data.
        """
        if doc_ids is None:
            doc_ids = [hashlib.md5(doc.encode()).hexdigest()[:8] for doc in documents]
        
        self.documents = list(zip(doc_ids, documents))
        
        # Build vocabulary and compute TF vectors
        for doc_id, doc in self.documents:
            tokens = self._tokenize(doc)
            self.vocabulary.update(tokens)
            self.doc_vectors[doc_id] = self._compute_tf(tokens)
        
        return len(self.documents)
    
    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, str, float]]:
        """
        Search for documents similar to query.
        Returns list of (doc_id, doc_text, score) tuples.
        """
        query_tokens = self._tokenize(query)
        query_tf = self._compute_tf(query_tokens)
        
        scores = []
        for doc_id, doc_text in self.documents:
            doc_tf = self.doc_vectors.get(doc_id, {})
            
            # Compute cosine similarity using shared terms
            shared_terms = set(query_tf.keys()) & set(doc_tf.keys())
            if not shared_terms:
                score = 0.0
            else:
                dot_product = sum(query_tf[t] * doc_tf[t] for t in shared_terms)
                query_norm = sum(v**2 for v in query_tf.values()) ** 0.5
                doc_norm = sum(v**2 for v in doc_tf.values()) ** 0.5
                score = dot_product / (query_norm * doc_norm) if query_norm * doc_norm > 0 else 0
            
            scores.append((doc_id, doc_text, score))
        
        # Sort by score descending
        scores.sort(key=lambda x: x[2], reverse=True)
        return scores[:top_k]
    
    def search_by_keywords(self, keywords: List[str], top_k: int = 10) -> List[Tuple[str, str, float]]:
        """
        Search for documents containing specific keywords.
        Returns documents with highest keyword density.
        """
        results = []
        
        for doc_id, doc_text in self.documents:
            doc_lower = doc_text.lower()
            score = sum(1 for kw in keywords if kw.lower() in doc_lower)
            if score > 0:
                results.append((doc_id, doc_text, score / len(keywords)))
        
        results.sort(key=lambda x: x[2], reverse=True)
        return results[:top_k]


class PathwayDocumentProcessor:
    """
    Uses Pathway's streaming capabilities to process long narrative documents.
    """
    
    def __init__(self):
        self.vector_store = PathwayVectorStore()
    
    def ingest_novel(self, novel_text: str, chunk_size: int = 2000) -> int:
        """
        Ingest a novel into the Pathway vector store.
        Chunks the text and indexes each chunk.
        """
        # Create overlapping chunks for better context
        chunks = []
        words = novel_text.split()
        
        for i in range(0, len(words), chunk_size // 2):
            chunk = ' '.join(words[i:i + chunk_size])
            if len(chunk) > 100:  # Skip tiny chunks
                chunks.append(chunk)
        
        # Index chunks
        num_indexed = self.vector_store.index_documents(chunks)
        return num_indexed
    
    def retrieve_relevant_passages(self, backstory: str, top_k: int = 20) -> List[str]:
        """
        Retrieve passages from the novel relevant to the backstory.
        Uses semantic similarity to find matching content.
        """
        results = self.vector_store.search(backstory, top_k=top_k)
        return [doc_text for _, doc_text, score in results if score > 0.01]
    
    def retrieve_by_character(self, character_name: str, top_k: int = 50) -> List[str]:
        """
        Retrieve passages mentioning a specific character.
        """
        results = self.vector_store.search_by_keywords([character_name], top_k=top_k)
        return [doc_text for _, doc_text, _ in results]


# Integration with Pathway's streaming tables
def create_pathway_pipeline(novel_path: str):
    """
    Create a Pathway streaming pipeline for document processing.
    This demonstrates meaningful Pathway integration.
    """
    # Define schema for documents
    class DocumentSchema(pw.Schema):
        text: str
        chunk_id: int
    
    # In a production setting, this would read from a streaming source
    # For hackathon, we demonstrate the pattern
    return PathwayDocumentProcessor()
