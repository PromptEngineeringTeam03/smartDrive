import json
import pandas as pd

# Comprehensive Traffic Law Dataset for DriveSmart AI
traffic_laws_data = [
    {
        "id": "TL001",
        "jurisdiction": "Massachusetts",
        "category": "Speed Limits",
        "violation": "Speeding in residential area",
        "law_text": "No person shall operate a motor vehicle at a speed exceeding 30 miles per hour in a thickly settled or business district, except as otherwise provided by local ordinance.",
        "statute": "M.G.L. c. 90, § 17",
        "penalty": "$100-$300 fine, 2-4 points",
        "severity": "moderate",
        "preventive_tip": "Always observe posted speed limit signs and reduce speed in residential areas",
        "keywords": ["speeding", "residential", "speed limit", "mph"]
    },
    {
        "id": "TL002",
        "jurisdiction": "Massachusetts",
        "category": "Phone Use",
        "violation": "Using handheld device while driving",
        "law_text": "No operator of a motor vehicle shall use a mobile electronic device while operating such vehicle, including while temporarily stationary due to traffic, a traffic control device, or other momentary delays.",
        "statute": "M.G.L. c. 90, § 13B",
        "penalty": "First offense: $100, Second offense: $250, Third offense: $500 + insurance surcharge",
        "severity": "high",
        "preventive_tip": "Use hands-free devices or pull over safely to use your phone",
        "keywords": ["phone", "mobile device", "texting", "distracted driving", "red light"]
    },
    {
        "id": "TL003",
        "jurisdiction": "Massachusetts",
        "category": "DUI/DWI",
        "violation": "Operating under the influence",
        "law_text": "Whoever operates a motor vehicle while under the influence of intoxicating liquor, or of marijuana, narcotic drugs, depressants or stimulant substances shall be punished.",
        "statute": "M.G.L. c. 90, § 24",
        "penalty": "First offense: Up to 2.5 years jail, $500-$5000 fine, 1-year license suspension",
        "severity": "critical",
        "preventive_tip": "Never drive after consuming alcohol or drugs; use designated driver or rideshare services",
        "keywords": ["DUI", "DWI", "drunk driving", "alcohol", "intoxicated"]
    },
    {
        "id": "TL004",
        "jurisdiction": "Massachusetts",
        "category": "Traffic Signals",
        "violation": "Running a red light",
        "law_text": "The driver of any vehicle shall obey the instructions of any official traffic control signal applicable thereto placed in accordance with law, unless otherwise directed by a police officer.",
        "statute": "M.G.L. c. 89, § 9",
        "penalty": "$150 fine, 3 points",
        "severity": "high",
        "preventive_tip": "Always come to a complete stop at red lights and proceed only when green",
        "keywords": ["red light", "traffic signal", "stop", "intersection"]
    },
    {
        "id": "TL005",
        "jurisdiction": "Massachusetts",
        "category": "Parking",
        "violation": "Parking in handicapped space without permit",
        "law_text": "No person shall park in a space designated for handicapped persons unless displaying a valid handicapped parking placard or license plate.",
        "statute": "M.G.L. c. 90, § 20A",
        "penalty": "$300-$500 fine",
        "severity": "moderate",
        "preventive_tip": "Only park in handicapped spaces if you have a valid permit displayed",
        "keywords": ["handicapped parking", "disabled parking", "parking violation", "permit"]
    },
    {
        "id": "TL006",
        "jurisdiction": "California",
        "category": "Speed Limits",
        "violation": "Excessive speeding on highway",
        "law_text": "No person shall drive a vehicle upon a highway at a speed greater than is reasonable or prudent having due regard for weather, visibility, traffic, and surface conditions.",
        "statute": "California Vehicle Code § 22350",
        "penalty": "$238+ fine, 1-2 points depending on speed",
        "severity": "high",
        "preventive_tip": "Maintain safe speeds appropriate for road and weather conditions",
        "keywords": ["speeding", "highway", "excessive speed", "reckless driving"]
    },
    {
        "id": "TL007",
        "jurisdiction": "California",
        "category": "Seat Belts",
        "violation": "Failure to wear seat belt",
        "law_text": "A person shall not operate a motor vehicle on a highway unless that person and all passengers 16 years of age or over are properly restrained by a safety belt.",
        "statute": "California Vehicle Code § 27315",
        "penalty": "$162 fine (first offense)",
        "severity": "low",
        "preventive_tip": "Always buckle up before starting your vehicle",
        "keywords": ["seat belt", "safety belt", "restraint", "passenger safety"]
    },
    {
        "id": "TL008",
        "jurisdiction": "New York",
        "category": "Right of Way",
        "violation": "Failure to yield to pedestrian in crosswalk",
        "law_text": "Every driver of a vehicle shall yield the right of way to a pedestrian crossing the roadway within any marked crosswalk or within any unmarked crosswalk at an intersection.",
        "statute": "NY VTL § 1151",
        "penalty": "$50-$300 fine, 3 points, possible license suspension",
        "severity": "high",
        "preventive_tip": "Always stop for pedestrians in crosswalks and watch for crossing pedestrians at intersections",
        "keywords": ["pedestrian", "crosswalk", "right of way", "yield"]
    },
    {
        "id": "TL009",
        "jurisdiction": "Texas",
        "category": "School Zones",
        "violation": "Speeding in school zone",
        "law_text": "A person may not operate a vehicle in a school crossing zone at a speed of more than 15 miles per hour during the times designated by the sign.",
        "statute": "Texas Transportation Code § 545.357",
        "penalty": "$200-$400 fine, doubled in school zone",
        "severity": "high",
        "preventive_tip": "Slow down to posted school zone speed limits during active hours",
        "keywords": ["school zone", "speeding", "children", "reduced speed"]
    },
    {
        "id": "TL010",
        "jurisdiction": "Florida",
        "category": "Reckless Driving",
        "violation": "Reckless driving",
        "law_text": "Any person who drives any vehicle in willful or wanton disregard for the safety of persons or property is guilty of reckless driving.",
        "statute": "Florida Statutes § 316.192",
        "penalty": "Up to 90 days jail, $500 fine, 4 points",
        "severity": "critical",
        "preventive_tip": "Always drive with care and consideration for others on the road",
        "keywords": ["reckless driving", "dangerous driving", "willful disregard", "safety"]
    },
    {
        "id": "TL011",
        "jurisdiction": "Massachusetts",
        "category": "Commercial Vehicles",
        "violation": "Commercial truck parking violation",
        "law_text": "Commercial vehicles over 10,000 pounds may not park on residential streets between 11 PM and 6 AM without permit.",
        "statute": "M.G.L. c. 90, § 18",
        "penalty": "$100 fine, possible towing",
        "severity": "low",
        "preventive_tip": "Park commercial vehicles in designated areas or obtain proper permits",
        "keywords": ["commercial vehicle", "truck", "parking", "residential"]
    },
    {
        "id": "TL012",
        "jurisdiction": "Massachusetts",
        "category": "License Requirements",
        "violation": "Operating without valid license",
        "law_text": "No person shall operate a motor vehicle on any way unless such person has a license or permit to operate such vehicle issued by the registrar.",
        "statute": "M.G.L. c. 90, § 10",
        "penalty": "$500-$1,000 fine, possible jail time",
        "severity": "critical",
        "preventive_tip": "Always maintain a valid driver's license and carry it while driving",
        "keywords": ["license", "permit", "suspended license", "unlicensed"]
    }
]

# Create DataFrame
df = pd.DataFrame(traffic_laws_data)

# Save to CSV
df.to_csv('traffic_laws_dataset.csv', index=False)

# Save to JSON for ChromaDB
with open('traffic_laws_dataset.json', 'w') as f:
    json.dump(traffic_laws_data, f, indent=2)

print("Dataset created successfully!")
print(f"\nDataset Statistics:")
print(f"Total records: {len(traffic_laws_data)}")
print(f"Jurisdictions: {df['jurisdiction'].nunique()}")
print(f"Categories: {df['category'].unique()}")
print("\nSample record:")
print(json.dumps(traffic_laws_data[0], indent=2))