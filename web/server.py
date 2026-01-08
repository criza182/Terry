from fastapi import FastAPI, Request
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

@app.get("/api/update")
async def get_update():
    return JSONResponse({
        "model": state.model_name,
        "perplexity_model": state.perplexity_model, # Return current config
        "logs": state.logs[-50:] # Return last 50 logs
    })

class ModelConfig(BaseModel):
    model_name: str

@app.post("/api/settings")
async def set_settings(config: ModelConfig):
    state.set_perplexity_model(config.model_name)
    return {"status": "ok", "model": config.model_name}


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    async def generate():
        async for chunk in process(request.message):
            if chunk:
                yield chunk + "\n" # Add newline for client
    
    return StreamingResponse(generate(), media_type="text/plain")
