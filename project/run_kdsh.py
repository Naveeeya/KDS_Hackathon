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
from evidence.llm_analyzer import HybridAnalyzer
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


def analyze_single(novel_text: str, backstory_text: str, character_name: str = None) -> dict:
    """
    Run the full pipeline on a single novel + backstory pair.
    Uses Pathway vector store for semantic retrieval + LLM for final analysis.
    """
    # Use Pathway processor for semantic retrieval
    pathway_processor = PathwayDocumentProcessor()
    num_chunks = pathway_processor.ingest_novel(novel_text)
    
    # Retrieve relevant passages based on backstory content
    relevant_passages = pathway_processor.retrieve_relevant_passages(backstory_text, top_k=30)
    
    # If character name provided, also retrieve character-specific passages
    if character_name:
        char_passages = pathway_processor.retrieve_by_character(character_name, top_k=50)
        # Combine and deduplicate
        all_passages = list(set(relevant_passages + char_passages))
    else:
        all_passages = relevant_passages
    
    # Use retrieved passages for analysis (or fall back to chunks if empty)
    if all_passages:
        analysis_text = '\n'.join(all_passages)
    else:
        analysis_text = novel_text[:100000]  # Fallback
    
    # Chunk for experience detection
    chunker = NarrativeChunker()
    chunks = chunker.chunk_novel(analysis_text)
    
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
    constraint_result = comparator.compare(character_state, backstory_state)
    
    # Use hybrid analyzer (constraint + LLM)
    hybrid = HybridAnalyzer(use_llm=True)
    final_result = hybrid.analyze(
        constraint_result=constraint_result,
        backstory=backstory_text,
        evidence_passages=all_passages[:15],  # Send top 15 passages to LLM
        character_name=character_name or ""
    )
    
    return {
        "prediction": final_result['prediction'],
        "rationale": final_result['rationale']
    }


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
