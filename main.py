import asyncio
import threading
import uvicorn
import schedule
from core.voice import listen, speak
from core.brain import process
from web.server import app
from core.shared import log  # Import logger

def run_web_server():
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="error") # Reduce noise

def cleanup_tts():
    import glob
    import os
    files = glob.glob("tts_*.mp3")
    for f in files:
        try: os.remove(f)
        except: pass
    log(f"Cleaned up {len(files)} old TTS files.")

async def main_loop():
    cleanup_tts()
    await speak("Halo, Aku Terry")
    log("Terry siap mendengarkan...") # Log
    
    while True:
        command = await listen()
        if command:
            log(f"Mendengar: {command}") # Log
            
            from core.shared import state
            state.status = "thinking"
            log("Terry sedang berpikir...")
            
            # Daftar kata pemicu diperluas (Lebih Sensitif)
            # Trigger Check REMOVED for easier interaction
            # if any(t in command for t in TRIGGERS):
            if True: # Always process
                async for response_chunk in process(command):
                    if response_chunk:
                        state.status = "speaking"
                        await speak(response_chunk)
            
            state.status = "idle"
            # else:
            #     log(f"[Info] Mengabaikan '{command}' (Tidak ada kata kunci pemicu)") # Log
        
        schedule.run_pending()
        await asyncio.sleep(0.01)

if __name__ == "__main__":
    # Jalankan web server di thread terpisah
    web_thread = threading.Thread(target=run_web_server, daemon=True)
    web_thread.start()
    log("Web Server started at :8000")

    # Jalankan loop utama
    try:
        asyncio.run(main_loop())
    except KeyboardInterrupt:
        log("Terry shutting down.")
