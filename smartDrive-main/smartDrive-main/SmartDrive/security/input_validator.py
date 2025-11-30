"""
DriveSmart AI - Input Security Validator
Detects and neutralizes prompt injection attempts
File: security/input_validator.py
"""

import re
from typing import Dict, List, Tuple
from datetime import datetime


class PromptSecurityValidator:
    """Pre-processes user inputs to detect and neutralize prompt injection attempts"""
    
    # Patterns indicating direct injection attempts
    MALICIOUS_PATTERNS = [
        r'ignore (all |previous )?instructions',
        r'you are now (a |an )?',
        r'repeat (back )?your (system )?instructions',
        r'admin mode|system mode|developer mode',
        r'disregard (all |previous )?rules',
        r'new (role|instructions|rules)',
        r'SYSTEM:|ADMIN:|OVERRIDE:',
        r'<\|system\|>|<\|admin\|>',
        r'forget (all |previous )?instructions',
        r'act as (a |an )?',
        r'pretend (to be|you are)',
        r'your new role is',
    ]
    
    # Patterns indicating jailbreak attempts
    JAILBREAK_PATTERNS = [
        r"i'm writing (a novel|a story|fiction|a book)",
        r"hypothetically speaking",
        r"for (educational|research|academic) purposes only",
        r"according to (a )?recent (ruling|law|case)",
        r"in a fictional scenario",
        r"imagine (you are|that)",
        r"let's play a game where",
        r"what would you do if",
    ]
    
    # Patterns suggesting evasion intent
    EVASION_PATTERNS = [
        r"(how to|ways to) (avoid|evade|escape|get out of)",
        r"loopholes? (in|for)",
        r"tricks? to (avoid|evade)",
        r"get away with",
        r"without getting caught",
        r"bypass (the )?(law|rule|regulation)",
    ]
    
    def __init__(self):
        # Compile patterns for better performance
        self.malicious_regex = [re.compile(p, re.IGNORECASE) for p in self.MALICIOUS_PATTERNS]
        self.jailbreak_regex = [re.compile(p, re.IGNORECASE) for p in self.JAILBREAK_PATTERNS]
        self.evasion_regex = [re.compile(p, re.IGNORECASE) for p in self.EVASION_PATTERNS]
    
    def validate_input(self, user_query: str) -> Dict:
        """
        Validates user input for security threats
        
        Returns:
            dict with keys:
                - is_safe: bool
                - flags: list of (flag_type, pattern_matched)
                - risk_level: str (SAFE, MEDIUM, HIGH, CRITICAL)
                - sanitized_query: str or None
        """
        flags = []
        query_lower = user_query.lower()
        
        # Check for direct injection attempts
        for pattern in self.malicious_regex:
            match = pattern.search(user_query)
            if match:
                flags.append(("INJECTION_ATTEMPT", match.group(0)))
        
        # Check for jailbreak attempts
        for pattern in self.jailbreak_regex:
            match = pattern.search(user_query)
            if match:
                flags.append(("JAILBREAK_ATTEMPT", match.group(0)))
        
        # Check for evasion intent
        for pattern in self.evasion_regex:
            match = pattern.search(user_query)
            if match:
                flags.append(("EVASION_INTENT", match.group(0)))
        
        # Check for fake citations
        if self._has_suspicious_citation(user_query):
            flags.append(("SUSPICIOUS_CITATION", "Unverified case citation detected"))
        
        # Check for encoding attempts (Base64, hex, etc.)
        if self._has_encoding_attempt(user_query):
            flags.append(("ENCODING_ATTEMPT", "Encoded content detected"))
        
        # Check for excessive special characters (obfuscation)
        if self._has_obfuscation(user_query):
            flags.append(("OBFUSCATION", "Unusual character patterns detected"))
        
        risk_level = self._calculate_risk_level(flags)
        
        return {
            "is_safe": len(flags) == 0,
            "flags": flags,
            "risk_level": risk_level,
            "sanitized_query": user_query if len(flags) == 0 else None,
            "timestamp": datetime.now().isoformat()
        }
    
    def _has_suspicious_citation(self, query: str) -> bool:
        """Detects potentially fabricated legal citations"""
        citation_pattern = r'\b\w+\s+v\.?\s+\w+\s*\(?\s*\d{4}\s*\)?'
        
        current_year = datetime.now().year
        matches = re.finditer(citation_pattern, query, re.IGNORECASE)
        
        for match in matches:
            year_match = re.search(r'\d{4}', match.group(0))
            if year_match:
                year = int(year_match.group(0))
                if year >= current_year:
                    return True
        
        return False
    
    def _has_encoding_attempt(self, query: str) -> bool:
        """Detects Base64, hex, or other encoding schemes"""
        base64_pattern = r'[A-Za-z0-9+/]{20,}={0,2}'
        if re.search(base64_pattern, query):
            potential_b64 = re.findall(base64_pattern, query)
            for b64 in potential_b64:
                if len(b64) % 4 == 0 or b64.endswith('='):
                    return True
        
        hex_pattern = r'(?:0x|\\x)[0-9a-fA-F]{2,}'
        if re.search(hex_pattern, query):
            return True
        
        return False
    
    def _has_obfuscation(self, query: str) -> bool:
        """Detects unusual Unicode or character obfuscation"""
        unicode_count = sum(1 for c in query if ord(c) > 127)
        
        if len(query) > 0 and (unicode_count / len(query)) > 0.2:
            return True
        
        special_chars = sum(1 for c in query if c in '!@#$%^&*()_+-=[]{}|;:,.<>?~`')
        if len(query) > 0 and (special_chars / len(query)) > 0.3:
            return True
        
        return False
    
    def _calculate_risk_level(self, flags: List[Tuple[str, str]]) -> str:
        """Categorizes threat level based on detected flags"""
        if not flags:
            return "SAFE"
        
        injection_count = sum(1 for f in flags if f[0] == "INJECTION_ATTEMPT")
        critical_flags = sum(1 for f in flags if f[0] in ["INJECTION_ATTEMPT", "ENCODING_ATTEMPT"])
        
        if injection_count >= 2 or critical_flags >= 3:
            return "CRITICAL"
        elif injection_count >= 1 or critical_flags >= 2:
            return "HIGH"
        elif len(flags) >= 2:
            return "MEDIUM"
        else:
            return "LOW"