import schedule
import time
import requests
from bs4 import BeautifulSoup
from AppOpener import open as app_opener
from core.shared import log

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
                
                # List of sites known to block iframes (X-Frame-Options: SAMEORIGIN/DENY)
                protected_sites = ["google.com", "facebook.com", "twitter.com", "instagram.com", "github.com"]
                is_protected = any(site in payload.lower() for site in protected_sites)
                
                from core.shared import state
                if is_protected:
                    import webbrowser
                    webbrowser.open(payload)
                    return f"Membuka {payload} di browser eksternal karena situs ini melarang frame internal untuk keamanan."
                
                state.url_to_open = payload
                return f"Membuka website {payload} di mini window HUD."


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
            # Run command with real-time logging
            from core.shared import state
            
            process = subprocess.Popen(
                cmd, 
                shell=True, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            result = ""
            
            # Stream stdout
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    clean_line = line.strip()
                    if clean_line:
                        state.add_log(f"[YouTube] {clean_line}")
                        result += clean_line 
                        
            # Capture stderr (warnings)
            stderr_output = process.stderr.read()
            if stderr_output:
                for err_line in stderr_output.splitlines():
                    if err_line.strip():
                        state.add_log(f"[YouTube WARNING] {err_line.strip()}")
            
            result = result.strip()
            
            if result:
                # Ambil baris pertama saja jika ada multi-line (antisipasi garbage)
                video_id = result.split('\n')[0].strip()
                video_url = f"https://www.youtube.com/embed/{video_id}?autoplay=1&mute=0"
                
                from core.shared import state
                state.url_to_open = video_url
                state.add_log(f"[DEBUG] Setting URL: {video_url}") # Debug Log
                
                return f"Memutar '{payload}' di mini window YouTube."

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

    elif action_type == "generate_image":
        import requests
        import os
        import subprocess
        
        try:
            prompt_encoded = payload.replace(" ", "%20")
            url = f"https://image.pollinations.ai/prompt/{prompt_encoded}"
            
            # Setup path
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
            gallery_dir = os.path.join(base_dir, "rumah", "galeri")
            if not os.path.exists(gallery_dir): os.makedirs(gallery_dir)
            
            filename = f"img_{int(time.time())}.jpg"
            file_path = os.path.join(gallery_dir, filename)
            
            print(f"Generating image (Pollinations): {payload}...")
            response = requests.get(url, timeout=20)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                
                # Trigger Frontend Popup
                from core.shared import state
                # Path relative to 'rumah' which is mounted as /media
                state.image_to_show = f"/media/galeri/{filename}"
                print(f"[Actions] Image generated. Triggering popup: {state.image_to_show}")
                
                # Disable external viewer for now
                # if os.name == 'nt':
                #     try: subprocess.Popen(['start', file_path], shell=True)
                #     except: pass
                
                return f"Gambar '{payload}' berhasil dibuat. Cek layar."
            else:
                raise Exception("Pollinations API failed")
                
        except Exception as e:
            print(f"Pollinations Error: {e}, mencoba backup Hugging Face...")
            return generate_image_hf(payload, gallery_dir, filename)

    elif action_type == "capture_web":
        import pyautogui
        import webbrowser
        import os
        import subprocess
        
        try:
            url = payload
            if not url.startswith("http"): url = "https://" + url
            
            print(f"Capturing web: {url}...")
            webbrowser.open(url)
            time.sleep(5) # Wait for page load
            
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) 
            ss_dir = os.path.join(base_dir, "rumah", "screenshots")
            if not os.path.exists(ss_dir): os.makedirs(ss_dir)
            
            filename = f"ss_{int(time.time())}.png"
            file_path = os.path.join(ss_dir, filename)
            
            pyautogui.screenshot(file_path)
            
            if os.name == 'nt':
                try: subprocess.Popen(['start', file_path], shell=True)
                except: pass
                
            return f"Screenshot website berhasil disimpan."
        except Exception as e:
            return f"Gagal screenshot: {e}"

    return "Aksi tidak dikenali."

def generate_image_hf(prompt, folder, filename):
    import requests
    import os
    import subprocess
    from dotenv import load_dotenv
    load_dotenv()
    
    token = os.getenv("HF_TOKEN")
    if not token:
        return "Gagal: Pollinations error dan HF_TOKEN tidak ditemukan di .env."
        
    API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.post(API_URL, headers=headers, json={"inputs": prompt})
        if response.status_code == 200:
            file_path = os.path.join(folder, filename)
            with open(file_path, "wb") as f:
                f.write(response.content)
                
            # Trigger Frontend Popup
            from core.shared import state
            state.image_to_show = f"/media/galeri/{filename}"
            
            # if os.name == 'nt':
            #     try: subprocess.Popen(['start', file_path], shell=True)
            #     except: pass
            
            return f"Gambar '{prompt}' berhasil dibuat (Backup HF)."
        else:
            return f"Gagal backup HF: {response.text}"
    except Exception as e:
        return f"Gagal total: {e}"

def scrape_web(url):
    """Membaca konten teks dari website untuk diringkas oleh AI."""
    if not url.startswith("http"):
        url = "https://" + url
    try:
        log(f"[Action] Scraping content from: {url}")
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Hapus elemen yang tidak perlu
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()
            
        text = soup.get_text(separator=' ', strip=True)
        # Limit text size for AI prompt
        return text[:5000]
    except Exception as e:
        return f"Gagal membaca website: {e}"
