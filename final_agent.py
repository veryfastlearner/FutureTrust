#!/usr/bin/env python3
"""
Final Frontier Agent - Ultimate Layer
Synthesizes results from all previous layers and presents final verdict with justification
"""

import os
import sys
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from groq import Groq
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEFAULT_MODEL = "llama-3.3-70b-versatile"
MODEL = os.getenv("MODEL", DEFAULT_MODEL).strip().strip("\"'")

if MODEL.isdigit() or MODEL.startswith("meta-llama"):
    MODEL = DEFAULT_MODEL

groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


FINAL_AGENT_PROMPT = """You are the Final Frontier Agent - the ultimate decision maker in a multi-layer content verification system.

Your job is to synthesize findings from all previous layers and deliver a FINAL, READABLE verdict with clear justification.

## LAYER INPUTS:
1. **Content Inspector** (First Layer): Detected obvious red flags, URLs, accounts
2. **URL Pipeline**: Results from URL safety checks (if URLs were found)
3. **Bot Detection**: Profile analysis results (if accounts were found)

## YOUR TASK:
Based on ALL layer inputs, produce a final verdict that:
1. States CLEARLY if the content is Trustworthy, Suspicious, or Untrustworthy
2. Provides CONCISE, readable explanation (2-3 sentences max)
3. Highlights the KEY evidence that led to this decision
4. Suggests what the user should do

## OUTPUT FORMAT:
Return ONLY a JSON object:
{
    "verdict": "trustworthy|suspicious|untrustworthy",
    "confidence": "high|medium|low",
    "summary": "2-3 sentence readable explanation",
    "key_evidence": ["point 1", "point 2"],
    "recommendation": "what the user should do",
    "risk_level": "none|low|medium|high|critical"
}

Rules:
- If ANY layer found critical issues → verdict must be "untrustworthy"
- If URL is flagged as phishing/malware → immediate "untrustworthy"
- If bot detection shows "bot" with high confidence → strong "untrustworthy" indicator
- If all layers pass but content has red flags → "suspicious"
- Be decisive but fair - default to "suspicious" if uncertain
"""


@dataclass
class LayerResults:
    """Container for all layer results"""
    inspector: Dict[str, Any]
    url_check: Optional[Dict[str, Any]] = None
    bot_check: Optional[Dict[str, Any]] = None
    content: str = ""


class FinalFrontierAgent:
    """Ultimate decision maker with readable justification"""
    
    def __init__(self):
        self.model = MODEL
        self.client = groq_client
    
    def synthesize(self, layers: LayerResults) -> Dict[str, Any]:
        """
        Synthesize all layer results into final verdict
        
        Args:
            layers: LayerResults containing all inspection results
            
        Returns:
            Dict with final verdict, confidence, summary, etc.
        """
        # Build context for the LLM
        context = self._build_context(layers)
        
        if not self.client:
            # Fallback to rule-based synthesis if no Groq
            return self._rule_based_synthesis(layers)
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": FINAL_AGENT_PROMPT},
                    {"role": "user", "content": context}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            return self._parse_response(content, layers)
            
        except Exception as e:
            print(f"[Final Agent Error] {e}")
            return self._rule_based_synthesis(layers)
    
    def _build_context(self, layers: LayerResults) -> str:
        """Build context string from all layers"""
        lines = [
            "## CONTENT TO ANALYZE:",
            f"{layers.content[:500]}",  # Truncate if too long
            "",
            "## LAYER 1: CONTENT INSPECTOR RESULTS:",
            json.dumps(layers.inspector, indent=2),
            "",
        ]
        
        if layers.url_check:
            lines.extend([
                "## LAYER 2: URL SAFETY CHECK:",
                json.dumps(layers.url_check, indent=2),
                "",
            ])
        
        if layers.bot_check:
            lines.extend([
                "## LAYER 3: BOT DETECTION:",
                json.dumps(layers.bot_check, indent=2),
                "",
            ])
        
        lines.append("## YOUR TASK:")
        lines.append("Synthesize all findings and provide the FINAL VERDICT.")
        
        return "\n".join(lines)
    
    def _rule_based_synthesis(self, layers: LayerResults) -> Dict[str, Any]:
        """Fallback rule-based synthesis when LLM unavailable"""
        inspector = layers.inspector
        url_check = layers.url_check
        bot_check = layers.bot_check
        
        # Start with default
        verdict = "trustworthy"
        confidence = "high"
        risk_level = "none"
        key_evidence = []
        
        # Check URL results
        if url_check:
            url_class = url_check.get("prediction_class", 0)
            if url_class in [2, 3]:  # Phishing or Malware
                verdict = "untrustworthy"
                confidence = "high"
                risk_level = "critical"
                key_evidence.append(f"URL flagged as {url_check.get('prediction_label', 'malicious')}")
            elif url_class == 1:  # Defacement
                verdict = "suspicious"
                confidence = "medium"
                risk_level = "medium"
                key_evidence.append("URL shows suspicious structure")
        
        # Check bot detection
        if bot_check:
            top_result = bot_check.get("top_result", {})
            if top_result.get("label") == "bot" and top_result.get("confidence", 0) > 0.7:
                verdict = "untrustworthy" if verdict != "untrustworthy" else "untrustworthy"
                confidence = "high"
                risk_level = "high" if risk_level != "critical" else "critical"
                key_evidence.append(f"Profile identified as bot ({top_result.get('confidence', 0)*100:.1f}% confidence)")
            elif top_result.get("label") in ["cyborg", "bot"]:
                verdict = "suspicious" if verdict == "trustworthy" else verdict
                key_evidence.append(f"Profile shows automated characteristics ({top_result.get('label')})")
        
        # Check inspector red flags
        red_flags = inspector.get("red_flags", [])
        if red_flags:
            if len(red_flags) >= 3:
                verdict = "untrustworthy" if verdict != "untrustworthy" else verdict
                confidence = "medium"
                risk_level = "high"
            elif len(red_flags) >= 1:
                verdict = "suspicious" if verdict == "trustworthy" else verdict
                confidence = "medium"
                risk_level = "medium" if risk_level == "none" else risk_level
            
            key_evidence.extend([f"Detected: {flag}" for flag in red_flags[:3]])
        
        # Build summary based on verdict
        if verdict == "trustworthy":
            summary = "All verification layers passed. No suspicious patterns, URL structure is safe, and no bot indicators detected."
            recommendation = "Content appears legitimate. Proceed with normal caution."
        elif verdict == "suspicious":
            summary = f"Some concerning indicators found: {', '.join(key_evidence[:2])}. While not confirmed malicious, exercise caution."
            recommendation = "Verify information through other sources before trusting."
        else:  # untrustworthy
            summary = f"Multiple critical issues detected: {', '.join(key_evidence[:2])}. Strong indicators this content is not trustworthy."
            recommendation = "Avoid this content. Do not click links or provide personal information."
        
        return {
            "verdict": verdict,
            "confidence": confidence,
            "summary": summary,
            "key_evidence": key_evidence,
            "recommendation": recommendation,
            "risk_level": risk_level,
            "layers_analyzed": {
                "inspector": True,
                "url_check": url_check is not None,
                "bot_check": bot_check is not None
            }
        }
    
    def _parse_response(self, content: str, layers: LayerResults) -> Dict[str, Any]:
        """Parse LLM response, fallback to rules if parsing fails"""
        try:
            # Try to extract JSON
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1:
                json_str = content[start:end+1]
                result = json.loads(json_str)
                
                # Ensure required fields
                required = ["verdict", "confidence", "summary", "key_evidence", "recommendation", "risk_level"]
                for field in required:
                    if field not in result:
                        result[field] = "unknown" if field != "key_evidence" else []
                
                result["layers_analyzed"] = {
                    "inspector": True,
                    "url_check": layers.url_check is not None,
                    "bot_check": layers.bot_check is not None
                }
                return result
        except Exception as e:
            print(f"[Parse Error] {e}")
        
        # Fallback to rule-based
        return self._rule_based_synthesis(layers)


# Singleton
_final_agent = None

def get_final_agent() -> FinalFrontierAgent:
    """Get or create Final Frontier Agent singleton"""
    global _final_agent
    if _final_agent is None:
        _final_agent = FinalFrontierAgent()
    return _final_agent


def synthesize_results(
    inspector_result: Dict[str, Any],
    content: str,
    url_result: Optional[Dict[str, Any]] = None,
    bot_result: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to run final synthesis
    
    Args:
        inspector_result: Content inspector results
        content: Original content
        url_result: URL safety check results (optional)
        bot_result: Bot detection results (optional)
        
    Returns:
        Final verdict with justification
    """
    agent = get_final_agent()
    layers = LayerResults(
        inspector=inspector_result,
        url_check=url_result,
        bot_check=bot_result,
        content=content
    )
    return agent.synthesize(layers)


if __name__ == "__main__":
    # Test
    test_layers = LayerResults(
        inspector={
            "red_flags": ["urgency", "suspicious_phrases"],
            "urls_count": 1,
            "accounts_count": 0,
            "confidence": "medium"
        },
        url_check={
            "prediction_class": 2,
            "prediction_label": "Phishing",
            "confidence": 85.5
        },
        content="URGENT: You won $1,000,000! Click https://evil.com now!!!"
    )
    
    agent = FinalFrontierAgent()
    result = agent.synthesize(test_layers)
    
    print("=" * 50)
    print("FINAL FRONTIER AGENT RESULT")
    print("=" * 50)
    print(json.dumps(result, indent=2))
