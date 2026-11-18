from pathlib import Path
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from .config import ROOT, settings
from .api.chat import router as chat_router
from .api.voice import router as voice_router
from .api.documents import router as documents_router

app = FastAPI(title=settings.app_name, version="1.0.0", description="Bangla-English voice assistant starter")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"], allow_credentials=True, allow_methods=["GET", "POST"], allow_headers=["*"])
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")
templates = Jinja2Templates(directory=ROOT / "backend" / "app" / "templates")
app.include_router(chat_router); app.include_router(voice_router); app.include_router(documents_router)
@app.get("/")
async def home(request: Request): return templates.TemplateResponse(request, "index.html")
@app.get("/health")
def health(): return {"status": "ok", "service": "NOVA"}
@app.websocket("/ws/status")
async def websocket_status(ws: WebSocket):
    await ws.accept()
    try:
        await ws.send_json({"type": "connected", "message": "NOVA websocket ready"})
        while True:
            data = await ws.receive_text()
            await ws.send_json({"type": "ack", "message": data})
    except WebSocketDisconnect: pass
