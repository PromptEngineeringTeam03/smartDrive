from SmartDrive.src.vector_store import CloudTrafficLawVectorStore

vsm = CloudTrafficLawVectorStore()
vs = vsm.get_existing_vectorstore("traffic_laws")

docs = vs.similarity_search("New York pedestrian crosswalk right of way", k=5)

for d in docs:
    print(d.metadata.get("jurisdiction"), d.metadata.get("statute"))