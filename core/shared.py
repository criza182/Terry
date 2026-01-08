import time

class SharedState:
    def __init__(self):
        self.logs = []
        self.model_name = "System"
        self.perplexity_model = "sonar" # Default
        self.chat_history = [] # Memori Percakapan
        self.max_logs = 100

    def add_log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        print(entry) # Still print to console
        self.logs.append(entry)
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)

    def set_model(self, name):
        self.model_name = name

    def set_perplexity_model(self, model):
        self.perplexity_model = model
        self.add_log(f"[Config] Perplexity model set to: {model}")

# Global Instance
state = SharedState()

def log(message):
    state.add_log(message)
