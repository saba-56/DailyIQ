from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.database import get_db
from services.ai_service import ask_ai_chat

router = APIRouter(prefix="/ask-ai", tags=["ask-ai"])


class ChatMessage(BaseModel):
    role: str = Field(pattern="^(user|model)$")
    content: str


class AskAIRequest(BaseModel):
    message: str = Field(..., min_length=1)
    history: list[ChatMessage] = []


class AskAIResponse(BaseModel):
    reply: str


@router.post("", response_model=AskAIResponse)
def ask_ai_endpoint(payload: AskAIRequest, db: Session = Depends(get_db)):
    user_query = payload.message.strip()
    if not user_query:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")

    history_dicts = [
        {"role": msg.role, "content": msg.content}
        for msg in payload.history
    ]

    reply = ask_ai_chat(
        message=user_query,
        history=history_dicts,
        db=db
    )

    return {"reply": reply}
