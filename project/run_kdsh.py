"""
Batch processor for hackathon dataset.
Reads test.csv, runs pipeline on each entry, outputs predictions.
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


# Map book names to file paths
NOVEL_PATHS = {
    "The Count of Monte Cristo": "data/The Count of Monte Cristo.txt",
    "In Search of the Castaways": "data/In search of the castaways.txt"
}


def load_novel(book_name: str) -> str:
    """Load novel text based on book name."""
    path = NOVEL_PATHS.get(book_name)
    if not path or not os.path.exists(path):
        raise FileNotFoundError(f"Novel not found for: {book_name}")
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def analyze_single(novel_text: str, backstory_text: str) -> dict:
    """
    Run the full pipeline on a single novel + backstory pair.
    Returns prediction (0 or 1) and rationale.
    """
    # Chunk novel
    chunker = NarrativeChunker()
    chunks = chunker.chunk_novel(novel_text)
    
    # Detect experiences
    detector = ExperienceDetector()
    experiences = detector.detect_experiences(chunks)
    
    # Evolve character constraints from story
    updater = ConstraintUpdater()
    character_state = CharacterState({}, [])
    for exp in experiences:
        character_state = updater.update_state(exp, character_state)
    
    # Parse backstory
    parser = BackstoryParser()
    backstory_state = parser.parse_backstory(backstory_text)
    
    # Compare constraints
    comparator = ConstraintComparator()
    result = comparator.compare(character_state, backstory_state)
    
    # Generate dossier for evidence analysis
    dossier_gen = DossierGenerator()
    dossier = dossier_gen.generate_dossier(
        experiences=experiences,
        backstory_text=backstory_text,
        story_state=character_state,
        backstory_state=backstory_state,
        comparison_result=result
    )
    
    conflicts = result["conflicts"]
    
    # Filter for MEDIUM/HIGH severity conflicts only
    significant_conflicts = [c for c in conflicts if c.get("severity", "").lower() in ["medium", "high"]]
    
    # Determine conflict dimensions with evidence dominance
    conflict_dims_with_evidence = []
    for conflict in significant_conflicts:
        dim = conflict.get("dimension", "")
        dim_data = dossier["dimension_analysis"].get(dim, {})
        contradicting = dim_data.get("contradicting_count", 0)
        supporting = dim_data.get("supporting_count", 0)
        if contradicting >= supporting * 0.5:
            conflict_dims_with_evidence.append(dim)
    
    # Final decision
    if conflict_dims_with_evidence:
        prediction = 0
        conflict_list = ", ".join(conflict_dims_with_evidence)
        rationale = f"Polarity mismatch in [{conflict_list}]. HIGH severity with evidence dominance."
    else:
        prediction = 1
        if significant_conflicts:
            rationale = "Minor conflicts below evidence threshold. Constraints align."
        else:
            rationale = "No meaningful conflicts. All constraint polarities align."
    
    return {"prediction": prediction, "rationale": rationale}


def main():
    print("=" * 60)
    print("HACKATHON BATCH PROCESSOR")
    print("=" * 60)
    
    # Load test.csv
    test_path = "../test.csv"
    if not os.path.exists(test_path):
        print(f"ERROR: test.csv not found at {test_path}")
        return
    
    test_df = pd.read_csv(test_path)
    print(f"\nLoaded {len(test_df)} test samples")
    
    # Cache novels to avoid reloading
    novel_cache = {}
    
    results = []
    
    for idx, row in test_df.iterrows():
        story_id = row["id"]
        book_name = row["book_name"]
        backstory = row["content"]
        
        print(f"\n[{idx+1}/{len(test_df)}] Processing ID: {story_id} ({book_name})")
        
        try:
            # Load novel (cached)
            if book_name not in novel_cache:
                print(f"    Loading novel: {book_name}...")
                novel_cache[book_name] = load_novel(book_name)
            novel_text = novel_cache[book_name]
            
            # Run analysis
            result = analyze_single(novel_text, backstory)
            
            results.append({
                "story_id": story_id,
                "prediction": result["prediction"],
                "rationale": result["rationale"]
            })
            
            print(f"    Prediction: {result['prediction']}")
            
        except Exception as e:
            print(f"    ERROR: {str(e)}")
            results.append({
                "story_id": story_id,
                "prediction": 1,  # Default to consistent on error
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
    print(f"Predictions - 0 (contradict): {sum(1 for r in results if r['prediction'] == 0)}")
    print(f"Predictions - 1 (consistent): {sum(1 for r in results if r['prediction'] == 1)}")


if __name__ == "__main__":
    main()
