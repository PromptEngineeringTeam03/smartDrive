import os
import chromadb
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("Testing ChromaDB Connection...")
print("-" * 50)

# Print environment variables (hide sensitive parts)
api_key = os.getenv('CHROMA_API_KEY')
tenant = os.getenv('CHROMA_TENANT')
db_name = os.getenv('CHROMA_DB')

print(f"API Key: {api_key[:10]}..." if api_key else "API Key: NOT FOUND")
print(f"Tenant: {tenant}")
print(f"Database: {db_name}")
print("-" * 50)

try:
    # Connect to ChromaDB
    client = chromadb.HttpClient(
        host="https://api.trychroma.com",
        port=443,
        ssl=True,
        headers={
            "Authorization": f"Bearer {api_key}"
        },
        tenant=tenant,
        database=db_name
    )
    
    print("✅ Connected to ChromaDB successfully!")
    
    # Get the traffic_laws collection
    collection = client.get_collection("traffic_laws")
    print(f"✅ Found 'traffic_laws' collection")
    
    # Count documents
    count = collection.count()
    print(f"✅ Collection has {count} documents")
    
    # Test a search
    print("\nTesting search for 'speed limit'...")
    results = collection.query(
        query_texts=["speed limit"],
        n_results=2
    )
    
    if results['documents'][0]:
        print(f"✅ Found {len(results['documents'][0])} results")
        print("\nFirst result preview:")
        print(results['documents'][0][0][:200] + "...")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Check your .env file has correct credentials")
    print("2. Ensure you have internet connection")
    print("3. Verify ChromaDB API key is valid")