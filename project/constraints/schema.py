"""
Defines the core data structures for experiences,
constraints, and character states.
"""

from typing import Dict, List
from dataclasses import dataclass


@dataclass
class Experience:
    id: str
    chapter_id: int
    event_type: str  # e.g., 'decision', 'loss', 'conflict', 'belief', 'action'
    involved_entities: List[str]
    outcome: str
    raw_text_reference: str


@dataclass
class Constraint:
    dimension: str  # e.g., 'violence', 'trust', 'authority'
    polarity: str  # 'positive', 'negative', 'neutral'
    strength: float  # 0.0 - 1.0
    evidence_ids: List[str]


@dataclass
class CharacterState:
    constraints: Dict[str, Constraint]
    history: List[str]  # experience IDs
