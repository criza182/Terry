import os
import warnings
import re
import google.generativeai as genai
from core.actions import execute_action
from dotenv import load_dotenv

# Suppress the google.generativeai deprecation warning
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")

load_dotenv()

# System Prompt
SYSTEM_PROMPT = """
Kamu adalah Terry, asisten AI cerdas untuk Windows 11. 
Gaya bicara: Santai, ramah, dan sangat singkat (Direct & Concise).
JANGAN mengulang kata pemicu atau nama "Terry" di awal jawaban.
Hanya bicara panjang jika diminta (Writer Mode).
"""

async def process(text: str):
    """Memproses teks input dan menghasilkan aliran respon (streaming)."""
    text_lower = text.lower()
    
    # --- OTAK LOKAL (Hemat Kuota & Cepat) ---
    if text_lower.startswith("buka "):
        app_name = text_lower.replace("buka ", "").strip()
        yield execute_action("open_app", app_name)
        return
        
    if text_lower.startswith("putar ") or "di youtube" in text_lower:
        query = text_lower.replace("putar ", "").replace("di youtube", "").strip()
        yield execute_action("play_youtube", query)
        return
        
    if "jam berapa" in text_lower or "waktu sekarang" in text_lower:
        yield execute_action("get_time")
        return
        
    if "tanggal berapa" in text_lower or "hari apa" in text_lower:
        yield execute_action("get_date")
        return

    if "suara" in text_lower or "volume" in text_lower:
        if any(k in text_lower for k in ["besar", "naik", "tambah", "keras", "up"]):
            yield execute_action("volume_up")
            return
        if any(k in text_lower for k in ["kecil", "turun", "kurang", "pelan", "down"]): 
            yield execute_action("volume_down")
            return
        if any(k in text_lower for k in ["mute", "diam", "mati"]):
            yield execute_action("volume_mute")
            return

    if any(k in text_lower for k in ["pause", "jeda", "stop", "berhenti", "resume", "lanjut", "mainkan lagi"]):
        yield execute_action("media_play_pause")
        return
    if any(k in text_lower for k in ["next", "selanjutnya", "lewat", "skip"]):
        yield execute_action("media_next")
        return

    if "fast.com" in text_lower or ("tes" in text_lower and ("internet" in text_lower or "kecepatan" in text_lower or "speed" in text_lower)):
        yield execute_action("open_app", "https://fast.com")
        return

    if "server" in text_lower:
        if any(k in text_lower for k in ["cek", "check", "status", "hidup", "online"]):
            target = "2.2.2.29" if "lokal" in text_lower else "tonykumbayer.my.id"
            yield execute_action("check_server", target)
            return
        if "buka" in text_lower or "login" in text_lower or "dashboard" in text_lower or "casa" in text_lower:
            yield execute_action("open_app", "https://tonykumbayer.my.id")
            return
            
    if "casaos" in text_lower:
        yield execute_action("open_app", "https://tonykumbayer.my.id")
        return

    # --- PENCARIAN INTERNET ---
    keywords_search = ["carikan", "cari ", "siapa ", "apa itu", "berapa harga", "harga ", "berita ", "lirik "]
    context_info = ""
    is_search = any(k in text_lower for k in keywords_search)
    
    if is_search:
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(text, max_results=3))
                if results:
                    context_info += "\nInformasi Internet:\n"
                    for r in results:
                        context_info += f"- {r['body']}\n"
        except Exception as e:
            print(f"[Brain] Gagal Search: {e}")

    # --- HELPER: Sentence Splitter & Action Parser ---
    async def process_stream(stream_gen, is_gemini=False):
        full_reply = ""
        buffer = ""
        
        for chunk in stream_gen:
            content = ""
            if is_gemini:
                try: content = chunk.text
                except: pass
            else:
                try: content = chunk.choices[0].delta.content or ""
                except: pass
            
            if not content: continue
            
            full_reply += content
            buffer += content
            
            # Split by punctuation
            if any(p in buffer for p in [". ", "! ", "? ", "\n"]):
                parts = re.split(r'([.!?,]\s|\n)', buffer)
                for i in range(0, len(parts)-1, 2):
                    sentence = (parts[i] + parts[i+1]).strip()
                    if sentence and "[ACTION:" not in sentence:
                        yield sentence
                buffer = parts[-1]

        # Yield remaining buffer
        if buffer.strip() and "[ACTION:" not in buffer:
            yield buffer.strip()
        
        # Parse Actions
        for action_tag in ["REMIND", "WRITE_FILE", "OPEN_APP"]:
            match = re.search(fr"\[ACTION:{action_tag}\]\s*(.*)", full_reply)
            if match:
                payload = match.group(1).strip()
                if action_tag == "REMIND":
                    try:
                        sec, msg = payload.split("|")
                        yield execute_action("set_reminder", {"seconds": int(sec), "message": msg})
                    except: pass
                elif action_tag == "WRITE_FILE":
                    yield execute_action("write_file", payload)
                elif action_tag == "OPEN_APP":
                    yield execute_action("open_app", payload)

    # --- AI PROVIDERS ---
    prompt = f"{SYSTEM_PROMPT}\n\n{context_info}\n\nUser: {text}\nTerry:"

    # 1. Gemini
    gemini_keys = [k for k in [os.getenv(f"GEMINI_API_KEY{i}") for i in ["", "_2", "_3"]] if k]
    for key in gemini_keys:
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            response = model.generate_content(prompt, stream=True)
            async for s in process_stream(response, is_gemini=True): yield s
            return
        except Exception as e: print(f"Gemini Error: {e}")

    # 2. Perplexity
    pplx_keys = [k for k in [os.getenv(f"PERPLEXITY_API_KEY{i}") for i in ["", "_2", "_3"]] if k]
    if pplx_keys:
        from openai import OpenAI
        for key in pplx_keys:
            try:
                client = OpenAI(api_key=key, base_url="https://api.perplexity.ai")
                stream = client.chat.completions.create(
                    model="sonar",
                    messages=[{"role": "user", "content": prompt}],
                    stream=True
                )
                async for s in process_stream(stream): yield s
                return
            except Exception as e: print(f"Perplexity Error: {e}")

    # 3. DeepSeek
    ds_key = os.getenv("DEEPSEEK_API_KEY")
    if ds_key:
        from openai import OpenAI
        try:
            client = OpenAI(api_key=ds_key, base_url="https://api.deepseek.com")
            stream = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            async for s in process_stream(stream): yield s
            return
        except Exception as e: print(f"DeepSeek Error: {e}")

    # 4. Groq
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        from groq import Groq
        try:
            client = Groq(api_key=groq_key)
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                stream=True
            )
            async for s in process_stream(stream): yield s
            return
        except Exception as e: print(f"Groq Error: {e}")

    # 5. Fallback
    import webbrowser
    webbrowser.open(f"https://www.google.com/search?q={text}")
    yield "Maaf, semua AI sedang sibuk. Saya bukakan Google ya."
