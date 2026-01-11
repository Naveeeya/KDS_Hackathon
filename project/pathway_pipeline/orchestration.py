"""
Orchestrates the entire pipeline using Pathway.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pathway as pw
from pathway_pipeline.ingestion import DataIngestion
from narrative.chunker import NarrativeChunker
from narrative.experience_detector import ExperienceDetector
from constraints.schema import CharacterState
from constraints.updater import ConstraintUpdater
from backstory.parser import BackstoryParser
from constraints.comparator import ConstraintComparator
from evidence.retriever import EvidenceRetriever
import pandas as pd


def main():
    novel_path = "data/novels/harry_potter_main.txt"
    backstory_path = "data/backstories/harry_potter_backstory.txt"

    ingestion = DataIngestion()
    novel_text = ingestion.ingest_novel(novel_path)
    backstory_text = ingestion.ingest_backstory(backstory_path)

    chunker = NarrativeChunker()
    chunks = chunker.chunk_novel(novel_text)

    detector = ExperienceDetector()
    experiences = detector.detect_experiences(chunks)

    updater = ConstraintUpdater()
    character_state = CharacterState({}, [])
    for exp in experiences:
        character_state = updater.update_state(exp, character_state)

    parser = BackstoryParser()
    backstory_state = parser.parse_backstory(backstory_text)

    comparator = ConstraintComparator()
    result = comparator.compare(character_state, backstory_state)

    # TODO: Evidence retrieval if needed

    # Serialize full decision explanation into CSV
    decision_exp = result["decision_explanation"]
    conflicts = result["conflicts"]
    
    prediction = result["prediction"]
    decision = decision_exp["decision"]
    reason = decision_exp["reason"]
    trigger_summary = decision_exp.get("trigger_summary", "") if prediction == 0 else ""
    checked_dimensions = ";".join(decision_exp.get("checked_dimensions", [])) if prediction == 1 else ""
    conflict_dimensions = ";".join([c["dimension"] for c in conflicts])
    conflict_details = " || ".join([
        f"Story {c['dimension']}: {c['story_constraint']['polarity']} ({c['story_constraint']['strength']}) | "
        f"Backstory {c['dimension']}: {c['backstory_constraint']['polarity']} ({c['backstory_constraint']['strength']})"
        for c in conflicts
    ])
    
    results = [{
        "prediction": prediction,
        "decision": decision,
        "reason": reason,
        "trigger_summary": trigger_summary,
        "checked_dimensions": checked_dimensions,
        "conflict_dimensions": conflict_dimensions,
        "conflict_details": conflict_details
    }]
    df = pd.DataFrame(results)
    df.to_csv('results/results.csv', index=False)


if __name__ == "__main__":
    main()