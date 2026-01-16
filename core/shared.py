import time

class SharedState:
    def __init__(self):
        self.logs = []
        self.model_name = "System"
        self.perplexity_model = "sonar-pro"
        self.manual_provider = "Gemini" # Default manual provider
        
        # Voice Control
        self.voice_enabled = True # Default ON
        self.chat_history = [] # Memori Percakapan
        self.max_logs = 100
        self.url_to_open = None # Membuka website di mini window
        self.image_to_show = None # Menampilkan gambar di popup
        
        # Status for UI animations
        self.status = "idle" # 'idle', 'thinking', 'speaking'
        
        # Brain Control
        self.brain_mode = "auto" # 'auto' or 'manual'

    def add_log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        self.logs.append(entry)
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)
        
        # Write directly to original stdout to avoid LoggerWriter recursion/loop
        # and ensure it appears in the console
        try:
            sys.__stdout__.write(entry + "\n")
            sys.__stdout__.flush()
        except: pass

    def set_model(self, name):
        self.model_name = name

    def set_perplexity_model(self, model):
        self.perplexity_model = model
        self.add_log(f"[Config] Perplexity model set to: {model}")

    def set_brain_mode(self, mode, provider=None):
        self.brain_mode = mode
        if mode == "manual":
            self.manual_provider = provider
            self.add_log(f"[Config] Brain MANUAL: {provider}")
        else:
            self.add_log(f"[Config] Brain AUTO (Terry's Choice)")

    # Global Instance
state = SharedState()

import sys

class LoggerWriter:
    def __init__(self, stream):
        self.terminal = stream

    def write(self, message):
        try:
            self.terminal.write(message)
            if message.strip():
                # Format similar to add_log
                timestamp = time.strftime("%H:%M:%S")
                state.logs.append(f"[{timestamp}] {message.strip()}")
                if len(state.logs) > state.max_logs:
                    state.logs.pop(0)
        except:
             pass

    def flush(self):
        try: self.terminal.flush()
        except: pass
        
    def isatty(self):
        return False

# Redirect Sys Pipes
sys.stdout = LoggerWriter(sys.__stdout__)
sys.stderr = LoggerWriter(sys.__stderr__)

def log(message):
    # Use the shared state method which handles appending and safe printing
    state.add_log(message)

