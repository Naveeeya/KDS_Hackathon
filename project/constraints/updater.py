"""
Handles incremental updates to character constraints based on new experiences.
"""

from constraints.schema import CharacterState, Experience, Constraint
from typing import List


from narrative.sentiment import SentimentAnalyzer

class ConstraintUpdater:
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

    def update_state(self, experience: Experience, state: CharacterState) -> CharacterState:
        """
        Updates the character state by detecting dimensions and polarities from text.
        """
        # Append experience ID to history
        new_history = state.history + [experience.id]
        
        # Update constraints
        new_constraints = state.constraints.copy()
        text_lower = experience.raw_text_reference.lower()
        
        # Detect dimensions
        for dim, keywords in self.dimension_keywords.items():
            if any(kw in text_lower for kw in keywords):
                # Detect polarity using VADER
                polarity = self.sentiment.get_polarity(experience.raw_text_reference)
                
                if dim in new_constraints:
                    # Increase strength
                    new_constraints[dim] = Constraint(
                        dimension=dim,
                        polarity=polarity,
                        strength=min(1.0, new_constraints[dim].strength + 0.1),
                        evidence_ids=new_constraints[dim].evidence_ids + [experience.id]
                    )
                else:
                    # Create new
                    new_constraints[dim] = Constraint(
                        dimension=dim,
                        polarity=polarity,
                        strength=0.1,
                        evidence_ids=[experience.id]
                    )
        
        return CharacterState(constraints=new_constraints, history=new_history)