#!/usr/bin/env python3
"""
Content Inspector - First Layer of Filtering
Detects URLs, account info, and obvious signs of untrustworthy content
Routes to appropriate specialized tools
"""

import re
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from urllib.parse import urlparse


@dataclass
class InspectionResult:
    """Result from the Content Inspector"""
    content: str
    urls_found: List[str] = field(default_factory=list)
    accounts_found: List[str] = field(default_factory=list)
    obvious_red_flags: List[str] = field(default_factory=list)
    confidence: str = "medium"  # low, medium, high
    recommendation: str = ""
    needs_url_check: bool = False
    needs_bot_check: bool = False
    needs_final_agent: bool = True


class ContentInspector:
    """First layer AI Inspector for content analysis"""
    
    # Obvious red flag patterns
    RED_FLAGS = {
        "urgency": r"\b(urgent|hurry|act now|limited time|expires? soon|last chance|don'?t miss)\b",
        "suspicious_phrases": r"\b(congratulations.{0,30}won|you've been selected|free money|click here|verify now|confirm account)\b",
        "fake_domains": r"\b(googel|faceboook|twittter|instagrm|paypaal)\b",
        "all_caps": r"[A-Z]{5,}",
        "excessive_punctuation": r"[!?]{3,}",
        "suspicious_numbers": r"\b\d{16}|\d{4}[\s-]\d{4}[\s-]\d{4}[\s-]\d{4}\b",  # Credit card patterns
        "crypto_scam": r"\b(send \d+ (btc|eth|bitcoin|crypto).{0,50}(double|multiply|10x|instant))\b",
        "fake_news_markers": r"\b(shocking|you won'?t believe|doctors hate this|secret trick)\b",
    }
    
    # Social media platform patterns
    PLATFORM_PATTERNS = {
        "twitter": r"(?:twitter\.com|x\.com)/([a-zA-Z0-9_]{1,15})",
        "instagram": r"instagram\.com/([a-zA-Z0-9_.]{1,30})",
        "facebook": r"facebook\.com/([a-zA-Z0-9.]{5,50})",
        "linkedin": r"linkedin\.com/in/([a-zA-Z0-9-]{5,100})",
        "tiktok": r"tiktok\.com/@([a-zA-Z0-9_.]{1,24})",
        "youtube": r"youtube\.com/@?([a-zA-Z0-9_-]{1,50})",
    }
    
    def __init__(self):
        self.compiled_red_flags = {k: re.compile(v, re.IGNORECASE) for k, v in self.RED_FLAGS.items()}
        self.compiled_platforms = {k: re.compile(v, re.IGNORECASE) for k, v in self.PLATFORM_PATTERNS.items()}
    
    def extract_urls(self, text: str) -> List[str]:
        """Extract all URLs from text"""
        # Comprehensive URL pattern
        url_pattern = re.compile(
            r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:[\w.])*)?)?',
            re.IGNORECASE
        )
        urls = url_pattern.findall(text)
        
        # Also find URLs without protocol
        domain_pattern = re.compile(
            r'(?:^|\s)([a-zA-Z0-9][-a-zA-Z0-9]*\.[a-zA-Z]{2,}(?:/[^\s]*)?)',
            re.IGNORECASE
        )
        domains = domain_pattern.findall(text)
        
        # Normalize URLs
        all_urls = []
        for url in urls:
            all_urls.append(self._normalize_url(url))
        for domain in domains:
            if not domain.startswith(('http://', 'https://')):
                all_urls.append(self._normalize_url(domain))
        
        return list(set(all_urls))  # Remove duplicates
    
    def _normalize_url(self, url: str) -> str:
        """Normalize URL to https format"""
        url = url.strip()
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url
    
    def extract_accounts(self, text: str) -> List[Dict[str, str]]:
        """Extract social media account mentions"""
        accounts = []
        
        for platform, pattern in self.compiled_platforms.items():
            matches = pattern.findall(text)
            for match in matches:
                accounts.append({
                    "platform": platform,
                    "username": match,
                    "url": f"https://{platform}.com/{match}" if platform != "youtube" else f"https://youtube.com/@{match}"
                })
        
        # Look for @mentions that might be accounts
        mention_pattern = re.compile(r'@([a-zA-Z0-9_]{1,20})')
        mentions = mention_pattern.findall(text)
        for mention in mentions:
            if not any(a["username"] == mention for a in accounts):
                accounts.append({
                    "platform": "unknown",
                    "username": mention,
                    "url": None
                })
        
        return accounts
    
    def detect_obvious_red_flags(self, text: str) -> List[str]:
        """Detect obvious signs of untrustworthy/fake content"""
        red_flags = []
        
        text_lower = text.lower()
        
        for flag_name, pattern in self.compiled_red_flags.items():
            if pattern.search(text):
                red_flags.append(flag_name)
        
        # Check for AI-generated text markers
        if self._is_likely_ai_generated(text):
            red_flags.append("ai_generated_patterns")
        
        return red_flags
    
    def _is_likely_ai_generated(self, text: str) -> bool:
        """Heuristic detection of AI-generated text patterns"""
        # Common AI patterns
        ai_patterns = [
            r"\b(as an ai\b|as a language model|i cannot|i'm not able to)",
            r"\b(here are|below are|the following)\s+(?:some\s+)?(?:ways?|tips?|steps?|reasons?)",
            r"\b(it is important to note that|worth noting that|keep in mind that)",
            r"\b(delve|navigate|landscape|realm|tapestry)\b",
        ]
        
        score = 0
        for pattern in ai_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                score += 1
        
        # Check for repetitive sentence structures
        sentences = re.split(r'[.!?]+', text)
        if len(sentences) > 3:
            # Check if many sentences start the same way
            first_words = [s.strip().split()[0].lower() if s.strip() else '' for s in sentences[:5]]
            if len(set(first_words)) < 3:
                score += 1
        
        return score >= 2
    
    def analyze(self, content: str) -> InspectionResult:
        """
        Main analysis method - First layer filtering
        
        Returns:
            InspectionResult with detected elements and routing recommendations
        """
        # Extract components
        urls = self.extract_urls(content)
        accounts = self.extract_accounts(content)
        red_flags = self.detect_obvious_red_flags(content)
        
        # Determine confidence based on red flags
        if len(red_flags) >= 3:
            confidence = "high"
            recommendation = "High likelihood of untrustworthy content. Multiple red flags detected."
        elif len(red_flags) >= 1:
            confidence = "medium"
            recommendation = "Some suspicious patterns detected. Needs deeper analysis."
        else:
            confidence = "low"
            recommendation = "No obvious red flags. Proceed with standard verification."
        
        # Determine what checks are needed
        needs_url_check = len(urls) > 0
        needs_bot_check = len(accounts) > 0
        
        # If we found obvious red flags, we definitely need the final agent
        needs_final_agent = True
        
        return InspectionResult(
            content=content,
            urls_found=urls,
            accounts_found=[a["username"] for a in accounts],
            obvious_red_flags=red_flags,
            confidence=confidence,
            recommendation=recommendation,
            needs_url_check=needs_url_check,
            needs_bot_check=needs_bot_check,
            needs_final_agent=needs_final_agent
        )
    
    def get_summary(self, result: InspectionResult) -> Dict[str, Any]:
        """Get a summary of the inspection for the next layers"""
        return {
            "layer": "inspector",
            "urls_count": len(result.urls_found),
            "accounts_count": len(result.accounts_found),
            "red_flags_count": len(result.obvious_red_flags),
            "red_flags": result.obvious_red_flags,
            "confidence": result.confidence,
            "needs_url_check": result.needs_url_check,
            "needs_bot_check": result.needs_bot_check,
            "routing_decision": self._get_routing_decision(result)
        }
    
    def _get_routing_decision(self, result: InspectionResult) -> str:
        """Determine routing based on inspection results"""
        routes = []
        if result.needs_url_check:
            routes.append("url_pipeline")
        if result.needs_bot_check:
            routes.append("bot_detection")
        if result.obvious_red_flags:
            routes.append("urgent_review")
        
        if not routes:
            return "standard_verification"
        
        return " + ".join(routes)


# Singleton instance
_inspector = None

def get_inspector() -> ContentInspector:
    """Get or create the Content Inspector singleton"""
    global _inspector
    if _inspector is None:
        _inspector = ContentInspector()
    return _inspector


def inspect_content(content: str) -> Dict[str, Any]:
    """Convenience function to inspect content and return summary"""
    inspector = get_inspector()
    result = inspector.analyze(content)
    return inspector.get_summary(result)


if __name__ == "__main__":
    # Test the inspector
    test_content = """
    Hey! Check out this amazing offer at https://googel.com/free-money 
    URGENT: You won $1,000,000! Click here now!!! 
    Contact @john_doe on Twitter for details.
    """
    
    inspector = ContentInspector()
    result = inspector.analyze(test_content)
    
    print("=" * 50)
    print("CONTENT INSPECTION RESULT")
    print("=" * 50)
    print(f"URLs Found: {result.urls_found}")
    print(f"Accounts Found: {result.accounts_found}")
    print(f"Red Flags: {result.obvious_red_flags}")
    print(f"Confidence: {result.confidence}")
    print(f"Recommendation: {result.recommendation}")
    print(f"Needs URL Check: {result.needs_url_check}")
    print(f"Needs Bot Check: {result.needs_bot_check}")
    print("=" * 50)
    print(json.dumps(inspector.get_summary(result), indent=2))
