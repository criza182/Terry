import os
from dotenv import load_dotenv

# Try to load .env
loaded = load_dotenv()
print(f".env loaded successfully: {loaded}")

# Print Gemini API Key (masked)
gemini_key = os.getenv("GEMINI_API_KEY")
if gemini_key:
    # Check for BOM or weird characters
    print(f"GEMINI_API_KEY found: ...{gemini_key[-4:]}")
    print(f"Key length: {len(gemini_key)}")
    print(f"Key starts with: {repr(gemini_key[:5])}")
else:
    print("GEMINI_API_KEY NOT found in environment.")

# Check for other possible names
print("Checking for other variations:")
for key in os.environ:
    if "GEMINI" in key:
        print(f"Found: {key}")

# Check first line of .env manually if possible
try:
    with open(".env", "rb") as f:
        first_line = f.readline()
        print(f"First line (raw): {first_line}")
except Exception as e:
    print(f"Could not read .env raw: {e}")
