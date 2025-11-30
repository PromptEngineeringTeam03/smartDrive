"""
DriveSmart AI - Fine-Tuning Script (Self-Contained)
This version includes the training data directly - no separate file needed
"""

import json
import os
from pathlib import Path

# =============================================================================
# TRAINING DATA (embedded directly in script)
# =============================================================================

RETRIEVAL_TRAINING_PAIRS = [
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
    {
        "query": "What is the speed limit in a school zone?",
        "positive": "California Vehicle Code Section 22352 establishes a prima facie speed limit of 25 mph when passing school buildings or grounds during school hours when children are present. Some zones may have lower posted limits of 15 mph.",
        "hard_negative": "School buses must stop at railroad crossings and open doors to listen for approaching trains before proceeding."
    },
    {
        "query": "Can I turn right on a red light?",
        "positive": "California Vehicle Code Section 21453 permits right turns on red after coming to a complete stop, unless a sign prohibits the turn. Drivers must yield to pedestrians and cross traffic before proceeding.",
        "hard_negative": "Traffic signals are typically timed to optimize traffic flow during peak hours and reduce congestion at major intersections."
    },
    {
        "query": "What is the legal blood alcohol limit for driving?",
        "positive": "California Vehicle Code Section 23152 establishes that it is unlawful to drive with a blood alcohol concentration (BAC) of 0.08% or higher. For commercial drivers, the limit is 0.04%, and for drivers under 21, any detectable alcohol (0.01%) is prohibited.",
        "hard_negative": "Alcoholic beverages must be sold by licensed establishments that comply with state alcohol control regulations."
    },
    {
        "query": "Do I need to wear a seatbelt in California?",
        "positive": "California Vehicle Code Section 27315 requires all drivers and passengers to wear seatbelts. Children under 8 must be secured in a car seat or booster seat in the back seat. Violation carries a base fine of $20 for first offense.",
        "hard_negative": "Vehicle manufacturers must ensure all seatbelts meet federal motor vehicle safety standards before installation."
    },
    {
        "query": "What are the rules for passing a school bus?",
        "positive": "California Vehicle Code Section 22454 prohibits passing a school bus when its red lights are flashing and stop sign is extended. Drivers in both directions must stop unless separated by a divided highway. Violations can result in fines up to $1,000.",
        "hard_negative": "School bus drivers must complete specialized training and obtain a commercial license with passenger endorsement."
    },
    {
        "query": "How close can I park to a fire hydrant?",
        "positive": "California Vehicle Code Section 22514 prohibits parking within 15 feet of a fire hydrant. Violations can result in a citation of approximately $80 plus fees, and the vehicle may be towed if blocking emergency access.",
        "hard_negative": "Fire hydrants must be inspected annually by the local fire department to ensure proper water pressure and functionality."
    },
    {
        "query": "What is the penalty for running a red light?",
        "positive": "Running a red light in California (CVC 21453) carries a base fine of $100, but with assessments and fees, the total typically ranges from $480-$500. One point is added to your driving record, and red light camera violations carry the same penalties.",
        "hard_negative": "Traffic light timing is determined by traffic engineers based on intersection geometry and traffic volume studies."
    },
    {
        "query": "Can I drive with headphones on?",
        "positive": "California Vehicle Code Section 27400 prohibits wearing headphones, earbuds, or earplugs in both ears while driving. A single earbud in one ear is permitted. Violation is an infraction with a base fine of approximately $197.",
        "hard_negative": "Audio equipment installed in vehicles must meet federal standards for electromagnetic interference."
    },
    {
        "query": "What are the bicycle lane rules for drivers?",
        "positive": "California Vehicle Code Section 21209 prohibits driving in a bicycle lane except when making a right turn, entering or leaving the roadway, or parking where permitted. Drivers must yield to bicyclists when crossing the bike lane.",
        "hard_negative": "Bicycle lanes must be marked with specific paint colors and symbols as defined by the Manual on Uniform Traffic Control Devices."
    },
    {
        "query": "How long do points stay on my driving record?",
        "positive": "In California, most traffic violation points remain on your driving record for 3 years from the violation date. More serious violations like DUI or hit-and-run stay for 10 years. Points are used by the DMV and insurance companies differently.",
        "hard_negative": "Driving records are maintained by the Department of Motor Vehicles and can be requested for a fee."
    },
]


def prepare_training_data():
    """Prepare and save training data"""
    
    training_data = {
        "queries": {},
        "corpus": {},
        "relevant_docs": {}
    }
    
    for idx, pair in enumerate(RETRIEVAL_TRAINING_PAIRS):
        query_id = f"q{idx}"
        pos_id = f"pos{idx}"
        neg_id = f"neg{idx}"
        
        training_data["queries"][query_id] = pair["query"]
        training_data["corpus"][pos_id] = pair["positive"]
        training_data["corpus"][neg_id] = pair["hard_negative"]
        training_data["relevant_docs"][query_id] = [pos_id]
    
    # Create data directory if it doesn't exist
    Path("data").mkdir(exist_ok=True)
    
    # Save to file
    with open("data/embedding_training_data.json", "w") as f:
        json.dump(training_data, f, indent=2)
    
    print(f"✓ Created training data with {len(RETRIEVAL_TRAINING_PAIRS)} examples")
    return training_data


def fine_tune_embeddings():
    """Fine-tune sentence-transformers for better traffic law retrieval"""
    
    from sentence_transformers import SentenceTransformer, InputExample, losses
    from torch.utils.data import DataLoader
    
    print("=" * 60)
    print("EMBEDDING MODEL FINE-TUNING")
    print("=" * 60)
    
    # Check if data exists, create if not
    data_path = "data/embedding_training_data.json"
    if not os.path.exists(data_path):
        print("\n⚠ Training data not found. Creating it now...")
        prepare_training_data()
    
    # Load training data
    with open(data_path, "r") as f:
        data = json.load(f)
    
    # Create training examples
    train_examples = []
    for query_id, query in data["queries"].items():
        pos_id = data["relevant_docs"][query_id][0]
        positive = data["corpus"][pos_id]
        train_examples.append(InputExample(texts=[query, positive]))
    
    print(f"✓ Loaded {len(train_examples)} training examples")
    
    # Load base model
    model_name = "sentence-transformers/all-MiniLM-L6-v2"
    print(f"✓ Loading base model: {model_name}")
    model = SentenceTransformer(model_name)
    
    # Create dataloader
    train_dataloader = DataLoader(train_examples, shuffle=True, batch_size=8)
    
    # Loss function
    train_loss = losses.MultipleNegativesRankingLoss(model)
    
    # Training config
    num_epochs = 3
    warmup_steps = int(len(train_dataloader) * num_epochs * 0.1)
    output_path = "models/drivesmart-embeddings"
    
    print(f"\nTraining Configuration:")
    print(f"  • Epochs: {num_epochs}")
    print(f"  • Batch size: 8")
    print(f"  • Warmup steps: {warmup_steps}")
    print(f"  • Output: {output_path}")
    
    # Create output directory
    Path("models").mkdir(exist_ok=True)
    
    # Fine-tune
    print("\n🚀 Starting fine-tuning...")
    model.fit(
        train_objectives=[(train_dataloader, train_loss)],
        epochs=num_epochs,
        warmup_steps=warmup_steps,
        output_path=output_path,
        show_progress_bar=True
    )
    
    print(f"\n✅ Fine-tuning complete!")
    print(f"   Model saved to: {output_path}")
    
    return model


def test_model():
    """Quick test of the fine-tuned model"""
    from sentence_transformers import SentenceTransformer
    import numpy as np
    
    print("\n" + "=" * 60)
    print("TESTING FINE-TUNED MODEL")
    print("=" * 60)
    
    # Load models
    baseline = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    
    finetuned_path = "models/drivesmart-embeddings"
    if os.path.exists(finetuned_path):
        finetuned = SentenceTransformer(finetuned_path)
    else:
        print("⚠ Fine-tuned model not found. Run fine-tuning first.")
        return
    
    # Test case
    query = "Can I use my phone while stopped at a traffic light?"
    relevant = "CVC 23123.5 prohibits handheld phone use while driving, including at red lights."
    irrelevant = "Traffic lights use red, yellow, and green to control intersection traffic flow."
    
    print(f"\nTest Query: {query}")
    print(f"Relevant: {relevant[:60]}...")
    print(f"Irrelevant: {irrelevant[:60]}...")
    
    for name, model in [("Baseline", baseline), ("Fine-tuned", finetuned)]:
        q_emb = model.encode(query)
        r_emb = model.encode(relevant)
        i_emb = model.encode(irrelevant)
        
        rel_score = np.dot(q_emb, r_emb) / (np.linalg.norm(q_emb) * np.linalg.norm(r_emb))
        irr_score = np.dot(q_emb, i_emb) / (np.linalg.norm(q_emb) * np.linalg.norm(i_emb))
        
        correct = "✅" if rel_score > irr_score else "❌"
        print(f"\n{name}:")
        print(f"  Relevant similarity: {rel_score:.4f}")
        print(f"  Irrelevant similarity: {irr_score:.4f}")
        print(f"  Correct ranking: {correct}")


if __name__ == "__main__":
    # Step 1: Prepare data (creates file if missing)
    prepare_training_data()
    
    # Step 2: Fine-tune
    fine_tune_embeddings()
    
    # Step 3: Test
    test_model()
