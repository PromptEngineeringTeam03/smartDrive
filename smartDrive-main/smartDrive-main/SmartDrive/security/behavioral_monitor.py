"""
DriveSmart AI - Behavioral Monitoring System
Tracks user behavior patterns to detect coordinated attacks
File: security/behavioral_monitor.py
"""

from datetime import datetime, timedelta
from typing import Dict, List
from collections import defaultdict


class BehavioralMonitor:
    """Monitors user behavior patterns to detect systematic attacks"""
    
    def __init__(self, session_timeout_minutes: int = 30):
        self.user_sessions = {}
        self.session_timeout = timedelta(minutes=session_timeout_minutes)
        
        # Thresholds for detection
        self.RAPID_QUERY_THRESHOLD = 10
        self.RAPID_QUERY_WINDOW = 60
        self.HIGH_ATTACK_RATIO = 0.4
        self.MIN_QUERIES_FOR_ANALYSIS = 5
        self.SYSTEMATIC_PROBING_THRESHOLD = 3
    
    def analyze_session(self, session_id: str, query: str, validation_result: Dict) -> Dict:
        """
        Tracks patterns that might indicate systematic probing
        
        Returns:
            dict with keys:
                - session_risk: str (NORMAL, ELEVATED, HIGH)
                - indicators: list of risk indicators
                - action: str (CONTINUE, WARNING, RATE_LIMIT, BLOCK)
                - details: dict with session statistics
        """
        self._cleanup_expired_sessions()
        
        if session_id not in self.user_sessions:
            self.user_sessions[session_id] = self._create_new_session()
        
        session = self.user_sessions[session_id]
        session["last_activity"] = datetime.now()
        session["query_count"] += 1
        session["queries"].append({
            "query": query[:100],
            "timestamp": datetime.now(),
            "was_flagged": not validation_result.get("is_safe", True),
            "flags": validation_result.get("flags", [])
        })
        
        if not validation_result.get("is_safe", True):
            session["flagged_queries"] += 1
            session["attack_patterns"].extend(validation_result.get("flags", []))
        
        risk_indicators = self._detect_risk_patterns(session)
        session_risk = self._calculate_session_risk(risk_indicators)
        action = self._determine_action(session_risk, session)
        
        return {
            "session_risk": session_risk,
            "indicators": risk_indicators,
            "action": action,
            "details": {
                "total_queries": session["query_count"],
                "flagged_queries": session["flagged_queries"],
                "session_duration_minutes": self._get_session_duration(session),
                "unique_attack_types": len(set(flag[0] for flag in session["attack_patterns"]))
            }
        }
    
    def _create_new_session(self) -> Dict:
        """Creates a new session tracking object"""
        return {
            "query_count": 0,
            "flagged_queries": 0,
            "attack_patterns": [],
            "queries": [],
            "start_time": datetime.now(),
            "last_activity": datetime.now(),
            "warnings_issued": 0,
            "rate_limited": False
        }
    
    def _detect_risk_patterns(self, session: Dict) -> List[str]:
        """Detects suspicious behavioral patterns"""
        indicators = []
        
        # Rapid-fire queries
        if session["query_count"] >= self.RAPID_QUERY_THRESHOLD:
            duration = (datetime.now() - session["start_time"]).seconds
            if duration < self.RAPID_QUERY_WINDOW:
                indicators.append("RAPID_QUERY_PATTERN")
        
        # High proportion of flagged queries
        if session["query_count"] >= self.MIN_QUERIES_FOR_ANALYSIS:
            attack_ratio = session["flagged_queries"] / session["query_count"]
            if attack_ratio > self.HIGH_ATTACK_RATIO:
                indicators.append("HIGH_ATTACK_RATIO")
        
        # Systematic pattern testing
        unique_attack_types = len(set(flag[0] for flag in session["attack_patterns"]))
        if unique_attack_types >= self.SYSTEMATIC_PROBING_THRESHOLD:
            indicators.append("SYSTEMATIC_PROBING")
        
        # Escalation pattern
        if self._detect_escalation(session):
            indicators.append("ESCALATING_ATTACKS")
        
        # Trust-building then attack pattern
        if self._detect_trust_building(session):
            indicators.append("TRUST_BUILDING_ATTACK")
        
        # Repeated similar attacks (fuzzing)
        if self._detect_fuzzing(session):
            indicators.append("FUZZING_ATTACK")
        
        return indicators
    
    def _detect_escalation(self, session: Dict) -> bool:
        """Detects if attacks are becoming more severe over time"""
        if len(session["queries"]) < 5:
            return False
        
        midpoint = len(session["queries"]) // 2
        first_half = session["queries"][:midpoint]
        second_half = session["queries"][midpoint:]
        
        first_half_flagged = sum(1 for q in first_half if q["was_flagged"])
        second_half_flagged = sum(1 for q in second_half if q["was_flagged"])
        
        if len(second_half) > 0:
            second_ratio = second_half_flagged / len(second_half)
            if len(first_half) > 0:
                first_ratio = first_half_flagged / len(first_half)
                return second_ratio > first_ratio + 0.3
        
        return False
    
    def _detect_trust_building(self, session: Dict) -> bool:
        """Detects pattern of legitimate queries followed by malicious ones"""
        if len(session["queries"]) < 4:
            return False
        
        recent_queries = session["queries"][-5:]
        early_queries = session["queries"][:3]
        
        early_safe = sum(1 for q in early_queries if not q["was_flagged"])
        recent_flagged = sum(1 for q in recent_queries if q["was_flagged"])
        
        return early_safe >= 2 and recent_flagged >= 3
    
    def _detect_fuzzing(self, session: Dict) -> bool:
        """Detects repeated similar attack attempts"""
        if len(session["attack_patterns"]) < 5:
            return False
        
        attack_counts = defaultdict(int)
        for flag_type, _ in session["attack_patterns"]:
            attack_counts[flag_type] += 1
        
        return any(count >= 4 for count in attack_counts.values())
    
    def _calculate_session_risk(self, indicators: List[str]) -> str:
        """Categorizes overall session risk level"""
        if not indicators:
            return "NORMAL"
        
        high_severity = ["SYSTEMATIC_PROBING", "ESCALATING_ATTACKS", "FUZZING_ATTACK"]
        
        if any(ind in high_severity for ind in indicators):
            return "HIGH"
        elif len(indicators) >= 2:
            return "ELEVATED"
        else:
            return "ELEVATED"
    
    def _determine_action(self, risk_level: str, session: Dict) -> str:
        """Determines what action to take based on risk assessment"""
        if risk_level == "NORMAL":
            return "CONTINUE"
        
        if risk_level == "ELEVATED":
            if session["warnings_issued"] == 0:
                session["warnings_issued"] += 1
                return "WARNING"
            else:
                return "RATE_LIMIT"
        
        if risk_level == "HIGH":
            if session["rate_limited"]:
                return "BLOCK"
            else:
                session["rate_limited"] = True
                return "RATE_LIMIT"
        
        return "CONTINUE"
    
    def _get_session_duration(self, session: Dict) -> float:
        """Calculates session duration in minutes"""
        duration = datetime.now() - session["start_time"]
        return duration.total_seconds() / 60
    
    def _cleanup_expired_sessions(self):
        """Removes sessions that have exceeded timeout"""
        current_time = datetime.now()
        expired = []
        
        for session_id, session in self.user_sessions.items():
            if current_time - session["last_activity"] > self.session_timeout:
                expired.append(session_id)
        
        for session_id in expired:
            del self.user_sessions[session_id]
    
    def get_session_summary(self, session_id: str) -> Dict:
        """Returns detailed summary of a session"""
        if session_id not in self.user_sessions:
            return {"error": "Session not found"}
        
        session = self.user_sessions[session_id]
        
        attack_distribution = defaultdict(int)
        for flag_type, _ in session["attack_patterns"]:
            attack_distribution[flag_type] += 1
        
        return {
            "session_id": session_id,
            "total_queries": session["query_count"],
            "flagged_queries": session["flagged_queries"],
            "attack_ratio": session["flagged_queries"] / session["query_count"] if session["query_count"] > 0 else 0,
            "duration_minutes": self._get_session_duration(session),
            "unique_attack_types": len(attack_distribution),
            "attack_distribution": dict(attack_distribution),
            "warnings_issued": session["warnings_issued"],
            "rate_limited": session["rate_limited"],
            "start_time": session["start_time"].isoformat(),
            "last_activity": session["last_activity"].isoformat()
        }