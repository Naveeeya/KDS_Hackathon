"""
Handles chronological chunking of the novel.
"""

from typing import List
import pathway as pw
import pandas as pd


class NarrativeChunker:
    def __init__(self):
        pass

    def chunk_novel(self, novel_text: str) -> List[str]:
        """
        Chunks the novel text chronologically.
        Returns list of chunks.
        """
        # Simple chunking by paragraphs
        chunks = [chunk.strip() for chunk in novel_text.split('\n\n') if chunk.strip()]
        return chunks