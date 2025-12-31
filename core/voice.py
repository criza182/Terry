import os
import asyncio
import speech_recognition as sr
import edge_tts
import time
import random
import platform
import subprocess
import ctypes
import os

# Detect OS
IS_WINDOWS = platform.system() == "Windows"

def play_audio_cross_platform(filename):
    """Play audio consistent with the OS."""
    file_path = os.path.abspath(filename)
    
    if IS_WINDOWS:
        # --- Windows Native (MCI) ---
        alias = f"terry_{random.randint(1000,9999)}"
        ctypes.windll.winmm.mciSendStringW(f'open "{file_path}" type mpegvideo alias {alias}', None, 0, 0)
        ctypes.windll.winmm.mciSendStringW(f'play {alias} wait', None, 0, 0)
        ctypes.windll.winmm.mciSendStringW(f'close {alias}', None, 0, 0)
    else:
        # --- Linux/Mac (FFplay) ---
        # Uses ffplay (part of ffmpeg) which is already a requirement
        # -nodisp: No graphical window
        # -autoexit: Close after playing
        # -loglevel quiet: Suppress output
        try:
            subprocess.run(["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", file_path], check=True)
        except Exception as e:
            print(f"[Audio] Error playing on Linux: {e}")

recognizer = sr.Recognizer()
recognizer.energy_threshold = 300 
recognizer.dynamic_energy_threshold = True

mic = sr.Microphone()
VOICE = "id-ID-GadisNeural"

# Audio Queue and Worker
_audio_queue = asyncio.Queue()
_worker_task = None

async def _audio_worker():
    """Worker to play audio from the queue sequentially."""
    while True:
        filename = await _audio_queue.get()
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, play_audio_cross_platform, filename)
        except Exception as e:
            print(f"[Audio Worker] Error: {e}")
        finally:
            if os.path.exists(filename):
                try:
                    os.remove(filename)
                except:
                    pass
            _audio_queue.task_done()

async def speak(text: str):
    """Mengubah teks menjadi suara dan memasukkannya ke antrean."""
    global _worker_task
    if not text: return
    
    # Start worker if not running
    if _worker_task is None or _worker_task.done():
        _worker_task = asyncio.create_task(_audio_worker())

    print(f"Terry: {text}")
    
    filename = f"tts_{int(time.time())}_{random.randint(100,999)}.mp3"
    
    try:
        # 1. Generate Audio
        communicate = edge_tts.Communicate(text, VOICE, rate="+25%")
        await communicate.save(filename)
        
        # 2. Put in Queue
        await _audio_queue.put(filename)
            
    except Exception as e:
        print(f"[Audio] Error generating: {e}")
        if os.path.exists(filename):
            try: os.remove(filename)
            except: pass

# Flag untuk kalibrasi sekali saja
is_calibrated = False

async def listen() -> str:
    """Mendengarkan input suara, menunggu sampai Terry selesai bicara."""
    global is_calibrated
    
    # Tunggu sampai Terry selesai bicara (Antrean kosong)
    if _audio_queue.qsize() > 0:
        await _audio_queue.join()

    with mic as source:
        try:
            if not is_calibrated:
                print("[Mic] Kalibrasi... (Hening sejenak)")
                recognizer.adjust_for_ambient_noise(source, duration=1)
                is_calibrated = True
            
            print("Mendengarkan...", end="\r")
            
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=10)
            text = recognizer.recognize_google(audio, language="id-ID")
            return text.lower()
            
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except Exception as e:
            print(f"[Mic] Error: {e}")
            return ""
