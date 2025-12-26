from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi import Request

app = FastAPI(title="Terry Dashboard")

# Setup templates
# app.mount("/static", StaticFiles(directory="web/static"), name="static") 
# (Static belum dibuat, komen dulu)

templates = Jinja2Templates(directory="web/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "status": "Online"})

@app.get("/status")
async def get_status():
    return {"status": "running", "ai_model": "Gemini-Pro"}
