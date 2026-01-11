"""
Pathway-based ingestion of novels and backstories.
"""

import pathway as pw


class DataIngestion:
    def __init__(self):
        pass

    def ingest_novel(self, path: str) -> str:
        """
        Ingests the novel text from .txt file.
        """
        with open(path, 'r') as f:
            return f.read()

    def ingest_backstory(self, path: str) -> str:
        """
        Ingests backstory text from .txt file.
        """
        with open(path, 'r') as f:
            return f.read()