import os
import warnings
import re
from google import genai
from google.genai import types
from core.actions import execute_action
from dotenv import load_dotenv
from core.shared import log, state # Import shared

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
        state.set_model("Local (Action)")
        app_name = text_lower.replace("buka ", "").strip()
        yield execute_action("open_app", app_name)
        return
        
    if text_lower.startswith("putar ") or "di youtube" in text_lower:
        state.set_model("Local (Action)")
        query = text_lower.replace("putar ", "").replace("di youtube", "").strip()
        yield execute_action("play_youtube", query)
        return
        
    if "jam berapa" in text_lower or "waktu sekarang" in text_lower:
        state.set_model("Local (Action)")
        yield execute_action("get_time")
        return
        
    if "tanggal berapa" in text_lower or "hari apa" in text_lower:
        state.set_model("Local (Action)")
        yield execute_action("get_date")
        return

    if "suara" in text_lower or "volume" in text_lower:
        state.set_model("Local (Action)")
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
        state.set_model("Local (Action)")
        yield execute_action("media_play_pause")
        return
    if any(k in text_lower for k in ["next", "selanjutnya", "lewat", "skip"]):
        state.set_model("Local (Action)")
        yield execute_action("media_next")
        return

    if "fast.com" in text_lower or ("tes" in text_lower and ("internet" in text_lower or "kecepatan" in text_lower or "speed" in text_lower)):
        state.set_model("Local (Action)")
        yield execute_action("open_app", "https://fast.com")
        return

    if "server" in text_lower:
        state.set_model("Local (Action)")
        if any(k in text_lower for k in ["cek", "check", "status", "hidup", "online"]):
            target = "2.2.2.29" if "lokal" in text_lower else "tonykumbayer.my.id"
            yield execute_action("check_server", target)
            return
        if "buka" in text_lower or "login" in text_lower or "dashboard" in text_lower or "casa" in text_lower:
            yield execute_action("open_app", "https://tonykumbayer.my.id")
            return
            
    if "casaos" in text_lower:
        state.set_model("Local (Action)")
        yield execute_action("open_app", "https://tonykumbayer.my.id")
        return
        
    # --- VISUAL ACTION ---
    # 1. Web Capture (Prioritas karena lebih spesifik)
    if any(k in text_lower for k in ["screenshot", "foto web", "tangkap layar", "capture"]):
        state.set_model("Local (Web Capture)")
        url = text_lower.replace("screenshot", "").replace("foto web", "").replace("tangkap layar", "").replace("capture", "").strip()
        yield execute_action("capture_web", url)
        return

    # 2. Image Generation
    img_keywords = ["buatkan gambar", "buat gambar", "bikin gambar", "bikinin gambar", "lukiskan", "gambarin", "generate image", "generate gambar"]
    if any(k in text_lower for k in img_keywords):
        state.set_model("Local (Image Gen)")
        prompt = text_lower
        for k in img_keywords:
            prompt = prompt.replace(k, "")
        yield execute_action("generate_image", prompt.strip())
        return

    # --- PENCARIAN INTERNET ---
    keywords_search = ["carikan", "cari ", "siapa ", "apa itu", "berapa harga", "harga ", "berita ", "lirik "]
    context_info = ""
    is_search = any(k in text_lower for k in keywords_search)
    
    if is_search:
        state.set_model("DuckDuckGo Search")
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                results = list(ddgs.text(text, max_results=3))
                if results:
                    context_info += "\nInformasi Internet:\n"
                    for r in results:
                        context_info += f"- {r['body']}\n"
        except Exception as e:
            log(f"[Brain] Gagal Search: {e}")

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

        # --- SAVE MEMORY ---
        if full_reply.strip() and not any(k in text.lower() for k in ["buka", "putar", "jam", "tanggal"]):
             state.chat_history.append({"role": "user", "content": text})
             state.chat_history.append({"role": "assistant", "content": full_reply})
             # Limit to 10 conversations (20 items)
             if len(state.chat_history) > 20: state.chat_history = state.chat_history[-20:]

    # --- AI PROVIDERS ---
    # Build history string
    history_str = ""
    if state.chat_history:
        history_str = "\n[Riwayat Percakapan Sebelumnya]:\n"
        for msg in state.chat_history:
             history_str += f"{'User' if msg['role']=='user' else 'Terry'}: {msg['content']}\n"
             
    full_prompt = f"{SYSTEM_PROMPT}\n{history_str}\n{context_info}\nUser: {text}\nTerry:"

    # 1. Gemini
    gemini_keys = [k for k in [os.getenv(f"GEMINI_API_KEY{i}") for i in ["", "_2", "_3"]] if k]
    if not gemini_keys:
        log("[Brain] Skipping Gemini: No API Keys found in .env")
    else:
        for key in gemini_keys:
            try:
                # Try a few common model names in order of stability/speed
                models_to_try = [
                    'gemini-2.0-flash', 
                    'gemini-1.5-flash', 
                    'gemini-2.0-flash-exp', 
                    'gemini-2.5-flash'
                ]
                last_err = None
                
                for model_name in models_to_try:
                    try:
                        state.set_model(f"Gemini {model_name}")
                        log(f"[Brain] Trying {model_name} (Key: ...{key[-4:]})...")
                        client = genai.Client(api_key=key)
                        response = client.models.generate_content_stream(
                            model=model_name,
                            contents=full_prompt
                        )
                        async for s in process_stream(response, is_gemini=True): yield s
                        return
                    except Exception as ge:
                        last_err = ge
                        # Handle both 404 (Not Found) and 429 (Quota Exhausted) by trying the next model
                        if any(err_code in str(ge) for err_code in ["404", "NOT_FOUND", "429", "RESOURCE_EXHAUSTED"]):
                            log(f"[Brain] {model_name} failed, trying next model version...")
                            continue 
                        raise ge # Reraise for other critical errors to try next key/provider
                
                if last_err: raise last_err
            except Exception as e: 
                log(f"[Brain] Gemini Error: {e}")
                log("[Brain] Switching to next provider...")

    # 2. Perplexity
    pplx_keys = [k for k in [os.getenv(f"PERPLEXITY_API_KEY{i}") for i in ["", "_2", "_3"]] if k]
    if pplx_keys:
        pplx_model = state.perplexity_model or "sonar"
        from openai import OpenAI
        for key in pplx_keys:
            try:
                # Fallback jika model di state adalah yang bermasalah (misal deprecated)
                if pplx_model == "sonar-reasoning":
                    pplx_model = "sonar"
                
                state.set_model(f"Perplexity ({pplx_model})")
                log(f"[Brain] Trying Perplexity ({pplx_model})...")
                client = OpenAI(api_key=key, base_url="https://api.perplexity.ai", timeout=20.0)
                stream = client.chat.completions.create(
                    model=pplx_model,
                    messages=[{"role": "user", "content": full_prompt}],
                    stream=True
                )
                async for s in process_stream(stream): yield s
                return
            except Exception as e:
                log(f"[Brain] Perplexity Error: {e}")
                if "incomplete chunked read" in str(e) or "peer closed connection" in str(e):
                    log("[Brain] Perplexity streaming failed, retrying once without streaming...")
                    try:
                        response = client.chat.completions.create(
                            model=pplx_model,
                            messages=[{"role": "user", "content": full_prompt}],
                            stream=False
                        )
                        reply = response.choices[0].message.content
                        if reply:
                            # Split non-streamed reply into sentences to maintain consistency
                            sentences = re.split(r'([.!?,]\s|\n)', reply)
                            for i in range(0, len(sentences)-1, 2):
                                s = (sentences[i] + sentences[i+1]).strip()
                                if s: yield s
                            if sentences[-1].strip(): yield sentences[-1].strip()
                            return
                    except Exception as e2:
                        log(f"[Brain] Perplexity Fallback Error: {e2}")
                
                log("[Brain] Switching to next provider...")

    # 3. DeepSeek
    ds_key = os.getenv("DEEPSEEK_API_KEY")
    if ds_key:
        from openai import OpenAI
        try:
            state.set_model("DeepSeek Chat")
            log("[Brain] Trying DeepSeek Chat...")
            client = OpenAI(api_key=ds_key, base_url="https://api.deepseek.com", timeout=20.0)
            stream = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": full_prompt}],
                stream=True
            )
            async for s in process_stream(stream): yield s
            return
        except Exception as e: 
            log(f"[Brain] DeepSeek Error: {e}")
            log("[Brain] Switching to next provider...")

    # 4. Groq
    groq_key = os.getenv("GROQ_API_KEY")
    if groq_key:
        from groq import Groq
        try:
            state.set_model("Groq (Llama 3)")
            log("[Brain] Trying Groq (Llama 3)...")
            client = Groq(api_key=groq_key)
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": full_prompt}],
                stream=True
            )
            async for s in process_stream(stream): yield s
            return
        except Exception as e: 
            log(f"[Brain] Groq Error: {e}")
            log("[Brain] Switching to next provider...")

    # 5. Ollama (Local)
    ollama_url = os.getenv("OLLAMA_BASE_URL")
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3.2")
    if ollama_url:
        from openai import OpenAI
        try:
            state.set_model(f"Ollama Local ({ollama_model})")
            log(f"[Brain] Trying Ollama Local ({ollama_model})...")
            client = OpenAI(api_key="ollama", base_url=ollama_url)
            stream = client.chat.completions.create(
                model=ollama_model,
                messages=[{"role": "user", "content": full_prompt}],
                stream=True
            )
            async for s in process_stream(stream): yield s
            return
        except Exception as e: 
            log(f"[Brain] Ollama Error: {e}")
            log("[Brain] Switching to next provider...")

    # 6. Fallback
    state.set_model("System Fallback (Google)")
    log("[Brain] All AI providers failed. Using Google Search fallback.")
    import webbrowser
    webbrowser.open(f"https://www.google.com/search?q={text}")
    yield "Maaf, semua AI sedang sibuk. Saya bukakan Google ya."
