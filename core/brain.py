import os
import google.generativeai as genai
from core.actions import execute_action
from dotenv import load_dotenv

load_dotenv()

# Konfigurasi API
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("WARNING: GEMINI_API_KEY belum diset di .env")

# System Prompt
SYSTEM_PROMPT = """
Kamu adalah Terry, asisten AI yang cerdas, ramah, dan membantu.
Kamu berjalan di Windows 11.
Gaya bicaramu santai tapi sopan, seperti Jarvis tapi versi wanita yang ramah.
Jawablah dengan ringkas dan jelas.
Jika pengguna meminta melakukan sesuatu pada komputer (buka aplikasi, cek cuaca), 
kamu harus mendeteksi niat tersebut.
"""

async def process(text: str) -> str:
    """Memproses teks input secara sederhana."""
    # --- OTAK LOKAL (Hemat Kuota & Cepat) ---
    # Kita cek dulu apakah perintah bisa diproses tanpa AI
    text_lower = text.lower()
    
    # 1. Buka Aplikasi
    if text_lower.startswith("buka "):
        app_name = text_lower.replace("buka ", "").strip()
        return execute_action("open_app", app_name)
        
    # 2. YouTube / Putar Lagu
    if text_lower.startswith("putar ") or "di youtube" in text_lower:
        query = text_lower.replace("putar ", "").replace("di youtube", "").strip()
        return execute_action("play_youtube", query)
        
    # 3. Waktu / Jam
    if "jam berapa" in text_lower or "waktu sekarang" in text_lower:
        return execute_action("get_time")
        
    # 4. Tanggal
    if "tanggal berapa" in text_lower or "hari apa" in text_lower:
        return execute_action("get_date")
        
    # 5. MODE PENCARI (Search Engine - Hemat Kuota)
    # Menangkap pertanyaan fakta: "Carikan", "Siapa", "Apa itu", "Harga"
    keywords_search = ["carikan", "cari ", "siapa ", "apa itu", "berapa harga", "harga ", "berita "]
    if any(k in text_lower for k in keywords_search):
        try:
            from duckduckgo_search import DDGS
            print(f"[Brain] Mode Pencari: {text}")
            with DDGS() as ddgs:
                results = list(ddgs.text(text, max_results=1))
                if results:
                    best_result = results[0]
                    # Ambil judul dan isi ringkas
                    answer = f"Menurut info yang saya dapat: {best_result['body']}"
                    # Return jawaban langsung
                    return answer
        except Exception as e:
            print(f"[Brain] Gagal Search: {e}")
            # Lanjut ke AI jika search error (fallback)

    # --- OTAK AI (Gemini Multi-Model Fallback) ---
    if not API_KEY:
        return "Atur API Key Anda di file .env."

    # Daftar model untuk rotasi jika limit habis (Expanded List)
    BACKUP_MODELS = [
        'gemini-2.0-flash',             # Utama
        'gemini-2.0-flash-lite',        # Lite Stable
        'gemini-2.0-flash-lite-001',    # Lite Versioned
        'gemini-2.0-flash-exp',         # Experimental
        'gemini-exp-1206',              # Experimental Dec
        'gemini-2.5-flash',             # Terbaru (Sering limit, tapi coba)
        'gemini-2.0-flash-001',         # Stable Versioned
        'gemini-2.0-flash-lite-preview-02-05',
    ]

    last_error = ""

    for model_name in BACKUP_MODELS:
        try:
            # print(f"[Brain] Mencoba: {model_name}...") 
            model = genai.GenerativeModel(model_name)
            
            prompt = f"""
{SYSTEM_PROMPT}
Jika pengguna minta pengingat, balas: [ACTION:REMIND] detik|pesan
Lainnya balas percakapan biasa yang ramah.

User: {text}
Terry:
"""
            response = model.generate_content(prompt)
            reply = response.text.strip()

            if "[ACTION:REMIND]" in reply:
                try:
                    p = reply.replace("[ACTION:REMIND]", "").strip()
                    sec, msg = p.split("|")
                    return execute_action("set_reminder", {"seconds": int(sec), "message": msg})
                except: pass
            
            return reply

        except Exception as e:
            error_msg = str(e)
            last_error = error_msg
            if "429" in error_msg or "404" in error_msg:
                # print(f"[Brain] Skip {model_name}...")
                continue 
            else:
                print(f"[Brain] Error Kritikal: {e}")
                break

    # --- OTAK AI (GROQ - Llama 3 Fast Backup) ---
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    if GROQ_API_KEY and ("429" in last_error or "404" in last_error):
        try:
            from groq import Groq
            print(f"[Brain] Mengalihkan ke Groq (Llama 3)...")
            client = Groq(api_key=GROQ_API_KEY)
            
            chat_completion = client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT + "\nJika minta pengingat, balas: [ACTION:REMIND] detik|pesan\nJika minta buka aplikasi/website, balas: [ACTION:OPEN_APP] nama_aplikasi\nJika minta putar youtube, balas: [ACTION:YOUTUBE] query"
                    },
                    {
                        "role": "user",
                        "content": text,
                    }
                ],
                model="llama-3.3-70b-versatile",
            )
            
            reply = chat_completion.choices[0].message.content
            
            # Parsing Actions untuk Groq
            if "[ACTION:REMIND]" in reply:
                try:
                    p = reply.replace("[ACTION:REMIND]", "").strip()
                    sec, msg = p.split("|")
                    return execute_action("set_reminder", {"seconds": int(sec), "message": msg})
                except: pass
            
            elif "[ACTION:OPEN_APP]" in reply:
                app = reply.replace("[ACTION:OPEN_APP]", "").strip()
                return execute_action("open_app", app)
                
            elif "[ACTION:YOUTUBE]" in reply:
                query = reply.replace("[ACTION:YOUTUBE]", "").strip()
                return execute_action("play_youtube", query)
            
            return reply
            
        except Exception as e:
            print(f"[Brain] Groq Error: {e}")

    # Jika semua model gagal (Fallback Terakhir: Google Search)
    print(f"[Brain] Semua AI Menyerah. Fallback ke Google.")
    
    # Import di sini untuk menghindari circular import jika ada, atau pastikan import os/webbrowser ada
    import webbrowser
    webbrowser.open(f"https://www.google.com/search?q={text}")
    
    return "Maaf, kuota AI saya habis total. Saya bukakan Google untuk Anda."
