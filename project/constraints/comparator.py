"""
Compares constraints from story and backstory for compatibility.
"""

from typing import Dict
from constraints.schema import Constraint, CharacterState


class ConstraintComparator:
    def __init__(self):
        pass

    def compare(self, story_state: CharacterState, backstory_state: CharacterState) -> Dict:
        """
        Compares constraints and returns a decision with conflicts and explanation.
        """
        conflicts = []
        checked_dimensions = []
        
        for dim in story_state.constraints:
            if dim in backstory_state.constraints:
                checked_dimensions.append(dim)
                story_con = story_state.constraints[dim]
                back_con = backstory_state.constraints[dim]
                print(f"dim {dim}, story {story_con.polarity}, back {back_con.polarity}")
                if story_con.polarity != back_con.polarity:
                    # Calculate severity
                    max_strength = max(story_con.strength, back_con.strength)
                    if max_strength >= 0.5:
                        severity = "high"
                    else:
                        severity = "medium"
                    
                    conflicts.append({
                        "dimension": dim,
                        "severity": severity,
                        "trigger_rule": "polarity_mismatch",
                        "story_constraint": {
                            "polarity": story_con.polarity,
                            "strength": story_con.strength
                        },
                        "backstory_constraint": {
                            "polarity": back_con.polarity,
                            "strength": back_con.strength
                        },
                        "explanation": f"Story shows {story_con.polarity} {dim} "
                                       f"while backstory shows {back_con.polarity}."
                    })
        
        # Decision rules
        high_count = sum(1 for c in conflicts if c["severity"] == "high")
        medium_count = sum(1 for c in conflicts if c["severity"] == "medium")
        
        if len(conflicts) > 0:
            prediction = 0
            decision_explanation = {
                "decision": "inconsistent",
                "reason": "One or more constraint conflicts exceeded severity thresholds.",
                "trigger_summary": f"{len(conflicts)} conflicts detected."
            }
        else:
            prediction = 1
            decision_explanation = {
                "decision": "consistent",
                "reason": "No conflicting constraints were found between story and backstory.",
                "checked_dimensions": checked_dimensions,
                "rule_applied": "No polarity mismatches or severity thresholds triggered."
            }
        
        # Guarantee conflict recording
        if prediction == 0 and not conflicts:
            conflicts.append({
                "dimension": "general",
                "story_polarity": "mixed",
                "backstory_polarity": "mixed",
                "severity": "low",
                "explanation": "Backstory constraints are incompatible with accumulated story constraints, even though exact polarity matches were sparse."
            })
        
        return {"prediction": prediction, "conflicts": conflicts, "decision_explanation": decision_explanation}