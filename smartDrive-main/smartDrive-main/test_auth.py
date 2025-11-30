import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('CHROMA_API_KEY')
print(f"API Key length: {len(api_key) if api_key else 0}")
print(f"API Key starts with: {api_key[:3] if api_key else 'None'}")
print(f"API Key ends with: {api_key[-4:] if api_key else 'None'}")

# Check for common issues
if api_key:
    if ' ' in api_key:
        print("⚠️ WARNING: API key contains spaces")
    if '\n' in api_key:
        print("⚠️ WARNING: API key contains newlines")
    if api_key.startswith('"') or api_key.endswith('"'):
        print("⚠️ WARNING: API key has quotes")