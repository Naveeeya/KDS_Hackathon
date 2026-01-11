"""
Retrieves evidence snippets using keyword search.
"""

from typing import List


class EvidenceRetriever:
    def __init__(self):
        pass

    def retrieve_snippets(self, query: str, chunks: List[str], top_k: int = 3) -> List[str]:
        """
        Retrieves relevant text snippets for a query using keyword matching.
        """
        # Filter chunks containing the query (case-insensitive)
        matching = [chunk for chunk in chunks if query.lower() in chunk.lower()]
        
        # Return top_k snippets
        return matching[:top_k]