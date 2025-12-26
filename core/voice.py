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

async def speak(text: str):
    """Mengubah teks menjadi suara dengan Native Windows Player."""
    if not text: return
    print(f"Terry: {text}")
    
    filename = f"tts_{int(time.time())}_{random.randint(100,999)}.mp3"
    
    try:
        # 1. Generate Audio
        communicate = edge_tts.Communicate(text, VOICE)
        await communicate.save(filename)
        
        # 2. Play Audio (Run in executor)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, play_audio_cross_platform, filename)
            
    except Exception as e:
        print(f"[Audio] Error: {e}")
    finally:
        if os.path.exists(filename):
            try:
                os.remove(filename)
            except:
                pass

# Flag untuk kalibrasi sekali saja
is_calibrated = False

async def listen() -> str:
    """Mendengarkan input suara."""
    global is_calibrated
    
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
