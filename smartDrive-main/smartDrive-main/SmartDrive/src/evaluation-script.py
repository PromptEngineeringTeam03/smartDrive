"""
DriveSmart AI - Post Fine-Tuning Evaluation
Compare before/after performance to demonstrate improvement
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Callable

# Import your assessment framework
# from assessment_framework import TEST_SCENARIOS, AssessmentEvaluator


class ComparativeEvaluator:
    """Compare baseline vs fine-tuned model performance"""
    
    def __init__(self):
        self.results = {
            "baseline": [],
            "finetuned": []
        }
        
    def run_comparison(
        self, 
        baseline_fn: Callable, 
        finetuned_fn: Callable,
        test_scenarios: List[Dict]
    ) -> Dict:
        """Run same tests on both models"""
        
        print("=" * 60)
        print("COMPARATIVE EVALUATION")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        for scenario in test_scenarios:
            print(f"\nScenario: {scenario['id']}")
            
            # Test baseline
            start = time.time()
            baseline_response = baseline_fn(scenario["query"])
            baseline_time = (time.time() - start) * 1000
            
            # Test fine-tuned
            start = time.time()
            finetuned_response = finetuned_fn(scenario["query"])
            finetuned_time = (time.time() - start) * 1000
            
            # Score both
            baseline_score = self._score_response(scenario, baseline_response)
            finetuned_score = self._score_response(scenario, finetuned_response)
            
            self.results["baseline"].append({
                "scenario_id": scenario["id"],
                "response_time_ms": baseline_time,
                **baseline_score
            })
            
            self.results["finetuned"].append({
                "scenario_id": scenario["id"],
                "response_time_ms": finetuned_time,
                **finetuned_score
            })
            
            # Show improvement
            improvement = finetuned_score["total_score"] - baseline_score["total_score"]
            symbol = "↑" if improvement > 0 else "↓" if improvement < 0 else "="
            print(f"  Baseline: {baseline_score['total_score']:.2f} | Fine-tuned: {finetuned_score['total_score']:.2f} ({symbol}{abs(improvement):.2f})")
        
        return self._generate_comparison_report()
    
    def _score_response(self, scenario: Dict, response: str) -> Dict:
        """Score a response on multiple dimensions"""
        
        scores = {}
        
        # 1. Topic Coverage (0-1)
        topics_found = sum(
            1 for topic in scenario["expected_topics"]
            if topic.lower() in response.lower()
        )
        scores["topic_coverage"] = topics_found / len(scenario["expected_topics"])
        
        # 2. Has Legal Citation (0-1)
        citation_terms = ["code", "section", "statute", "cvc", "regulation", "dmv"]
        scores["has_citation"] = 1.0 if any(t in response.lower() for t in citation_terms) else 0.0
        
        # 3. Has Disclaimer (0-1)
        disclaimer_terms = ["not legal advice", "consult", "attorney", "disclaimer"]
        scores["has_disclaimer"] = 1.0 if any(t in response.lower() for t in disclaimer_terms) else 0.0
        
        # 4. Response Quality (0-1) - based on length appropriateness
        length = len(response)
        if 200 <= length <= 1500:
            scores["length_score"] = 1.0
        elif 100 <= length < 200 or 1500 < length <= 2000:
            scores["length_score"] = 0.7
        else:
            scores["length_score"] = 0.3
        
        # 5. Clarity - no excessive jargon, has structure
        has_structure = "\n" in response or ":" in response
        scores["clarity"] = 1.0 if has_structure else 0.5
        
        # Total weighted score
        weights = {
            "topic_coverage": 0.35,
            "has_citation": 0.25,
            "has_disclaimer": 0.15,
            "length_score": 0.15,
            "clarity": 0.10
        }
        
        scores["total_score"] = sum(
            scores[k] * weights[k] for k in weights
        )
        
        return scores
    
    def _generate_comparison_report(self) -> Dict:
        """Generate detailed comparison report"""
        
        def avg(results, key):
            return sum(r[key] for r in results) / len(results) if results else 0
        
        report = {
            "summary": {
                "num_scenarios": len(self.results["baseline"]),
                "timestamp": datetime.now().isoformat()
            },
            "baseline_metrics": {
                "avg_total_score": avg(self.results["baseline"], "total_score"),
                "avg_topic_coverage": avg(self.results["baseline"], "topic_coverage"),
                "avg_response_time_ms": avg(self.results["baseline"], "response_time_ms"),
                "citation_rate": avg(self.results["baseline"], "has_citation"),
                "disclaimer_rate": avg(self.results["baseline"], "has_disclaimer"),
            },
            "finetuned_metrics": {
                "avg_total_score": avg(self.results["finetuned"], "total_score"),
                "avg_topic_coverage": avg(self.results["finetuned"], "topic_coverage"),
                "avg_response_time_ms": avg(self.results["finetuned"], "response_time_ms"),
                "citation_rate": avg(self.results["finetuned"], "citation_rate") if "citation_rate" in self.results["finetuned"][0] else avg(self.results["finetuned"], "has_citation"),
                "disclaimer_rate": avg(self.results["finetuned"], "has_disclaimer"),
            },
            "improvements": {},
            "detailed_results": self.results
        }
        
        # Calculate improvements
        for metric in ["avg_total_score", "avg_topic_coverage", "citation_rate", "disclaimer_rate"]:
            baseline_val = report["baseline_metrics"][metric]
            finetuned_val = report["finetuned_metrics"][metric]
            
            if baseline_val > 0:
                pct_change = ((finetuned_val - baseline_val) / baseline_val) * 100
            else:
                pct_change = 100 if finetuned_val > 0 else 0
            
            report["improvements"][metric] = {
                "absolute_change": finetuned_val - baseline_val,
                "percent_change": pct_change
            }
        
        return report
    
    def print_report(self, report: Dict):
        """Print formatted report"""
        
        print("\n" + "=" * 60)
        print("EVALUATION REPORT")
        print("=" * 60)
        
        print("\n📊 METRIC COMPARISON")
        print("-" * 50)
        print(f"{'Metric':<25} {'Baseline':>12} {'Fine-tuned':>12} {'Change':>10}")
        print("-" * 50)
        
        metrics = [
            ("Total Score", "avg_total_score"),
            ("Topic Coverage", "avg_topic_coverage"),
            ("Citation Rate", "citation_rate"),
            ("Disclaimer Rate", "disclaimer_rate"),
            ("Response Time (ms)", "avg_response_time_ms"),
        ]
        
        for name, key in metrics:
            baseline = report["baseline_metrics"][key]
            finetuned = report["finetuned_metrics"][key]
            change = finetuned - baseline
            
            if key != "avg_response_time_ms":
                print(f"{name:<25} {baseline:>11.1%} {finetuned:>11.1%} {change:>+9.1%}")
            else:
                print(f"{name:<25} {baseline:>11.0f} {finetuned:>11.0f} {change:>+9.0f}")
        
        print("\n📈 KEY IMPROVEMENTS")
        print("-" * 50)
        
        for metric, data in report["improvements"].items():
            if data["percent_change"] > 0:
                print(f"✅ {metric}: +{data['percent_change']:.1f}%")
            elif data["percent_change"] < 0:
                print(f"⚠️  {metric}: {data['percent_change']:.1f}%")
        
        # Overall verdict
        overall_improvement = report["improvements"]["avg_total_score"]["percent_change"]
        print("\n" + "=" * 60)
        if overall_improvement > 10:
            print(f"🎉 SIGNIFICANT IMPROVEMENT: +{overall_improvement:.1f}% overall")
        elif overall_improvement > 0:
            print(f"✅ MODERATE IMPROVEMENT: +{overall_improvement:.1f}% overall")
        else:
            print(f"⚠️  NO IMPROVEMENT: {overall_improvement:.1f}% overall")
        print("=" * 60)


def run_full_evaluation():
    """Main evaluation runner"""
    
    # Import your actual implementations
    # from vector_store import VectorStore
    # from langraph import DrivesmartGraph
    
    # Example: Create baseline and fine-tuned query functions
    def baseline_query(query: str) -> str:
        # Your baseline RAG implementation
        # return DrivesmartGraph(embedding_model="default").invoke(query)
        return "Sample baseline response with legal information."
    
    def finetuned_query(query: str) -> str:
        # Your fine-tuned RAG implementation
        # return DrivesmartGraph(embedding_model="models/drivesmart-embeddings").invoke(query)
        return "Sample fine-tuned response with CVC Section 23123.5 citation and disclaimer."
    
    # Test scenarios
    test_scenarios = [
        {
            "id": "test_01",
            "query": "Can I use my phone at a red light in California?",
            "expected_topics": ["phone", "california", "vehicle code", "fine"]
        },
        {
            "id": "test_02", 
            "query": "What is the penalty for running a stop sign?",
            "expected_topics": ["stop sign", "fine", "points", "violation"]
        },
        {
            "id": "test_03",
            "query": "Explain right-of-way at a four-way stop",
            "expected_topics": ["right-of-way", "first", "arrive", "yield"]
        },
    ]
    
    # Run evaluation
    evaluator = ComparativeEvaluator()
    report = evaluator.run_comparison(baseline_query, finetuned_query, test_scenarios)
    
    # Print and save report
    evaluator.print_report(report)
    
    with open("evaluation_report.json", "w") as f:
        json.dump(report, f, indent=2)
    
    print("\nReport saved to: evaluation_report.json")
    
    return report


if __name__ == "__main__":
    run_full_evaluation()
