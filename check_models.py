import os
import google.genai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    print("API Key not found in .env")
    exit()

print("Checking available models...")
try:
    client = genai.Client(api_key=API_KEY)
    models = client.models.list()
    for m in models:
        print(f"- {m.name}")
except Exception as e:
    print(f"Error: {e}")
