"""
LLM-based consistency analyzer using OpenAI GPT-4.
Provides contextual understanding of backstory-narrative consistency.
"""

import os
from typing import List, Dict, Tuple
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class LLMConsistencyAnalyzer:
    """
    Uses GPT-4 to analyze consistency between backstory claims and novel evidence.
    """
    
    def __init__(self, api_key: str = None, model: str = None):
        """Initialize with OpenAI API key from environment or parameter."""
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY in .env file or environment.\n"
                "See .env.example for setup instructions."
            )
        self.client = OpenAI(api_key=self.api_key)
        # Use model from env or default to gpt-4o-mini (free tier)
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    
    def analyze_consistency(
        self, 
        backstory: str, 
        evidence_passages: List[str],
        character_name: str = ""
    ) -> Dict:
        """
        Analyze if backstory is consistent with evidence from the novel.
        
        Returns:
        {
            'prediction': 0 or 1,  # 0=contradict, 1=consistent
            'confidence': float,   # 0-1 confidence score
            'rationale': str,      # Explanation
            'conflicts': List[str] # Specific conflict dimensions
        }
        """
        # Construct prompt
        evidence_text = "\n\n---\n\n".join(evidence_passages[:20])  # Limit for token budget
        
        prompt = f"""You are analyzing narrative consistency for a character in a novel.

BACKSTORY CLAIM:
{backstory}

CHARACTER: {character_name if character_name else "Unknown"}

EVIDENCE FROM NOVEL (excerpts):
{evidence_text}

TASK:
Determine if the backstory claim is CONSISTENT or CONTRADICTORY with the character's behavior/traits shown in the novel excerpts.

Consider:
1. Direct contradictions (backstory says X, novel shows opposite)
2. Behavioral patterns that conflict with claimed history
3. Character traits inconsistent with backstory
4. Context and nuance (not just keywords)

RESPOND IN JSON FORMAT:
{{
    "prediction": 0 or 1,  // 0 = CONTRADICT, 1 = CONSISTENT
    "confidence": 0.0-1.0,  // How confident are you?
    "rationale": "Brief explanation (2-3 sentences)",
    "conflict_dimensions": ["dimension1", "dimension2"]  // Which aspects conflict? (violence, trust, authority, courage, loyalty, morality) or empty list if consistent
}}

Be strict: if there's clear contradiction, mark as 0. If uncertain or aligned, mark as 1."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert literary analyst specializing in character consistency."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Lower for more consistent results
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            
            return {
                'prediction': int(result.get('prediction', 1)),
                'confidence': float(result.get('confidence', 0.5)),
                'rationale': result.get('rationale', 'LLM analysis completed'),
                'conflicts': result.get('conflict_dimensions', [])
            }
            
        except Exception as e:
            # Fallback on error
            return {
                'prediction': 1,
                'confidence': 0.3,
                'rationale': f"LLM error: {str(e)}",
                'conflicts': []
            }
    
    def batch_analyze(
        self,
        backstory: str,
        evidence_chunks: List[str],
        character_name: str = "",
        chunk_size: int = 10
    ) -> Dict:
        """
        Analyze multiple evidence chunks in batches for cost efficiency.
        Returns aggregated result.
        """
        # For hackathon, analyze representative samples
        sample_chunks = evidence_chunks[:chunk_size]
        
        result = self.analyze_consistency(backstory, sample_chunks, character_name)
        return result


class HybridAnalyzer:
    """
    Hybrid approach: Use constraint-based analysis + LLM verification.
    """
    
    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm
        if use_llm:
            try:
                self.llm = LLMConsistencyAnalyzer()
            except ValueError:
                print("Warning: OpenAI API key not found. Falling back to constraint-only analysis.")
                self.use_llm = False
    
    def analyze(
        self,
        constraint_result: Dict,
        backstory: str,
        evidence_passages: List[str],
        character_name: str = ""
    ) -> Dict:
        """
        Combine constraint-based and LLM analysis.
        
        Strategy:
        1. If constraint analysis shows clear conflict → verify with LLM
        2. If constraint shows consistent → quick LLM check
        3. Return final prediction with explanation
        """
        # Get constraint-based prediction
        constraint_conflicts = constraint_result.get('conflicts', [])
        constraint_prediction = 0 if len(constraint_conflicts) > 0 else 1
        
        # If LLM available, use it for final decision
        if self.use_llm and evidence_passages:
            llm_result = self.llm.analyze_consistency(
                backstory, 
                evidence_passages,
                character_name
            )
            
            # Combine insights
            # Trust LLM more for nuanced cases
            final_prediction = llm_result['prediction']
            
            # Build comprehensive rationale
            if final_prediction == 0:
                conflict_dims = llm_result.get('conflicts', [])
                if conflict_dims:
                    rationale = f"LLM detected contradictions in [{', '.join(conflict_dims)}]. {llm_result['rationale']}"
                else:
                    rationale = f"Contradiction detected. {llm_result['rationale']}"
            else:
                rationale = f"Consistent. {llm_result['rationale']}"
            
            return {
                'prediction': final_prediction,
                'rationale': rationale,
                'llm_confidence': llm_result.get('confidence', 0.5),
                'method': 'hybrid_llm'
            }
        else:
            # Fallback to constraint-only
            if constraint_prediction == 0:
                dims = [c['dimension'] for c in constraint_conflicts[:3]]
                rationale = f"Constraint conflict in [{', '.join(dims)}]."
            else:
                rationale = "No constraint conflicts detected."
            
            return {
                'prediction': constraint_prediction,
                'rationale': rationale,
                'llm_confidence': None,
                'method': 'constraint_only'
            }
