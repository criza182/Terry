from core.brain import process
import os
import asyncio

# Mock environment if needed, or ensure .env is loaded
from dotenv import load_dotenv
load_dotenv()

# We want to force OpenRouter. 
# Temporary hack: Remove other keys from env in python memory or ensure we can hit OpenRouter.
# But brain.py checks env vars.
# Let's just run it and see logs. 
# Or better, set other keys to None temporarily.

async def test():
    # Clear other keys to force fallback to OpenRouter (since it's #5 in the list)
    # But wait, we want to test if it WORKS when selected.
    # The order is Gemini -> Perplexity -> DeepSeek -> Groq -> OpenRouter -> Ollama
    
    # Let's temporarily unset other keys for this process
    # Bersihkan semua key lain untuk memaksa fallback ke OpenRouter
    for key in list(os.environ.keys()):
        if any(prefix in key for prefix in ["GEMINI", "PERPLEXITY", "DEEPSEEK", "GROQ", "OLLAMA"]):
            os.environ[key] = ""
    
    # Ensure OpenRouter key is set (User might not have set it yet, so we expect failure or skip)
    if not os.getenv("OPENROUTER_API_KEY"):
        print("WARNING: OPENROUTER_API_KEY is not set in .env. Test checks logic only.")
        # We can set a dummy key to verify it TRIES to call OpenRouter
        os.environ["OPENROUTER_API_KEY"] = "sk-or-dummy-key"
    
    print("Testing OpenRouter integration...")
    print(f"OpenRouter Key Present: {bool(os.environ.get('OPENROUTER_API_KEY'))}")
    
    async for chunk in process("Halo, ceritakan sedikit tentang OpenRouter"):
        print(chunk, end="", flush=True)
    print("\nTest finished.")

if __name__ == "__main__":
    asyncio.run(test())
