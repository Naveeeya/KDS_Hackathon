"""
Detects meaningful experiences from narrative chunks.
"""

from constraints.schema import Experience
from typing import List
import re
import hashlib


class ExperienceDetector:
    def __init__(self):
        # Dimension keywords for detection
        self.dimension_keywords = {
            "violence": ["violence", "fight", "attack", "conflict", "battle"],
            "authority": ["authority", "leader", "rule", "obey", "defy"],
            "trust": ["trust", "betray", "rely", "bond", "distrust"]
        }

    def extract_experiences(self, text_chunk: str, chapter_id: int) -> List[Experience]:
        """
        Extracts meaningful experiences from a text chunk.
        Splits into sentences, matches keywords, creates Experience objects.
        """
        experiences = []
        # Simple sentence splitting by periods
        sentences = re.split(r'(?<=[.!?])\s+', text_chunk.strip())
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            lower_sent = sentence.lower()
            # Check for any dimension keywords
            for dim, keywords in self.dimension_keywords.items():
                if any(kw in lower_sent for kw in keywords):
                    # Generate stable ID
                    id_str = hashlib.md5(f"{chapter_id}_{sentence}".encode()).hexdigest()[:8]
                    experience = Experience(
                        id=id_str,
                        chapter_id=chapter_id,
                        event_type='general',  # Generic
                        involved_entities=[],  # TODO: Extract entities later
                        outcome=sentence,  # Simplified
                        raw_text_reference=sentence
                    )
                    experiences.append(experience)
                    break  # One per sentence
        
        return experiences

    def detect_experiences(self, chunks: List[str]) -> List[Experience]:
        """
        Processes multiple chunks to extract experiences.
        """
        all_experiences = []
        for i, chunk in enumerate(chunks):
            chapter_id = i + 1  # Assume chunks are chapters
            all_experiences.extend(self.extract_experiences(chunk, chapter_id))
        return all_experiences