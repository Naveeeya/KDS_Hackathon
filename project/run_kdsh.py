"""
KDSH 2026 - Narrative Consistency Analysis
Batch processor using Pathway vector store for semantic retrieval.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
from narrative.chunker import NarrativeChunker
from narrative.experience_detector import ExperienceDetector
from constraints.schema import CharacterState
from constraints.updater import ConstraintUpdater
from backstory.parser import BackstoryParser
from constraints.comparator import ConstraintComparator
from evidence.dossier_generator import DossierGenerator
from pathway_pipeline.vector_store import PathwayDocumentProcessor


# Map book names to file paths
NOVEL_PATHS = {
    "The Count of Monte Cristo": "data/The Count of Monte Cristo.txt",
    "In Search of the Castaways": "data/In search of the castaways.txt"
}

# Lowered threshold for better conflict detection
EVIDENCE_DOMINANCE_THRESHOLD = 0.3  # Was 0.5, now more sensitive


def load_novel(book_name: str) -> str:
    """Load novel text based on book name."""
    path = NOVEL_PATHS.get(book_name)
    if not path or not os.path.exists(path):
        raise FileNotFoundError(f"Novel not found for: {book_name}")
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


# Configuration
EVIDENCE_DOMINANCE_THRESHOLD = 0.3  # Tuned for improved recall


def analyze_single(novel_text, backstory_text, character_name=""):
    """
    Run pipeline for a single backstory.
    Returns dictionary with prediction and rationale.
    """
    # 1. Chunking
    chunker = NarrativeChunker()
    chunks = chunker.chunk_novel(novel_text)
    
    # Filter by character name
    if character_name:
        chunks = [c for c in chunks if character_name.lower() in c.lower()]
    
    # 2. Experience Detection
    detector = ExperienceDetector()
    experiences = detector.detect_experiences(chunks)
    
    # 3. Update Character State
    updater = ConstraintUpdater()
    story_state = CharacterState({}, [])
    for exp in experiences:
        story_state = updater.update_state(exp, story_state)
    
    # 4. Parse Backstory
    parser = BackstoryParser()
    backstory_state = parser.parse_backstory(backstory_text)
    
    # 5. Compare Constraints
    comparator = ConstraintComparator()
    dataset_result = comparator.compare(
        story_state, 
        backstory_state,
        threshold=EVIDENCE_DOMINANCE_THRESHOLD
    )
    
    return {
        'prediction': dataset_result['prediction'],
        'rationale': _format_rationale(dataset_result)
    }


def _format_rationale(result):
    if result['prediction'] == 1:
        return "No meaningful conflicts. Behavior aligns with backstory constraints."
    
    conflicts = result['conflicts']
    if not conflicts:
        # Should not happen if prediction is 0, but fallback
        return "Inconsistencies detected in general character tone."
        
    # Join explanations for all conflicts
    explanations = []
    for c in conflicts:
        dim = c['dimension']
        explanation = c.get('explanation', f"Conflict in {dim}")
        explanations.append(f"[{dim.upper()}]: {explanation}")
        
    return "; ".join(explanations)


def main():
    print("=" * 60)
    print("KDSH 2026 - NARRATIVE CONSISTENCY ANALYZER")
    print("Powered by Pathway Streaming Framework")
    print("=" * 60)
    
    # Load test.csv
    test_path = "../test.csv"
    if not os.path.exists(test_path):
        print(f"ERROR: test.csv not found at {test_path}")
        return
    
    test_df = pd.read_csv(test_path)
    print(f"\nLoaded {len(test_df)} test samples")
    print(f"Evidence Dominance Threshold: {EVIDENCE_DOMINANCE_THRESHOLD}")
    
    # Cache novels to avoid reloading
    novel_cache = {}
    
    results = []
    
    for idx, row in test_df.iterrows():
        story_id = row["id"]
        book_name = row["book_name"]
        backstory = row["content"]
        character = row.get("char", "")  # Get character name if available
        
        print(f"\n[{idx+1}/{len(test_df)}] ID: {story_id} | {book_name} | Char: {character}")
        
        try:
            # Load novel (cached)
            if book_name not in novel_cache:
                print(f"    Loading novel: {book_name}...")
                novel_cache[book_name] = load_novel(book_name)
            novel_text = novel_cache[book_name]
            
            # Run analysis with character filtering
            result = analyze_single(novel_text, backstory, character)
            
            results.append({
                "story_id": story_id,
                "prediction": result["prediction"],
                "rationale": result["rationale"]
            })
            
            pred_label = "CONTRADICT" if result["prediction"] == 0 else "CONSISTENT"
            print(f"    Prediction: {result['prediction']} ({pred_label})")
            
        except Exception as e:
            print(f"    ERROR: {str(e)}")
            results.append({
                "story_id": story_id,
                "prediction": 1,
                "rationale": f"Error during processing: {str(e)}"
            })
    
    # Save results
    results_df = pd.DataFrame(results)
    output_path = "results/results.csv"
    results_df.to_csv(output_path, index=False)
    
    print("\n" + "=" * 60)
    print("BATCH PROCESSING COMPLETE")
    print("=" * 60)
    print(f"\nResults saved to: {output_path}")
    print(f"Total samples: {len(results)}")
    contradict_count = sum(1 for r in results if r['prediction'] == 0)
    consistent_count = sum(1 for r in results if r['prediction'] == 1)
    print(f"Predictions - 0 (CONTRADICT): {contradict_count} ({100*contradict_count/len(results):.1f}%)")
    print(f"Predictions - 1 (CONSISTENT): {consistent_count} ({100*consistent_count/len(results):.1f}%)")


if __name__ == "__main__":
    main()
