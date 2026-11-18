import uuid
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from starlette.concurrency import run_in_threadpool
from ..config import UPLOAD_DIR, settings
from ..database import get_db, Message
from ..services.asr import transcribe
from ..services.llm import answer
from ..services.tts import synthesize
from ..services.rag import retrieve

router = APIRouter(prefix="/api/voice", tags=["voice"])
ALLOWED = {"audio/webm", "audio/wav", "audio/x-wav", "audio/mpeg", "audio/mp4", "audio/ogg", "application/octet-stream"}
@router.post("/ask")
async def voice_ask(audio: UploadFile = File(...), session_id: str = Form("default"), reply_language: str = Form("auto"), db: Session = Depends(get_db)):
    content_type = (audio.content_type or "").split(";")[0].lower()
    if content_type not in ALLOWED:
        raise HTTPException(415, "Unsupported audio type. Use WebM, WAV, MP3, MP4 or OGG.")
    if reply_language not in {"auto", "bn", "en"}:
        raise HTTPException(422, "reply_language must be auto, bn or en")
    data = await audio.read(settings.max_upload_mb * 1024 * 1024 + 1)
    if not data or len(data) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(413, "Audio is empty or exceeds upload limit")
    suffix = Path(audio.filename or "recording.webm").suffix.lower()
    if suffix not in {".webm", ".wav", ".mp3", ".m4a", ".ogg", ".mp4"}: suffix = ".webm"
    source = UPLOAD_DIR / f"{uuid.uuid4().hex}{suffix}"
    source.write_bytes(data)
    try:
        transcript = await run_in_threadpool(transcribe, str(source))
        if not transcript["text"]: raise HTTPException(422, "No speech detected")
        rows = db.query(Message).filter(Message.session_id == session_id).order_by(Message.id.desc()).limit(10).all()
        history = [{"role": r.role, "content": r.content} for r in reversed(rows)]
        context = retrieve(transcript["text"], db)
        reply = await answer(transcript["text"], history, context, reply_language)
        language = reply_language if reply_language != "auto" else ("en" if transcript["language"] == "en" else "bn")
        audio_file = await synthesize(reply, language)
        db.add_all([Message(session_id=session_id, role="user", content=transcript["text"]), Message(session_id=session_id, role="assistant", content=reply)])
        db.commit()
        return {"transcript": transcript["text"], "language": transcript["language"], "reply": reply, "audio_url": f"/api/voice/audio/{audio_file}"}
    finally:
        source.unlink(missing_ok=True)
@router.get("/audio/{filename}")
def audio_file(filename: str):
    if Path(filename).name != filename or not filename.endswith(".mp3"): raise HTTPException(400, "Invalid filename")
    path = UPLOAD_DIR / filename
    if not path.exists(): raise HTTPException(404, "Audio not found")
    return FileResponse(path, media_type="audio/mpeg", filename=filename)
