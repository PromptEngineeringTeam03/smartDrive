from dotenv import load_dotenv
import os
from pathlib import Path

env_path=Path(__file__).parent.parent/'smartdrive'/'src'/'.env'
load_dotenv(env_path)
print(f"OPENAI_API_KEY from env: {os.getenv('OPENAI_API_KEY')}")
print(f"Length: {len(os.getenv('OPENAI_API_KEY') or '')}")