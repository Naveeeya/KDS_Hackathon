"""
Optimized LLM-based consistency analyzer.
"""

import os
import time
from typing import List, Dict
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class LLMConsistencyAnalyzer:
    """Optimized GPT-4 analyzer for narrative consistency."""
    
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key required. See .env.example")
        self.client = OpenAI(api_key=self.api_key)
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.retry_delays = [0.5, 1, 2, 5]  # Exponential backoff
    
    def analyze_consistency(
        self, 
        backstory: str, 
        evidence_passages: List[str],
        character_name: str = ""
    ) -> Dict:
        """Analyze consistency with optimized prompt and retry logic."""
        
        # Limit evidence to top 5 passages for speed
        evidence_text = "\n\n".join(evidence_passages[:5])
        
        # Simplified, more direct prompt
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

0 = CONTRADICT (clear mismatch between backstory and evidence)
1 = CONSISTENT (backstory aligns with or doesn't contradict evidence)"""

        # Retry logic with exponential backoff
        for attempt, delay in enumerate(self.retry_delays):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You analyze character consistency in narratives."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=150,
                    response_format={"type": "json_object"}
                )
                
                import json
                result = json.loads(response.choices[0].message.content)
                
                return {
                    'prediction': int(result.get('prediction', 1)),
                    'confidence': 0.8,
                    'rationale': result.get('reason', 'LLM analysis'),
                    'conflicts': []
                }
                
            except Exception as e:
                if "rate_limit" in str(e).lower() or "429" in str(e):
                    if attempt < len(self.retry_delays) - 1:
                        time.sleep(delay)
                        continue
                # Fallback on final error
                return {
                    'prediction': 1,
                    'confidence': 0.2,
                    'rationale': "LLM unavailable",
                    'conflicts': []
                }


class HybridAnalyzer:
    """Fast hybrid: constraint + LLM verification."""
    
    def __init__(self, use_llm: bool = True):
        self.use_llm = use_llm
        if use_llm:
            try:
                self.llm = LLMConsistencyAnalyzer()
            except:
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
