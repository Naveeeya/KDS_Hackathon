"""
Multi-provider LLM analyzer with Google Gemini and OpenAI support.
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
        
        # Try Google Gemini
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_key)
                self.client = genai.GenerativeModel('gemini-1.5-flash')
                self.provider = "gemini"
                print("Using Google Gemini (free tier: 60 req/min)")
            except:
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
            raise ValueError("No LLM provider available. Set GEMINI_API_KEY or OPENAI_API_KEY in .env")
    
    def analyze_consistency(
        self, 
        backstory: str, 
        evidence_passages: List[str],
        character_name: str = ""
    ) -> Dict:
        """Analyze consistency using available LLM provider."""
        
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
                    response = self.client.generate_content(
                        prompt,
                        generation_config={
                            "temperature": 0.1,
                            "max_output_tokens": 150,
                        }
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
                if attempt < 2:
                    time.sleep(1 * (attempt + 1))  # 1s, 2s
                    continue
                # Final fallback
                return {
                    'prediction': 1,
                    'confidence': 0.2,
                    'rationale': "LLM unavailable",
                    'conflicts': []
                }


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
    
    def analyze(
        self,
        constraint_result: Dict,
        backstory: str,
        evidence_passages: List[str],
        character_name: str = ""
    ) -> Dict:
        """Quick hybrid analysis."""
        
        # If no LLM or no evidence, use constraints only
        if not self.use_llm or not evidence_passages:
            conflicts = constraint_result.get('conflicts', [])
            pred = 0 if len(conflicts) > 0 else 1
            if pred == 0:
                dims = [c['dimension'] for c in conflicts[:2]]
                rationale = f"Conflict in [{', '.join(dims)}]"
            else:
                rationale = "No conflicts detected"
            return {'prediction': pred, 'rationale': rationale}
        
        # Use LLM for final decision
        llm_result = self.llm.analyze_consistency(backstory, evidence_passages, character_name)
        return {
            'prediction': llm_result['prediction'],
            'rationale': llm_result['rationale']
        }
