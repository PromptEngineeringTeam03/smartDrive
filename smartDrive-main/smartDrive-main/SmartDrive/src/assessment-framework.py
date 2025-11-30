"""
DriveSmart AI - Initial Assessment Framework
Run this to evaluate your current system before fine-tuning
"""

import json
import time
from datetime import datetime

# Define test scenarios covering different user personas and query types
TEST_SCENARIOS = [
    # Individual Driver Queries
    {
        "id": "driver_01",
        "persona": "individual_driver",
        "query": "Is it legal to use my phone at a red light in California?",
        "expected_topics": ["cell phone laws", "California Vehicle Code", "handheld device"],
        "jurisdiction": "California"
    },
    {
        "id": "driver_02",
        "persona": "individual_driver",
        "query": "What happens if I get caught driving 20 mph over the speed limit?",
        "expected_topics": ["speeding penalties", "points", "fine amount"],
        "jurisdiction": "general"
    },
    {
        "id": "driver_03",
        "persona": "individual_driver",
        "query": "Can I make a right turn on red?",
        "expected_topics": ["right turn", "red light", "complete stop"],
        "jurisdiction": "general"
    },
    # Fleet Manager Queries
    {
        "id": "fleet_01",
        "persona": "fleet_manager",
        "query": "What are the parking restrictions for commercial trucks in downtown areas?",
        "expected_topics": ["commercial vehicle", "parking regulations", "weight limits"],
        "jurisdiction": "general"
    },
    {
        "id": "fleet_02",
        "persona": "fleet_manager",
        "query": "What documentation must our delivery drivers carry?",
        "expected_topics": ["license", "registration", "insurance", "commercial"],
        "jurisdiction": "general"
    },
    # Legal/Educational Queries
    {
        "id": "legal_01",
        "persona": "legal_professional",
        "query": "Summarize the differences in DUI blood alcohol limits across states",
        "expected_topics": ["BAC", "DUI", "state comparison", "0.08"],
        "jurisdiction": "multi-state"
    },
    {
        "id": "edu_01",
        "persona": "educator",
        "query": "Explain right-of-way rules at a four-way stop for new drivers",
        "expected_topics": ["right-of-way", "four-way stop", "first to arrive"],
        "jurisdiction": "general"
    },
    # Edge Cases
    {
        "id": "edge_01",
        "persona": "individual_driver",
        "query": "I got a ticket but the sign was covered by a tree branch. Can I fight it?",
        "expected_topics": ["contesting ticket", "visibility", "defense"],
        "jurisdiction": "general"
    },
]


class AssessmentEvaluator:
    def __init__(self, chatbot_function):
        """
        Initialize with your chatbot's query function
        chatbot_function should accept a query string and return a response string
        """
        self.chatbot = chatbot_function
        self.results = []
    
    def evaluate_response(self, scenario, response, response_time):
        """Evaluate a single response against expected criteria"""
        
        # Check topic coverage
        topics_found = sum(
            1 for topic in scenario["expected_topics"] 
            if topic.lower() in response.lower()
        )
        topic_coverage = topics_found / len(scenario["expected_topics"])
        
        # Check response quality indicators
        has_citation = any(phrase in response.lower() for phrase in 
                         ["code", "section", "statute", "regulation", "cvc", "dmv"])
        has_disclaimer = any(phrase in response.lower() for phrase in 
                           ["not legal advice", "consult", "attorney", "lawyer"])
        is_clear = len(response) > 100 and len(response) < 2000
        
        return {
            "scenario_id": scenario["id"],
            "persona": scenario["persona"],
            "query": scenario["query"],
            "response_length": len(response),
            "response_time_ms": response_time,
            "topic_coverage": topic_coverage,
            "has_legal_citation": has_citation,
            "has_disclaimer": has_disclaimer,
            "appropriate_length": is_clear,
            "response_preview": response[:500] + "..." if len(response) > 500 else response
        }
    
    def run_assessment(self):
        """Run full assessment on all test scenarios"""
        print("=" * 60)
        print("DriveSmart AI - Initial Assessment")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        for scenario in TEST_SCENARIOS:
            print(f"\nTesting: {scenario['id']} ({scenario['persona']})")
            print(f"Query: {scenario['query'][:50]}...")
            
            # Time the response
            start = time.time()
            try:
                response = self.chatbot(scenario["query"])
                response_time = (time.time() - start) * 1000
                
                result = self.evaluate_response(scenario, response, response_time)
                result["status"] = "success"
                
            except Exception as e:
                result = {
                    "scenario_id": scenario["id"],
                    "status": "error",
                    "error": str(e)
                }
                response_time = (time.time() - start) * 1000
            
            self.results.append(result)
            print(f"  Status: {result['status']}, Time: {response_time:.0f}ms")
        
        return self.generate_report()
    
    def generate_report(self):
        """Generate assessment summary report"""
        successful = [r for r in self.results if r.get("status") == "success"]
        
        if not successful:
            return {"error": "No successful responses to analyze"}
        
        report = {
            "summary": {
                "total_scenarios": len(TEST_SCENARIOS),
                "successful": len(successful),
                "failed": len(self.results) - len(successful),
                "avg_response_time_ms": sum(r["response_time_ms"] for r in successful) / len(successful),
                "avg_topic_coverage": sum(r["topic_coverage"] for r in successful) / len(successful),
                "citation_rate": sum(1 for r in successful if r["has_legal_citation"]) / len(successful),
                "disclaimer_rate": sum(1 for r in successful if r["has_disclaimer"]) / len(successful),
            },
            "by_persona": {},
            "areas_for_improvement": [],
            "detailed_results": self.results
        }
        
        # Analyze by persona
        personas = set(r["persona"] for r in successful)
        for persona in personas:
            persona_results = [r for r in successful if r["persona"] == persona]
            report["by_persona"][persona] = {
                "avg_topic_coverage": sum(r["topic_coverage"] for r in persona_results) / len(persona_results),
                "avg_response_time_ms": sum(r["response_time_ms"] for r in persona_results) / len(persona_results),
            }
        
        # Identify areas for improvement
        if report["summary"]["avg_topic_coverage"] < 0.7:
            report["areas_for_improvement"].append("Low topic coverage - improve retrieval relevance")
        if report["summary"]["citation_rate"] < 0.8:
            report["areas_for_improvement"].append("Missing legal citations - add citation prompting")
        if report["summary"]["avg_response_time_ms"] > 3000:
            report["areas_for_improvement"].append("Slow response time - optimize retrieval")
        
        return report


# Example usage (integrate with your actual chatbot)
def example_usage():
    # Replace this with your actual chatbot function
    def your_chatbot(query):
        # This should call your LangGraph chain or RAG pipeline
        # from langraph import DrivesmartGraph
        # return DrivesmartGraph().invoke(query)
        return "Sample response for testing"
    
    evaluator = AssessmentEvaluator(your_chatbot)
    report = evaluator.run_assessment()
    
    # Save report
    with open("initial_assessment_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\n" + "=" * 60)
    print("ASSESSMENT SUMMARY")
    print("=" * 60)
    print(f"Success Rate: {report['summary']['successful']}/{report['summary']['total_scenarios']}")
    print(f"Avg Topic Coverage: {report['summary']['avg_topic_coverage']:.1%}")
    print(f"Avg Response Time: {report['summary']['avg_response_time_ms']:.0f}ms")
    print(f"Citation Rate: {report['summary']['citation_rate']:.1%}")
    print(f"\nAreas for Improvement:")
    for area in report["areas_for_improvement"]:
        print(f"  - {area}")
    
    return report


if __name__ == "__main__":
    example_usage()
