"""
Unit tests for constraint logic.
"""

import pytest
from constraints.schema import Constraint, CharacterState
from constraints.comparator import ConstraintComparator


def test_comparator():
    comp = ConstraintComparator()
    story = CharacterState({"violence": Constraint("violence", "negative", 0.8, [])}, [])
    backstory = CharacterState({"violence": Constraint("violence", "positive", 0.9, [])}, [])
    result = comp.compare(story, backstory)
    assert result["prediction"] == 0  # Should contradict