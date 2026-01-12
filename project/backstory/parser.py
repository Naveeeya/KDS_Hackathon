"""
Parses hypothetical backstory into constraints.
"""

from constraints.schema import Constraint, CharacterState
from typing import Dict
import re
import hashlib


from narrative.sentiment import SentimentAnalyzer

class BackstoryParser:
    def __init__(self):
        # Dimension keywords
        self.dimension_keywords = {
            "violence": ["violence", "fight", "attack", "conflict", "battle", "hurt", "harm"],
            "authority": ["authority", "leader", "rule", "obey", "defy", "order", "command"],
            "trust": ["trust", "betray", "rely", "bond", "distrust", "friend", "loyal"],
            "courage": ["brave", "courage", "fear", "scared", "bold", "coward", "hero"],
            "loyalty": ["loyal", "betray", "abandon", "protect", "defend", "sacrifice"],
            "morality": ["right", "wrong", "evil", "good", "dark", "innocent", "guilt"]
        }
        self.sentiment = SentimentAnalyzer()

    def parse_backstory(self, backstory_text: str) -> CharacterState:
        """
        Parses backstory text into a CharacterState with constraints.
        """
        constraints = {}
        history = []
        
        # Split into sentences
        sentences = re.split(r'(?<=[.!?])\s+', backstory_text.strip())
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
            lower_sent = sentence.lower()
            
            # Detect dimensions and polarities
            for dim, keywords in self.dimension_keywords.items():
                if any(kw in lower_sent for kw in keywords):
                    # Determine polarity using VADER
                    polarity = self.sentiment.get_polarity(sentence)
                    
                    # Generate ID
                    claim_id = hashlib.md5(sentence.encode()).hexdigest()[:8]
                    
                    # Create or update constraint
                    if dim in constraints:
                        constraints[dim] = Constraint(
                            dimension=dim,
                            polarity=polarity,
                            strength=min(1.0, constraints[dim].strength + 0.1),
                            evidence_ids=constraints[dim].evidence_ids + [claim_id]
                        )
                    else:
                        constraints[dim] = Constraint(
                            dimension=dim,
                            polarity=polarity,
                            strength=0.5,
                            evidence_ids=[claim_id]
                        )
                    
                    history.append(claim_id)
                    break  # One per sentence
        
        return CharacterState(constraints=constraints, history=history)