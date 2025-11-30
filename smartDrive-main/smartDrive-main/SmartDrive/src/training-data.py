"""
DriveSmart AI - Training Data Preparation
Creates fine-tuning dataset from traffic law sources
"""

import json
from typing import List, Dict

# =============================================================================
# OPTION 1: Training data for EMBEDDING MODEL fine-tuning (Recommended)
# This improves your RAG retrieval quality
# =============================================================================

RETRIEVAL_TRAINING_PAIRS = [
    # Format: (user_query, relevant_passage_from_your_documents)
    {
        "query": "Can I use my phone at a red light in California?",
        "positive": "California Vehicle Code Section 23123.5 prohibits drivers from holding and operating a handheld wireless telephone or electronic wireless communications device while driving. The law applies whenever the vehicle is on a roadway, including when stopped at traffic signals.",
        "hard_negative": "Pedestrians must obey traffic signals when crossing at intersections. Red lights indicate pedestrians should not enter the crosswalk."
    },
    {
        "query": "What's the fine for running a stop sign?",
        "positive": "Failure to stop at a stop sign (CVC 22450) carries a base fine of approximately $35, but with penalty assessments and fees, the total typically ranges from $200-$250. Additionally, one point is added to the driver's record.",
        "hard_negative": "Stop signs must be installed at intersections where traffic studies indicate they are warranted based on traffic volume and accident history."
    },
    {
        "query": "How many points until my license is suspended?",
        "positive": "In California, the DMV may suspend your license if you accumulate: 4 points in 12 months, 6 points in 24 months, or 8 points in 36 months. Points remain on your record for 3-10 years depending on the violation type.",
        "hard_negative": "License plates must be clearly visible and properly mounted on both the front and rear of the vehicle."
    },
    {
        "query": "Is it legal to drive in the carpool lane alone?",
        "positive": "High-Occupancy Vehicle (HOV) lanes require a minimum of 2 occupants during posted hours, typically 6-9 AM and 3-7 PM on weekdays. Exceptions include motorcycles, eligible clean air vehicles with proper decals, and certain toll-paying vehicles.",
        "hard_negative": "Lane markings must be maintained by the responsible highway authority to ensure visibility in all weather conditions."
    },
    {
        "query": "What should I do if I get pulled over?",
        "positive": "When stopped by law enforcement, safely pull to the right side of the road, turn off your engine, and remain in the vehicle. Keep your hands visible, typically on the steering wheel. Provide license, registration, and proof of insurance when requested.",
        "hard_negative": "Emergency vehicles responding to calls have the right of way and other vehicles must yield by pulling to the right."
    },
    # Add 50-200 more pairs from your actual traffic law documents
]


def prepare_embedding_training_data(pairs: List[Dict]) -> Dict:
    """Prepare data for sentence-transformers fine-tuning"""
    
    training_data = {
        "queries": {},
        "corpus": {},
        "relevant_docs": {}
    }
    
    for idx, pair in enumerate(pairs):
        query_id = f"q{idx}"
        pos_id = f"pos{idx}"
        neg_id = f"neg{idx}"
        
        training_data["queries"][query_id] = pair["query"]
        training_data["corpus"][pos_id] = pair["positive"]
        training_data["corpus"][neg_id] = pair["hard_negative"]
        training_data["relevant_docs"][query_id] = [pos_id]
    
    return training_data


# =============================================================================
# OPTION 2: Training data for LLM fine-tuning (if required by assignment)
# Format for instruction fine-tuning
# =============================================================================

LLM_TRAINING_DATA = [
    {
        "system": "You are DriveSmart AI, a certified traffic law instructor. Provide accurate, jurisdiction-specific traffic law information with legal citations. Always include a disclaimer that this is not legal advice.",
        "instruction": "Is it legal to use my phone at a red light in California?",
        "response": """Using a handheld phone while stopped at a red light in California is NOT legal.

**Legal Basis:** California Vehicle Code Section 23123.5 prohibits drivers from holding and operating a handheld wireless telephone or electronic wireless communications device while driving a motor vehicle. The law applies whenever the motor vehicle is upon a highway, which includes being stopped at traffic signals.

**Key Points:**
- The prohibition applies even when the vehicle is temporarily stopped
- Hands-free operation using voice commands is permitted
- Mounting the phone on the dashboard or windshield for navigation is allowed with single-tap activation
- First offense carries a $20 base fine (~$150 with fees); subsequent offenses are $50 base (~$250 with fees)
- A point is NOT added to your driving record for this violation

**Recommendation:** Use hands-free technology or pull over to a safe location if you need to use your phone.

*Disclaimer: This information is for educational purposes only and does not constitute legal advice. Consult with a licensed attorney for specific legal guidance.*"""
    },
    {
        "system": "You are DriveSmart AI, a certified traffic law instructor. Provide accurate, jurisdiction-specific traffic law information with legal citations. Always include a disclaimer that this is not legal advice.",
        "instruction": "What happens if I get caught speeding 20 mph over the limit in California?",
        "response": """Speeding 20 mph over the limit in California is considered a significant violation with meaningful consequences.

**Legal Basis:** California Vehicle Code Section 22350 (Basic Speed Law) and Section 22356 (Maximum Speed Limit)

**Penalties for 20 mph Over:**
- Base fine: Approximately $100
- Total with fees/assessments: $360-$490 depending on county
- One point added to your driving record
- Point remains on record for 3 years

**Additional Consequences:**
- Insurance premium increases (typically 20-30%)
- Possible traffic school eligibility to mask the point (if no traffic school in past 18 months)
- If in a construction zone: fines are doubled
- If in a school zone: enhanced penalties apply

**Important:** If exceeding the limit by 26+ mph, you may face a 30-day license suspension under CVC 22348.

**Recommendation:** Contest the ticket if you believe you were not speeding, attend traffic school if eligible to prevent insurance increases, and maintain awareness of posted speed limits.

*Disclaimer: This information is for educational purposes only and does not constitute legal advice. Consult with a licensed attorney for specific legal guidance.*"""
    },
    # Add 100-500 more examples covering various scenarios
]


def prepare_llm_training_data(examples: List[Dict], format: str = "alpaca") -> List[Dict]:
    """
    Prepare data for LLM fine-tuning in various formats
    Formats: alpaca, sharegpt, openai
    """
    
    formatted_data = []
    
    for ex in examples:
        if format == "alpaca":
            formatted_data.append({
                "instruction": ex["instruction"],
                "input": "",
                "output": ex["response"],
                "system": ex.get("system", "")
            })
        
        elif format == "sharegpt":
            formatted_data.append({
                "conversations": [
                    {"from": "system", "value": ex.get("system", "")},
                    {"from": "human", "value": ex["instruction"]},
                    {"from": "gpt", "value": ex["response"]}
                ]
            })
        
        elif format == "openai":
            formatted_data.append({
                "messages": [
                    {"role": "system", "content": ex.get("system", "")},
                    {"role": "user", "content": ex["instruction"]},
                    {"role": "assistant", "content": ex["response"]}
                ]
            })
    
    return formatted_data


def validate_training_data(data: List[Dict]) -> Dict:
    """Validate training data quality"""
    
    issues = []
    stats = {
        "total_examples": len(data),
        "avg_response_length": 0,
        "has_citations": 0,
        "has_disclaimer": 0
    }
    
    total_length = 0
    
    for idx, ex in enumerate(data):
        response = ex.get("response", ex.get("output", ""))
        total_length += len(response)
        
        # Check for citations
        if any(term in response.lower() for term in ["section", "code", "cvc", "statute"]):
            stats["has_citations"] += 1
        else:
            issues.append(f"Example {idx}: Missing legal citation")
        
        # Check for disclaimer
        if "not legal advice" in response.lower() or "disclaimer" in response.lower():
            stats["has_disclaimer"] += 1
        else:
            issues.append(f"Example {idx}: Missing disclaimer")
        
        # Check response length
        if len(response) < 200:
            issues.append(f"Example {idx}: Response too short ({len(response)} chars)")
    
    stats["avg_response_length"] = total_length / len(data) if data else 0
    stats["citation_rate"] = stats["has_citations"] / len(data) if data else 0
    stats["disclaimer_rate"] = stats["has_disclaimer"] / len(data) if data else 0
    
    return {"stats": stats, "issues": issues[:20]}  # First 20 issues


def save_training_data():
    """Save training data in multiple formats"""
    
    # Save embedding training data
    embedding_data = prepare_embedding_training_data(RETRIEVAL_TRAINING_PAIRS)
    with open("data/embedding_training_data.json", "w") as f:
        json.dump(embedding_data, f, indent=2)
    print(f"Saved {len(RETRIEVAL_TRAINING_PAIRS)} embedding training pairs")
    
    # Save LLM training data in different formats
    for fmt in ["alpaca", "sharegpt", "openai"]:
        formatted = prepare_llm_training_data(LLM_TRAINING_DATA, format=fmt)
        with open(f"data/llm_training_{fmt}.json", "w") as f:
            json.dump(formatted, f, indent=2)
    print(f"Saved {len(LLM_TRAINING_DATA)} LLM training examples in 3 formats")
    
    # Validate
    validation = validate_training_data(LLM_TRAINING_DATA)
    print(f"\nValidation Results:")
    print(f"  Citation rate: {validation['stats']['citation_rate']:.1%}")
    print(f"  Disclaimer rate: {validation['stats']['disclaimer_rate']:.1%}")
    print(f"  Avg response length: {validation['stats']['avg_response_length']:.0f} chars")
    
    if validation["issues"]:
        print(f"\nIssues found ({len(validation['issues'])} shown):")
        for issue in validation["issues"][:5]:
            print(f"  - {issue}")


if __name__ == "__main__":
    save_training_data()
