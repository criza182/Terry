import asyncio
import threading
import uvicorn
import schedule
from core.voice import listen, speak
from core.brain import process
from web.server import app

def run_web_server():
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

async def main_loop():
    await speak("Hallo, aku Terry, ada apa sayang ?")
    while True:
        command = await listen()
        if command:
            print(f"Mendengar: {command}")
            
            # Daftar kata pemicu diperluas (Lebih Sensitif)
            TRIGGERS = [
                "terry", "halo", "buka", "ingat", "jam", "waktu", "tanggal", "putar", "tolong", 
                "siapa", "mainkan", "apa", "kenapa", "bagaimana", "gimana", "jelaskan", 
                "cerita", "dongeng", "hibur", "harga", "berapa", "cari", "tulis", "buat",
                "cek", "tes", "internet", "server", "check"
            ]
            
            if any(t in command for t in TRIGGERS):
                async for response_chunk in process(command):
                    if response_chunk:
                        await speak(response_chunk)
            else:
                print(f"[Info] Mengabaikan '{command}' (Tidak ada kata kunci pemicu)")
        
        schedule.run_pending()
        await asyncio.sleep(0.01)

if __name__ == "__main__":
    # Jalankan web server di thread terpisah
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()

    # Jalankan loop utama
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        print("Terry shutting down.")
