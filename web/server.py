from fastapi import FastAPI, Request
from typing import Optional
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from pydantic import BaseModel
from core.brain import process
from core.shared import state # Import Shared State
import os

app = FastAPI(title="Terry Dashboard")

# Setup static files
if not os.path.exists("web/static"):
    os.makedirs("web/static")

app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Setup media files (images/screenshots)
if not os.path.exists("rumah"):
    os.makedirs("rumah")
app.mount("/media", StaticFiles(directory="rumah"), name="media")

# Setup templates
templates = Jinja2Templates(directory="web/templates")

class ChatRequest(BaseModel):
    message: str

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "status": "Online"})

@app.get("/status")
async def get_status():
    return {"status": "running", "ai_model": state.model_name}

import psutil
import platform

@app.post("/api/toggle_voice")
async def toggle_voice():
    state.voice_enabled = not state.voice_enabled
    status = "ON" if state.voice_enabled else "OFF"
    state.add_log(f"SYSTEM_CONFIG: Mic {status}")
    return {"voice_enabled": state.voice_enabled}

@app.get("/api/update")
async def get_update():
    url = state.url_to_open
    if url:
        print(f"[SERVER] Sending URL to Frontend: {url}") # Console Debug
        state.url_to_open = None # Clear after sending
        
    img = state.image_to_show
    if img:
        print(f"[SERVER] Sending Image to Frontend: {img}")
        state.image_to_show = None
    
    # helper for human readable size
    def get_size(bytes, suffix="B"):
        factor = 1024
        for unit in ["", "K", "M", "G", "T", "P"]:
            if bytes < factor:
                return f"{bytes:.2f}{unit}{suffix}"
            bytes /= factor
            
    # Gather System Info
    cpu_usage = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory()
    ram_used = get_size(ram.used)
    ram_total = get_size(ram.total)
    ram_percent = ram.percent
    
    # GPU Info (Simple WMI fallback for Windows)
    gpu_name = "N/A"
    try:
        import subprocess
        # Get Name
        wmi_cmd = "wmic path win32_VideoController get name"
        output = subprocess.check_output(wmi_cmd, shell=True).decode().strip()
        lines = [line.strip() for line in output.split('\n') if line.strip()]
        if len(lines) > 1:
            gpu_name = lines[1] # The second line usually contains the first GPU name
    except:
        pass

    sys_info = {
        "os": f"{platform.system()} {platform.release()}",
        "processor": platform.processor(),
        "ram_display": f"{ram_used} / {ram_total}",
        "cpu_load": cpu_usage,
        "ram_load": ram_percent,
        "gpu_name": gpu_name
    }

    return JSONResponse({
        "model": state.model_name,
        "perplexity_model": state.perplexity_model,
        "logs": state.logs[-50:],
        "url_to_open": url,
        "image_to_show": img,
        "system_stats": sys_info,
        "voice_enabled": state.voice_enabled,
        "status": state.status
    })


class BrainConfig(BaseModel):
    mode: str 
    provider: Optional[str] = None
    or_model: Optional[str] = None # No longer explicitly used for manual select but kept for compatibility for a moment? No, let's remove.

@app.post("/api/set_brain")
async def set_brain(config: BrainConfig):
    state.set_brain_mode(config.mode, config.provider)
    return {"status": "ok", "mode": state.brain_mode, "provider": state.manual_provider}

class ModelConfig(BaseModel):
    model_name: str

@app.post("/api/settings")
async def set_settings(config: ModelConfig):
    state.set_perplexity_model(config.model_name)
    return {"status": "ok", "model": config.model_name}


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    async def generate():
        async for chunk in process(request.message):
            if chunk:
                yield chunk + "\n" # Add newline for client
    
    return StreamingResponse(generate(), media_type="text/plain")
