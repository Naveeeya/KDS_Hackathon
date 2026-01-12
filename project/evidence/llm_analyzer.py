"""
Multi-provider LLM analyzer with Google Gemini (via google-genai) and OpenAI support.
"""

import os
import time
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


class LLMConsistencyAnalyzer:
    """Multi-provider LLM analyzer (Gemini + OpenAI)."""
    
    def __init__(self):
        # Try Gemini first (better free tier), then OpenAI
        self.provider = None
        self.client = None
        
        # Try Google Gemini (New google-genai package)
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            try:
                from google import genai
                from google.genai import types
                self.client = genai.Client(api_key=gemini_key)
                self.provider = "gemini"
                # Use gemini-2.0-flash as primary
                self.model_name = "gemini-2.0-flash"
                print(f"Using Google Gemini {self.model_name} (via google-genai)")
            except Exception as e:
                print(f"Failed to initialize Gemini: {e}")
                pass
        
        # Fallback to OpenAI
        if not self.provider:
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                try:
                    from openai import OpenAI
                    self.client = OpenAI(api_key=openai_key)
                    self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
                    self.provider = "openai"
                    print("Using OpenAI GPT-4")
                except:
                    pass
        
        if not self.provider:
            print("Warning: No LLM provider available. Falling back to constraint-only analysis.")
    
    def analyze_consistency(
        self, 
        backstory: str, 
        evidence_passages: List[str],
        character_name: str = ""
    ) -> Dict:
        """Analyze consistency using available LLM provider."""
        
        if not self.provider:
             return {
                'prediction': 1,
                'confidence': 0.0,
                'rationale': "LLM provider unavailable",
                'conflicts': []
            }

        evidence_text = "\n\n".join(evidence_passages[:5])
        
        prompt = f"""Analyze if this backstory is CONSISTENT or CONTRADICTORY with the novel evidence.

BACKSTORY:
{backstory[:500]}

NOVEL EVIDENCE:
{evidence_text[:2000]}

Is the backstory consistent with the evidence? Reply in JSON:
{{
  "prediction": 0 or 1,
  "reason": "one sentence explanation"
}}

0 = CONTRADICT (clear mismatch)
1 = CONSISTENT (aligns or no contradiction)"""

        # Try with retries
        for attempt in range(3):
            try:
                if self.provider == "gemini":
                    from google.genai import types
                    response = self.client.models.generate_content(
                        model=self.model_name,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            temperature=0.1,
                            max_output_tokens=150,
                            response_mime_type="application/json"
                        )
                    )
                    result_text = response.text
                    
                elif self.provider == "openai":
                    response = self.client.chat.completions.create(
                        model=self.model,
                        messages=[
                            {"role": "system", "content": "Analyze character consistency."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.1,
                        max_tokens=150,
                        response_format={"type": "json_object"}
                    )
                    result_text = response.choices[0].message.content
                
                # Parse result
                import json
                result = json.loads(result_text)
                
                return {
                    'prediction': int(result.get('prediction', 1)),
                    'confidence': 0.8,
                    'rationale': result.get('reason', 'LLM analysis'),
                    'conflicts': []
                }
                
            except Exception as e:
                if "429" in str(e) or "ResourceExhausted" in str(e):
                    print("Gemini quota exceeded.")
                    break  # Stop retrying if quota exceeded
                if attempt < 2:
                    time.sleep(1 * (attempt + 1))
                    continue
                print(f"LLM Error: {e}")
        
        # Final fallback - Return specific error status to let hybrid analyzer fallback to constraints
        return None


class HybridAnalyzer:
    """Fast hybrid: constraint + multi-provider LLM."""
    
    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm
        if use_llm:
            try:
                self.llm = LLMConsistencyAnalyzer()
            except Exception as e:
                print(f"LLM initialization failed: {e}")
                self.use_llm = False
                self.llm = None
    
    def analyze(
        self,
        constraint_result: Dict,
        backstory: str,
        evidence_passages: List[str],
        character_name: str = ""
    ) -> Dict:
        """Quick hybrid analysis."""
        
        # Prepare constraint-based fallback result first
        conflicts = constraint_result.get('conflicts', [])
        constraint_pred = 0 if len(conflicts) > 0 else 1
        if constraint_pred == 0:
            dims = [c['dimension'] for c in conflicts[:2]]
            constraint_rationale = f"Constraint conflict in [{', '.join(dims)}]"
        else:
            constraint_rationale = "No meaningful conflicts. All constraint polarities align."
            
        constraint_fallback = {
            'prediction': constraint_pred,
            'rationale': constraint_rationale
        }

        # If no LLM, return constraint result
        if not self.use_llm or not self.llm or not evidence_passages:
            return constraint_fallback
        
        # Try LLM
        llm_result = self.llm.analyze_consistency(backstory, evidence_passages, character_name)
        
        # If LLM failed (returned None), use fallback
        if llm_result is None or llm_result.get('rationale') == "LLM provider unavailable":
            return constraint_fallback
            
        return {
            'prediction': llm_result['prediction'],
            'rationale': llm_result['rationale']
        }
