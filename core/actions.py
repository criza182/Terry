import schedule
import time
from AppOpener import open as app_opener

def reminder_job(message: str):
    print(f"\n[PENGINGAT] TERRY: {message}")
    # Jika ingin suara, bisa import speak tapi harus hati-hati circular import
    # Untuk sekarang print saja atau pop-up

def execute_action(action_type: str, payload="") -> str:
    """Mengeksekusi aksi sistem secara sederhana."""
    
    if action_type == "open_app":
        import webbrowser
        
        try:
            print(f"Mencoba membuka: {payload}")
            # Cek jika ini URL website
            if any(ext in payload for ext in [".com", ".id", ".net", ".org", "http"]):
                if not payload.startswith("http"):
                    payload = "https://" + payload
                webbrowser.open(payload)
                return f"Membuka website {payload}."
            else:
                app_opener(payload, match_closest=True)
                return f"Membuka {payload}."
        except Exception as e:
            return f"Gagal membuka {payload}."
            
    elif action_type == "set_reminder":
        try:
            seconds = payload.get("seconds", 10)
            message = payload.get("message", "Pengingat")
            def job_once():
                reminder_job(message)
                return schedule.CancelJob
            schedule.every(seconds).seconds.do(job_once)
            return f"Oke, saya ingatkan dalam {seconds} detik."
        except:
            return "Gagal atur pengingat."

    elif action_type == "play_youtube":
        import webbrowser
        import subprocess
        
        try:
            print(f"Mencari video untuk: {payload}")
            # Menggunakan yt-dlp untuk mencari ID video pertama
            # Command: yt-dlp "ytsearch1:query" --get-id
            import sys
            import os
            
            if sys.platform == "win32":
                yt_dlp_path = r"venv\Scripts\yt-dlp"
            else:
                yt_dlp_path = "venv/bin/yt-dlp"
                
            cmd = f'{yt_dlp_path} "ytsearch1:{payload}" --get-id --skip-download'
            
            # Run command
            result = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
            
            if result:
                video_url = f"https://www.youtube.com/watch?v={result}"
                webbrowser.open(video_url)
                return f"Memutar '{payload}' di YouTube."
            else:
                # Fallback jika ID tidak ketemu
                webbrowser.open(f"https://www.youtube.com/results?search_query={payload}")
                return f"Mencari '{payload}' di YouTube."
                
        except Exception as e:
            print(f"YouTube Error: {e}")
            webbrowser.open(f"https://www.youtube.com/results?search_query={payload}")
            return f"Membuka pencarian YouTube untuk '{payload}'."

    return "Aksi tidak dikenali."
