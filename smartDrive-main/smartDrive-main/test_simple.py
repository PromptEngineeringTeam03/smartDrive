import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('CHROMA_API_KEY')
tenant = os.getenv('CHROMA_TENANT')
database = os.getenv('CHROMA_DB')

print(f"Using API Key: {api_key[:10]}...")
print(f"Tenant: {tenant}")
print(f"Database: {database}")
print("-" * 50)

# Test the API directly
url = f"https://api.trychroma.com/api/v1/tenants/{tenant}/databases/{database}/collections"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

print("Testing direct API call...")
response = requests.get(url, headers=headers)
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    print("✅ API connection successful!")
    data = response.json()
    print(f"Found {len(data)} collections")
elif response.status_code == 401:
    print("❌ Authentication failed - API key not recognized")
elif response.status_code == 403:
    print("❌ Permission denied - API key doesn't have access to this tenant/database")
elif response.status_code == 404:
    print("❌ Not found - Check tenant ID and database name")
else:
    print(f"Response: {response.text}")