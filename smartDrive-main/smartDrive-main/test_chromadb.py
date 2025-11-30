import os
import chromadb
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('CHROMA_API_KEY')
tenant = os.getenv('CHROMA_TENANT')
database = os.getenv('CHROMA_DB')

print("Testing ChromaDB with correct client...")
print("-" * 50)

try:
    # Use the ChromaDB client directly without specifying v1 endpoints
    from chromadb import HttpClient
    
    client = HttpClient(
        host="api.trychroma.com",
        port=443,
        ssl=True,
        headers={
            "Authorization": f"Bearer {api_key}",
            "X-Chroma-Token": api_key  # Try both header formats
        },
        tenant=tenant,
        database=database
    )
    
    print("✅ Client created")
    
    # List collections
    collections = client.list_collections()
    print(f"✅ Found {len(collections)} collections")
    
    for col in collections:
        print(f"  - {col.name}")
    
    # Try to get traffic_laws collection
    collection = client.get_collection("traffic_laws")
    print(f"✅ Got traffic_laws collection with {collection.count()} records")
    
except Exception as e:
    print(f"❌ Error: {e}")
    
    print("\n" + "="*50)
    print("Let's try the CloudClient instead...")
    
    try:
        from chromadb import CloudClient
        
        client = CloudClient(
            tenant=tenant,
            database=database,
            api_key=api_key
        )
        
        print("✅ CloudClient connected")
        
        # Get collection
        collection = client.get_collection("traffic_laws")
        print(f"✅ Got collection with {collection.count()} records")
        
        # Test a query
        results = collection.query(
            query_texts=["speed limit"],
            n_results=1
        )
        
        if results['documents'][0]:
            print("✅ Query successful!")
            print(f"Sample result: {results['documents'][0][0][:100]}...")
            
    except Exception as e2:
        print(f"❌ CloudClient also failed: {e2}")