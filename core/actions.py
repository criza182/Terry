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

    elif action_type == "get_time":
        from datetime import datetime
        now = datetime.now()
        return f"Sekarang jam {now.strftime('%H:%M')}."

    elif action_type == "get_date":
        from datetime import datetime
        import locale
        # Coba set locale ke Indonesia kalau bisa, kalau tidak default
        try:
            locale.setlocale(locale.LC_TIME, 'id_ID')
        except:
            pass
        now = datetime.now()
        return f"Hari ini adalah {now.strftime('%A, %d %B %Y')}."

    elif action_type == "volume_up":
        import pyautogui
        # Tekan tombol volume up beberapa kali agar terasa bedanya
        pyautogui.press("volumeup", presses=5) 
        return "Membesarkan volume."

    elif action_type == "volume_down":
        import pyautogui
        pyautogui.press("volumedown", presses=5) 
        return "Mengecilkan volume."
        
    elif action_type == "volume_mute":
        import pyautogui
        pyautogui.press("volumemute") 
        return "Mematikan/Menyalakan suara."

    elif action_type == "check_server":
        import subprocess
        import platform
        
        host = payload if payload else "tonykumbayer.my.id"
        print(f"Pinging {host}...")
        
        # Bedakan command Windows vs Linux
        param = '-n' if platform.system().lower()=='windows' else '-c'
        command = ['ping', param, '1', host]
        
        try:
            # Jalankan ping
            output = subprocess.check_output(command, stderr=subprocess.STDOUT, timeout=5).decode()
            
            # Cek hasil (Windows: "Reply from", Linux: "bytes from")
            if "Reply from" in output or "bytes from" in output:
                # Coba ambil waktu ping (opsional/sederhana)
                return f"Server {host} ONLINE! Koneksi aman."
            else:
                return f"Server {host} tidak merespon. Mungkin sedang down."
        except subprocess.TimeoutExpired:
            return f"Ping ke {host} time out (RTO)."
        except Exception as e:
            return f"Gagal mengecek server: {str(e)}"

        except Exception as e:
            return f"Gagal mengecek server: {str(e)}"

    elif action_type == "media_play_pause":
        import pyautogui
        pyautogui.press("playpause")
        return "Oke."
        
    elif action_type == "media_next":
        import pyautogui
        pyautogui.press("nexttrack")
        return "Lagu selanjutnya."

    elif action_type == "write_file":
        import os
        import subprocess
        import re

        # Payload format expected: "filename.txt|content"
        # But AI is stupid, so we need to handle "content|filename.txt" or just "content"
        try:
            filename = "catatan_terry.txt" # Default
            content = payload

            if "|" in payload:
                parts = payload.split("|")
                # Heuristik: Mana yang lebih mirip nama file?
                # Nama file biasanya pendek (< 50 char) dan tidak punya newline
                p1 = parts[0].strip()
                p2 = parts[-1].strip() # Ambil bagian terakhir jika split > 2

                if len(p1) < 60 and "\n" not in p1 and "." in p1:
                    filename = p1
                    content = "|".join(parts[1:]) # Sisanya adalah konten
                elif len(p2) < 60 and "\n" not in p2 and "." in p2:
                    filename = p2
                    content = "|".join(parts[:-1]) # Sisanya adalah konten

            # Sanitasi Nama File (Hapus karakter dilarang Windows)
            filename = re.sub(r'[\\/*?:"<>|]', "", filename)
            filename = filename.replace("\n", "").strip()

            # Folder kerja Terry
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
            work_dir = os.path.join(base_dir, "rumah")
            
            if not os.path.exists(work_dir):
                os.makedirs(work_dir)
                
            file_path = os.path.join(work_dir, filename)
            
            # Tulis file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
                
            # Buka file otomatis (Notepad)
            if os.name == 'nt':
                subprocess.Popen(['notepad.exe', file_path])
            else: 
                try:
                    subprocess.Popen(['xdg-open', file_path])
                except: pass

            return f"Berhasil menulis ke '{filename}'."
            
        except Exception as e:
            return f"Gagal menulis file: {e}"

    return "Aksi tidak dikenali."
