"""
Generates a detailed dossier output meeting hackathon requirements.
Includes: excerpts, backstory claims, linkage, and analysis.
"""

from typing import List, Dict, Any
from dataclasses import dataclass, field
from constraints.schema import CharacterState, Experience, Constraint
import json
import os
from datetime import datetime


@dataclass
class EvidenceLink:
    """Links a novel excerpt to a backstory claim with analysis."""
    excerpt_id: str
    excerpt_text: str
    chapter_id: int
    backstory_claim: str
    claim_id: str
    dimension: str
    relationship: str  # 'supports', 'contradicts', 'provides_context'
    analysis: str
    excerpt_polarity: str
    claim_polarity: str
    confidence: float


@dataclass
class DossierEntry:
    """A single entry in the dossier showing excerpt-claim linkage."""
    dimension: str
    story_polarity: str
    backstory_polarity: str
    is_conflict: bool
    severity: str
    evidence_links: List[EvidenceLink] = field(default_factory=list)
    summary: str = ""


class DossierGenerator:
    """Generates detailed dossier output with evidence linkage."""
    
    def __init__(self):
        self.dimension_descriptions = {
            "violence": "Attitudes and behaviors related to violence, conflict, and physical confrontation",
            "authority": "Relationship with authority figures, rules, and leadership",
            "trust": "Patterns of trust, loyalty, betrayal, and interpersonal bonds"
        }
    
    def extract_backstory_claims(self, backstory_text: str) -> List[Dict[str, Any]]:
        """
        Extracts individual claims from backstory text.
        Each claim is a sentence that makes an assertion about the character.
        """
        import re
        import hashlib
        
        claims = []
        sentences = re.split(r'(?<=[.!?])\s+', backstory_text.strip())
        
        dimension_keywords = {
            "violence": ["violence", "fight", "attack", "conflict", "battle", "harm", "hurt", "defend"],
            "authority": ["authority", "leader", "rule", "obey", "defy", "command", "order", "follow"],
            "trust": ["trust", "betray", "rely", "bond", "distrust", "loyal", "friend", "faith"]
        }
        
        negatives = ['never', 'not', 'no', 'without', 'avoided', 'refused', 'questioned', 
                     'distrusted', 'defied', 'rebelled', 'kept to himself', "didn't", "wouldn't"]
        positives = ['enjoyed', 'liked', 'obeyed', 'trusted', 'relied', 'followed', 
                     'respected', 'fought willingly', 'attacked', 'always', 'often']
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue
                
            lower_sent = sentence.lower()
            
            for dim, keywords in dimension_keywords.items():
                if any(kw in lower_sent for kw in keywords):
                    # Determine polarity
                    if any(neg in lower_sent for neg in negatives):
                        polarity = 'negative'
                    elif any(pos in lower_sent for pos in positives):
                        polarity = 'positive'
                    else:
                        polarity = 'positive'
                    
                    claim_id = hashlib.md5(sentence.encode()).hexdigest()[:8]
                    
                    claims.append({
                        "claim_id": claim_id,
                        "text": sentence,
                        "dimension": dim,
                        "polarity": polarity
                    })
                    break
        
        return claims
    
    def link_evidence_to_claims(
        self,
        experiences: List[Experience],
        backstory_claims: List[Dict[str, Any]],
        story_state: CharacterState,
        backstory_state: CharacterState
    ) -> List[EvidenceLink]:
        """
        Creates explicit linkages between excerpts and backstory claims.
        """
        import hashlib
        
        links = []
        
        dimension_keywords = {
            "violence": ["violence", "fight", "attack", "conflict", "battle", "harm", "defend"],
            "authority": ["authority", "leader", "rule", "obey", "defy", "command"],
            "trust": ["trust", "betray", "rely", "bond", "distrust", "loyal", "friend"]
        }
        
        negatives = ['never', 'not', 'no', 'without', 'avoided', 'refused', 'questioned',
                     'distrusted', 'defied', 'rebelled', 'walked away', 'chose peace']
        positives = ['enjoyed', 'liked', 'obeyed', 'trusted', 'relied', 'followed',
                     'respected', 'fought willingly', 'attacked']
        
        for exp in experiences:
            exp_lower = exp.raw_text_reference.lower()
            
            # Determine experience dimension and polarity
            exp_dim = None
            exp_polarity = 'positive'
            
            for dim, keywords in dimension_keywords.items():
                if any(kw in exp_lower for kw in keywords):
                    exp_dim = dim
                    if any(neg in exp_lower for neg in negatives):
                        exp_polarity = 'negative'
                    elif any(pos in exp_lower for pos in positives):
                        exp_polarity = 'positive'
                    break
            
            if not exp_dim:
                continue
            
            # Find matching backstory claims in same dimension
            for claim in backstory_claims:
                if claim["dimension"] == exp_dim:
                    # Determine relationship
                    if exp_polarity == claim["polarity"]:
                        relationship = "supports"
                        analysis = self._generate_support_analysis(
                            exp.raw_text_reference, claim["text"], exp_dim, exp_polarity
                        )
                    else:
                        relationship = "contradicts"
                        analysis = self._generate_contradiction_analysis(
                            exp.raw_text_reference, claim["text"], exp_dim, 
                            exp_polarity, claim["polarity"]
                        )
                    
                    # Calculate confidence based on keyword strength
                    confidence = self._calculate_confidence(exp.raw_text_reference, claim["text"])
                    
                    link = EvidenceLink(
                        excerpt_id=exp.id,
                        excerpt_text=exp.raw_text_reference[:500],  # Truncate if too long
                        chapter_id=exp.chapter_id,
                        backstory_claim=claim["text"],
                        claim_id=claim["claim_id"],
                        dimension=exp_dim,
                        relationship=relationship,
                        analysis=analysis,
                        excerpt_polarity=exp_polarity,
                        claim_polarity=claim["polarity"],
                        confidence=confidence
                    )
                    links.append(link)
        
        return links
    
    def _generate_support_analysis(self, excerpt: str, claim: str, dimension: str, polarity: str) -> str:
        """Generates analysis text for supporting evidence."""
        return (f"This excerpt demonstrates {polarity} {dimension} behavior that aligns with "
                f"the backstory claim. The narrative evidence shows consistency in the character's "
                f"established patterns regarding {dimension}.")
    
    def _generate_contradiction_analysis(
        self, excerpt: str, claim: str, dimension: str, 
        excerpt_polarity: str, claim_polarity: str
    ) -> str:
        """Generates analysis text for contradicting evidence."""
        return (f"CONFLICT DETECTED: The excerpt shows {excerpt_polarity} {dimension} behavior, "
                f"but the backstory indicates {claim_polarity} {dimension}. This represents a "
                f"fundamental inconsistency between the character's stated history and their "
                f"behavior in the narrative.")
    
    def _calculate_confidence(self, excerpt: str, claim: str) -> float:
        """Calculates confidence score based on keyword overlap and clarity."""
        # Simple keyword overlap scoring
        excerpt_words = set(excerpt.lower().split())
        claim_words = set(claim.lower().split())
        
        overlap = len(excerpt_words & claim_words)
        max_len = max(len(excerpt_words), len(claim_words))
        
        if max_len == 0:
            return 0.5
        
        base_score = 0.5 + (overlap / max_len) * 0.5
        return round(min(1.0, base_score), 2)
    
    def generate_dossier(
        self,
        experiences: List[Experience],
        backstory_text: str,
        story_state: CharacterState,
        backstory_state: CharacterState,
        comparison_result: Dict
    ) -> Dict[str, Any]:
        """
        Generates the complete dossier with all required elements.
        """
        # Extract backstory claims
        backstory_claims = self.extract_backstory_claims(backstory_text)
        
        # Create evidence links
        evidence_links = self.link_evidence_to_claims(
            experiences, backstory_claims, story_state, backstory_state
        )
        
        # Group by dimension
        dimension_analysis = {}
        for dim in ["violence", "authority", "trust"]:
            dim_links = [l for l in evidence_links if l.dimension == dim]
            
            if dim_links:
                supporting = [l for l in dim_links if l.relationship == "supports"]
                contradicting = [l for l in dim_links if l.relationship == "contradicts"]
                
                story_pol = story_state.constraints.get(dim)
                back_pol = backstory_state.constraints.get(dim)
                
                dimension_analysis[dim] = {
                    "description": self.dimension_descriptions.get(dim, ""),
                    "story_polarity": story_pol.polarity if story_pol else "unknown",
                    "backstory_polarity": back_pol.polarity if back_pol else "unknown",
                    "total_excerpts": len(dim_links),
                    "supporting_count": len(supporting),
                    "contradicting_count": len(contradicting),
                    "is_conflict": len(contradicting) > 0,
                    "evidence_links": [
                        {
                            "excerpt_id": l.excerpt_id,
                            "excerpt_text": l.excerpt_text,
                            "chapter": l.chapter_id,
                            "backstory_claim": l.backstory_claim,
                            "relationship": l.relationship,
                            "analysis": l.analysis,
                            "confidence": l.confidence
                        }
                        for l in dim_links[:10]  # Limit to top 10 per dimension
                    ]
                }
        
        # Build final dossier
        dossier = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_excerpts_analyzed": len(experiences),
                "total_backstory_claims": len(backstory_claims),
                "total_evidence_links": len(evidence_links)
            },
            "prediction": {
                "value": comparison_result["prediction"],
                "decision": comparison_result["decision_explanation"]["decision"],
                "reason": comparison_result["decision_explanation"]["reason"]
            },
            "backstory_claims": backstory_claims,
            "dimension_analysis": dimension_analysis,
            "conflicts": comparison_result["conflicts"],
            "summary": self._generate_summary(
                comparison_result, dimension_analysis, len(evidence_links)
            )
        }
        
        return dossier
    
    def _generate_summary(
        self, 
        comparison_result: Dict, 
        dimension_analysis: Dict,
        total_links: int
    ) -> str:
        """Generates a human-readable summary of the analysis."""
        decision = comparison_result["decision_explanation"]["decision"]
        
        if decision == "consistent":
            summary = (
                f"CONSISTENT: The backstory claims are supported by the narrative evidence. "
                f"Analysis of {total_links} excerpt-claim linkages across "
                f"{len(dimension_analysis)} behavioral dimensions shows alignment between "
                f"the character's stated history and their actions in the story."
            )
        else:
            conflict_dims = [dim for dim, data in dimension_analysis.items() 
                           if data.get("is_conflict", False)]
            summary = (
                f"INCONSISTENT: Conflicts detected in {len(conflict_dims)} dimension(s): "
                f"{', '.join(conflict_dims)}. The backstory claims contradict behavioral "
                f"evidence found in the narrative. See detailed analysis below for "
                f"specific excerpts and explanations."
            )
        
        return summary
    
    def save_dossier(self, dossier: Dict, output_dir: str = "results"):
        """Saves the dossier in multiple formats."""
        os.makedirs(output_dir, exist_ok=True)
        
        # Save JSON (detailed)
        json_path = os.path.join(output_dir, "dossier.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(dossier, f, indent=2, ensure_ascii=False)
        
        # Save Markdown (human-readable)
        md_path = os.path.join(output_dir, "dossier.md")
        markdown = self._generate_markdown(dossier)
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        return json_path, md_path
    
    def _generate_markdown(self, dossier: Dict) -> str:
        """Generates a markdown version of the dossier."""
        lines = []
        
        # Header
        lines.append("# Narrative Consistency Dossier")
        lines.append("")
        lines.append(f"**Generated:** {dossier['metadata']['generated_at']}")
        lines.append("")
        
        # Decision Banner
        pred = dossier["prediction"]
        if pred["value"] == 1:
            lines.append("> [!NOTE]")
            lines.append(f"> **Decision: {pred['decision'].upper()}**")
        else:
            lines.append("> [!WARNING]")
            lines.append(f"> **Decision: {pred['decision'].upper()}**")
        lines.append(f"> {pred['reason']}")
        lines.append("")
        
        # Summary
        lines.append("## Executive Summary")
        lines.append("")
        lines.append(dossier["summary"])
        lines.append("")
        
        # Statistics
        lines.append("## Analysis Statistics")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|--------|-------|")
        lines.append(f"| Total Excerpts Analyzed | {dossier['metadata']['total_excerpts_analyzed']} |")
        lines.append(f"| Total Backstory Claims | {dossier['metadata']['total_backstory_claims']} |")
        lines.append(f"| Total Evidence Links | {dossier['metadata']['total_evidence_links']} |")
        lines.append("")
        
        # Backstory Claims
        lines.append("## Backstory Claims Analyzed")
        lines.append("")
        for i, claim in enumerate(dossier["backstory_claims"], 1):
            lines.append(f"### Claim {i} ({claim['dimension'].title()})")
            lines.append(f"**ID:** `{claim['claim_id']}`")
            lines.append(f"**Polarity:** {claim['polarity']}")
            lines.append("")
            lines.append(f"> {claim['text']}")
            lines.append("")
        
        # Dimension Analysis
        lines.append("## Dimension-by-Dimension Analysis")
        lines.append("")
        
        for dim, data in dossier["dimension_analysis"].items():
            lines.append(f"### {dim.title()}")
            lines.append("")
            lines.append(f"*{data['description']}*")
            lines.append("")
            
            # Polarity comparison
            if data["is_conflict"]:
                lines.append("> [!CAUTION]")
                lines.append(f"> **CONFLICT**: Story shows `{data['story_polarity']}` vs Backstory shows `{data['backstory_polarity']}`")
            else:
                lines.append("> [!TIP]")
                lines.append(f"> **ALIGNED**: Both story and backstory show `{data['story_polarity']}` polarity")
            lines.append("")
            
            lines.append(f"| Metric | Count |")
            lines.append(f"|--------|-------|")
            lines.append(f"| Total Excerpts | {data['total_excerpts']} |")
            lines.append(f"| Supporting | {data['supporting_count']} |")
            lines.append(f"| Contradicting | {data['contradicting_count']} |")
            lines.append("")
            
            # Evidence Links
            if data["evidence_links"]:
                lines.append("#### Evidence Links")
                lines.append("")
                
                for j, link in enumerate(data["evidence_links"][:5], 1):  # Show top 5
                    rel_icon = "✓" if link["relationship"] == "supports" else "✗"
                    lines.append(f"**{j}. [{rel_icon}] {link['relationship'].upper()}** (Chapter {link['chapter']}, Confidence: {link['confidence']})")
                    lines.append("")
                    lines.append("**Excerpt:**")
                    # Truncate long excerpts for readability
                    excerpt_display = link["excerpt_text"][:300] + "..." if len(link["excerpt_text"]) > 300 else link["excerpt_text"]
                    lines.append(f"> {excerpt_display}")
                    lines.append("")
                    lines.append("**Linked Backstory Claim:**")
                    lines.append(f"> {link['backstory_claim']}")
                    lines.append("")
                    lines.append("**Analysis:**")
                    lines.append(f"{link['analysis']}")
                    lines.append("")
                    lines.append("---")
                    lines.append("")
        
        # Conflicts Section
        if dossier["conflicts"]:
            lines.append("## Detected Conflicts")
            lines.append("")
            for i, conflict in enumerate(dossier["conflicts"], 1):
                lines.append(f"### Conflict {i}: {conflict.get('dimension', 'Unknown').title()}")
                lines.append("")
                lines.append(f"**Severity:** {conflict.get('severity', 'unknown')}")
                lines.append(f"**Trigger Rule:** {conflict.get('trigger_rule', 'N/A')}")
                lines.append("")
                if "explanation" in conflict:
                    lines.append(f"{conflict['explanation']}")
                lines.append("")
        
        return "\n".join(lines)
