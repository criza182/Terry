import requests
import os
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def get_free_models():
    if not OPENROUTER_API_KEY:
        print("Please set OPENROUTER_API_KEY in .env first.")
        # For testing purposes without the key in .env yet, we might fail or need to ask user.
        # But I recall user just asked to add it, so they probably haven't added the key yet?
        # OR maybe I should just implement the logic assuming the key will be there.
        # Actually, I can check the public models endpoint without an API key? 
        # OpenRouter docs say "Fetch a list of available models". Usually requires no auth or auth.
        pass

    try:
        response = requests.get("https://openrouter.ai/api/v1/models")
        if response.status_code == 200:
            models = response.json().get("data", [])
            free_models = []
            for m in models:
                pricing = m.get("pricing", {})
                prompt_price = pricing.get("prompt")
                completion_price = pricing.get("completion")
                
                # Check if price is 0 or "0"
                if (str(prompt_price) == "0" or prompt_price == 0) and \
                   (str(completion_price) == "0" or completion_price == 0):
                    free_models.append(m['id'])
            
            return free_models
        else:
            print(f"Error: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Exception: {e}")
        return []

if __name__ == "__main__":
    free_models = get_free_models()
    print(f"Found {len(free_models)} free models:")
    for m in free_models:
        print(f"- {m}")
