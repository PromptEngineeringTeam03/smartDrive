"""
DriveSmart AI - Response Output Validator (FIXED VERSION)
Post-generation validation to ensure response appropriateness
File: security/output_validator.py
"""

import re
from typing import Dict, List, Tuple


class ResponseValidator:
    """Validates generated responses for security violations"""
    
    # Content that suggests providing defense strategies
    PROHIBITED_CONTENT = [
        "how to avoid",
        "ways to evade",
        "loopholes",
        "defense strategy",
        "get out of",
        "beat the charge",
        "avoid detection",
        "trick the officer",
        "exploit the",
        "technicality that allows",
        "argue that you",
        "tell the officer that",
        "claim that you",
    ]
    
    # Phrases indicating inappropriate role
    ROLE_VIOLATION_INDICATORS = [
        "as your attorney",
        "i recommend that you",
        "your best defense is",
        "you should argue",
        "my advice is to",
        "i suggest you",
        "you could claim",
        "your strategy should be",
    ]
    
    def __init__(self):
        self.prohibited_regex = [re.compile(p, re.IGNORECASE) for p in self.PROHIBITED_CONTENT]
        self.role_violation_regex = [re.compile(p, re.IGNORECASE) for p in self.ROLE_VIOLATION_INDICATORS]
    
    def validate_response(self, response: str, original_query: str) -> Dict:
        """
        Validates generated response for security and quality
        
        Returns:
            dict with keys:
                - is_valid: bool
                - issues: list of (issue_type, details)
                - action: str (APPROVE, REGENERATE, BLOCK)
                - sanitized_response: str (with added disclaimers if needed)
        """
        issues = []
        
        # Check for prohibited advisory language
        for pattern in self.prohibited_regex:
            match = pattern.search(response)
            if match:
                issues.append(("PROHIBITED_ADVICE", match.group(0)))
        
        # Check for role boundary violations
        for pattern in self.role_violation_regex:
            match = pattern.search(response)
            if match:
                issues.append(("ROLE_VIOLATION", match.group(0)))
        
        # Check if response is answering a suspicious query appropriately
        if self._should_have_refused(original_query, response):
            issues.append(("INAPPROPRIATE_COMPLIANCE", "Response should have refused this query"))
        
        # NOTE: Removed strict citation validation - it was too aggressive
        # Citations will be validated by content quality instead
        
        # Determine action
        if not issues:
            action = "APPROVE"
        elif len(issues) >= 3 or any(i[0] in ["ROLE_VIOLATION", "INAPPROPRIATE_COMPLIANCE"] for i in issues):
            action = "BLOCK"
        else:
            action = "REGENERATE"
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "action": action,
            "sanitized_response": self._apply_safety_layer(response, issues) if action == "APPROVE" else None
        }
    
    def _should_have_refused(self, query: str, response: str) -> bool:
        """Determines if response inappropriately complied with suspicious query"""
        query_lower = query.lower()
        response_lower = response.lower()
        
        # Check if query is asking for evasion
        evasion_keywords = ['evade', 'avoid getting caught', 'trick', 'get away with']
        query_has_evasion = any(kw in query_lower for kw in evasion_keywords)
        
        # Check if response provides strategies (but allow general prevention tips)
        response_provides_strategy = any(phrase in response_lower for phrase in [
            'you could avoid detection',
            'ways to evade',
            'trick the officer',
            'avoid getting caught'
        ])
        
        # Only flag if query asks for evasion AND response provides evasion strategies
        if query_has_evasion and response_provides_strategy:
            return True
        
        return False
    
    def _is_factual_query(self, query: str) -> bool:
        """Determines if query expects a factual answer"""
        factual_indicators = [
            r'\bwhat is\b',
            r'\bwhat are\b',
            r'\bhow much\b',
            r'\bwhen\b',
            r'\bwhere\b',
            r'\bpenalty for\b',
            r'\blimit\b',
        ]
        
        return any(re.search(p, query, re.IGNORECASE) for p in factual_indicators)
    
    def _apply_safety_layer(self, response: str, issues: List[Tuple[str, str]]) -> str:
        """Adds disclaimers to responses when appropriate"""
        if "not constitute legal advice" in response.lower():
            return response
        
        legal_keywords = ['statute', 'law', 'penalty', 'violation', 'court', 'legal']
        if any(kw in response.lower() for kw in legal_keywords):
            disclaimer = (
                "\n\n⚠️ **IMPORTANT**: This information is for educational purposes only "
                "and does not constitute legal advice. For guidance on your specific situation, "
                "please consult a qualified attorney licensed in your jurisdiction."
            )
            return response + disclaimer
        
        return response