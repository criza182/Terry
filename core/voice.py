import os
import asyncio
import speech_recognition as sr
import edge_tts
import time
import random
import platform
import subprocess
import ctypes
from core.shared import log

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
            log(f"[Audio] Error playing on Linux: {e}")

recognizer = sr.Recognizer()
recognizer.energy_threshold = 300 
recognizer.dynamic_energy_threshold = True

mic = None # Deprecated (Replaced by SoundDevice)

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
            log(f"[Audio Worker] Error: {e}")
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

    log(f"Terry: {text}")
    
    filename = f"tts_{int(time.time())}_{random.randint(100,999)}.mp3"
    
    try:
        # 1. Generate Audio
        communicate = edge_tts.Communicate(text, VOICE, rate="+25%")
        await communicate.save(filename)
        
        # 2. Put in Queue
        await _audio_queue.put(filename)
            
    except Exception as e:
        log(f"[Audio] Error generating: {e}")
        if os.path.exists(filename):
            try: os.remove(filename)
            except: pass

# Flag untuk kalibrasi sekali saja
is_calibrated = False

# --- ALTERNATIVE MICROPHONE (SoundDevice) ---
try:
    import sounddevice as sd
    import numpy as np
    import scipy.io.wavfile as wav
    HAS_SD = True
except ImportError:
    HAS_SD = False
    log("[Voice] SoundDevice/Numpy not found. Install: pip install sounddevice numpy scipy")

async def listen() -> str:
    """Mendengarkan input suara menggunakan SoundDevice dengan deteksi aktivitas sederhana."""
    global is_calibrated
    from core.shared import state 
    
    if not HAS_SD:
        await asyncio.sleep(2)
        return ""
        
    if not state.voice_enabled:
        await asyncio.sleep(1)
        return ""

    if _audio_queue.qsize() > 0:
        log(f"[Audio] Menunggu {_audio_queue.qsize()} pesan suara selesai...")
        try:
            # Beri timeout 10 detik agar tidak hang selamanya jika driver audio bermasalah
            await asyncio.wait_for(_audio_queue.join(), timeout=10.0)
        except asyncio.TimeoutError:
            log("[Audio] Timeout menunggu suara selesai. Melanjutkan pendengaran...")
            # Bersihkan queue jika macet
            while not _audio_queue.empty():
                try: _audio_queue.get_nowait(); _audio_queue.task_done()
                except: pass

    log("Mendengarkan...")
    state.status = "listening"
    
    fs = 44100  
    duration = 5 # Tetap 5 detik namun kita bisa optimalkan nanti
    
    try:
        # Rekam audio
        recording = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype='int16')
        sd.wait() 
        state.status = "thinking"
        
        # Cek Volume
        rms = np.sqrt(np.mean(recording.astype(np.float32)**2))
        log(f"[Mic] Level: {rms:.1f}")
        
        # Jika terlalu sunyi, langsung skip tanpa tanya Google (Hemat kuota/waktu)
        if rms < 150:
            state.status = "idle"
            return ""
            
        audio_data = sr.AudioData(recording.tobytes(), fs, 2)
        
        log("[Mic] Sedang menerjemahkan suara...")
        try:
            # Gunakan timeout singkat untuk recognizer jika memungkinkan
            text = recognizer.recognize_google(audio_data, language="id-ID")
            if text:
                log(f"[Mic] Hasil: {text}")
                return text.lower()
        except sr.UnknownValueError:
            return ""
        except sr.RequestError as e:
            log(f"[Mic] Google Error (Cek Internet): {e}")
            return ""
        finally:
            state.status = "idle"
            
    except Exception as e:
        log(f"[Mic] Hardware Error: {e}")
        state.status = "idle"
        return ""
    return ""
