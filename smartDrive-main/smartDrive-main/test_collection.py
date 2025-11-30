# test_collection.py
import chromadb
from chromadb import HttpClient
import os
from dotenv import load_dotenv

load_dotenv()

client = HttpClient(
    host="api.trychroma.com",
    port=443,
    ssl=True,
    headers={
        "Authorization": f"Bearer {os.getenv('CHROMA_API_KEY')}",
        "X-Chroma-Token": os.getenv('CHROMA_API_KEY')
    },
    tenant=os.getenv('CHROMA_TENANT'),
    database=os.getenv('CHROMA_DB')
)

collection = client.get_collection("traffic_laws")

# Get a few documents without using embeddings
peek = collection.peek(5)  # Get first 5 documents
print("Sample documents in collection:")
for i, (doc, meta) in enumerate(zip(peek['documents'], peek['metadatas'])):
    print(f"\n{i+1}. {meta}")
    print(f"   Document: {doc[:200]}...")