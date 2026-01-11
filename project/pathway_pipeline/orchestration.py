"""
Orchestrates the entire pipeline using Pathway.
Generates detailed dossier output with evidence linkage.
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
from evidence.dossier_generator import DossierGenerator
import pandas as pd


def main():
    print("=" * 60)
    print("NARRATIVE CONSISTENCY ANALYSIS PIPELINE")
    print("=" * 60)
    
    novel_path = "data/novels/harry_potter_main.txt"
    backstory_path = "data/backstories/harry_potter_backstory.txt"

    # Step 1: Data Ingestion
    print("\n[1/7] Ingesting data...")
    ingestion = DataIngestion()
    novel_text = ingestion.ingest_novel(novel_path)
    backstory_text = ingestion.ingest_backstory(backstory_path)
    print(f"    - Novel: {len(novel_text)} characters")
    print(f"    - Backstory: {len(backstory_text)} characters")

    # Step 2: Chunking
    print("\n[2/7] Chunking narrative...")
    chunker = NarrativeChunker()
    chunks = chunker.chunk_novel(novel_text)
    print(f"    - Generated {len(chunks)} chunks")

    # Step 3: Experience Detection
    print("\n[3/7] Detecting experiences...")
    detector = ExperienceDetector()
    experiences = detector.detect_experiences(chunks)
    print(f"    - Detected {len(experiences)} relevant experiences")

    # Step 4: Constraint Evolution
    print("\n[4/7] Evolving character constraints...")
    updater = ConstraintUpdater()
    character_state = CharacterState({}, [])
    for exp in experiences:
        character_state = updater.update_state(exp, character_state)
    print(f"    - Evolved {len(character_state.constraints)} constraint dimensions")
    for dim, con in character_state.constraints.items():
        print(f"      • {dim}: {con.polarity} (strength: {con.strength:.2f})")

    # Step 5: Backstory Parsing
    print("\n[5/7] Parsing backstory claims...")
    parser = BackstoryParser()
    backstory_state = parser.parse_backstory(backstory_text)
    print(f"    - Parsed {len(backstory_state.constraints)} constraint dimensions")
    for dim, con in backstory_state.constraints.items():
        print(f"      • {dim}: {con.polarity} (strength: {con.strength:.2f})")

    # Step 6: Constraint Comparison
    print("\n[6/7] Comparing constraints...")
    comparator = ConstraintComparator()
    result = comparator.compare(character_state, backstory_state)
    print(f"    - Prediction: {result['prediction']} ({result['decision_explanation']['decision']})")
    print(f"    - Conflicts: {len(result['conflicts'])}")

    # Step 7: Generate Detailed Dossier
    print("\n[7/7] Generating detailed dossier...")
    dossier_gen = DossierGenerator()
    dossier = dossier_gen.generate_dossier(
        experiences=experiences,
        backstory_text=backstory_text,
        story_state=character_state,
        backstory_state=backstory_state,
        comparison_result=result
    )
    json_path, md_path = dossier_gen.save_dossier(dossier, "results")
    print(f"    - Saved JSON: {json_path}")
    print(f"    - Saved Markdown: {md_path}")

    # Also save summary CSV for quick reference
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
    
    csv_results = [{
        "prediction": prediction,
        "decision": decision,
        "reason": reason,
        "trigger_summary": trigger_summary,
        "checked_dimensions": checked_dimensions,
        "conflict_dimensions": conflict_dimensions,
        "conflict_details": conflict_details,
        "total_excerpts": dossier["metadata"]["total_excerpts_analyzed"],
        "total_claims": dossier["metadata"]["total_backstory_claims"],
        "total_evidence_links": dossier["metadata"]["total_evidence_links"]
    }]
    df = pd.DataFrame(csv_results)
    df.to_csv('results/results.csv', index=False)
    print(f"    - Saved CSV: results/results.csv")
    
    # Print Summary
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print(f"\n{dossier['summary']}")
    print(f"\nOutput files:")
    print(f"  • results/dossier.md   - Human-readable detailed report")
    print(f"  • results/dossier.json - Machine-readable full data")
    print(f"  • results/results.csv  - Quick summary")


if __name__ == "__main__":
    main()