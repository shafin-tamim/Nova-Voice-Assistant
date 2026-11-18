from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from ..database import get_db, Message
from ..services.llm import answer
from ..services.rag import retrieve

router = APIRouter(prefix="/api", tags=["chat"])
class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    session_id: str = Field(default="default", min_length=1, max_length=100)
    reply_language: str = "auto"
class ChatResponse(BaseModel):
    reply: str
    session_id: str
@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, db: Session = Depends(get_db)):
    if req.reply_language not in {"auto", "bn", "en"}:
        raise HTTPException(422, "reply_language must be auto, bn or en")
    rows = db.query(Message).filter(Message.session_id == req.session_id).order_by(Message.id.desc()).limit(10).all()
    history = [{"role": r.role, "content": r.content} for r in reversed(rows)]
    context = retrieve(req.message, db)
    reply = await answer(req.message, history, context, req.reply_language)
    db.add_all([Message(session_id=req.session_id, role="user", content=req.message), Message(session_id=req.session_id, role="assistant", content=reply)])
    db.commit()
    return ChatResponse(reply=reply, session_id=req.session_id)
@router.get("/history/{session_id}")
def history(session_id: str, db: Session = Depends(get_db)):
    rows = db.query(Message).filter(Message.session_id == session_id).order_by(Message.id.asc()).limit(200).all()
    return [{"role": r.role, "content": r.content, "created_at": r.created_at.isoformat()} for r in rows]
