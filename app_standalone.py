import os
import subprocess
import time
import threading
import sys

def launch_terry_app():
    # 1. Start main.py (server & loop)
    print("[Launcher] Starting Terry core...")
    # Pass current environment to ensure all paths (like schedule) are visible
    terry_process = subprocess.Popen(
        [sys.executable, "main.py"], 
        env=os.environ.copy()
    )
    
    # 2. Wait for server to start
    print("[Launcher] Waiting for server...")
    time.sleep(3)
    
    # 3. Launch browser in app mode
    # Try Edge first, then Chrome
    app_url = "http://localhost:8000"
    
    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    
    launched = False
    
    if os.path.exists(edge_path):
        print("[Launcher] Launching via MS Edge App Mode...")
        subprocess.Popen([edge_path, f"--app={app_url}"])
        launched = True
    elif os.path.exists(chrome_path):
        print("[Launcher] Launching via Google Chrome App Mode...")
        subprocess.Popen([chrome_path, f"--app={app_url}"])
        launched = True
    else:
        print("[Launcher] Chrome/Edge not found in default paths, opening default browser...")
        import webbrowser
        webbrowser.open(app_url)
        launched = True

    if launched:
        print("[Launcher] Terry UI is running. Close the app window to exit (or use Ctrl+C in terminal).")
        try:
            terry_process.wait()
        except KeyboardInterrupt:
            print("[Launcher] Shutting down...")
            terry_process.terminate()

if __name__ == "__main__":
    launch_terry_app()
