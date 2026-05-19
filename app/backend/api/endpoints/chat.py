from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel

from backend.api import deps
from database.models.chat_message import ChatMessage
from backend.services.ai_service import ai_service

router = APIRouter()

class MessageSchema(BaseModel):
    role: str
    content: str

    class Config:
        from_attributes = True

class ChatIn(BaseModel):
    conversation_id: str
    message: str
    system_prompt: Optional[str] = None

@router.post("/stream")
def stream_chat(
    chat_in: ChatIn,
    db: Session = Depends(deps.get_db)
):
    conversation_id = chat_in.conversation_id
    user_content = chat_in.message
    system_prompt = chat_in.system_prompt

    # 1. Save User Message to Database
    user_msg = ChatMessage(conversation_id=conversation_id, role="user", content=user_content)
    db.add(user_msg)
    db.commit()

    # 2. Fetch past conversation history
    past_messages = db.query(ChatMessage).filter(
        ChatMessage.conversation_id == conversation_id
    ).order_by(ChatMessage.created_at.asc()).all()

    formatted_messages = []
    for msg in past_messages:
        formatted_messages.append({"role": msg.role, "content": msg.content})

    # If the last message in history is not the user's current message, append it (safety fallback)
    if not formatted_messages or formatted_messages[-1]["content"] != user_content:
        formatted_messages.append({"role": "user", "content": user_content})

    # 3. Stream Response and Accumulate to save at the end
    def event_generator():
        accumulated_response = []
        try:
            for chunk in ai_service.generate_chat_stream(formatted_messages, system_prompt=system_prompt):
                accumulated_response.append(chunk)
                yield chunk
        finally:
            full_response = "".join(accumulated_response)
            if full_response.strip():
                # Write assistant message to Database on complete stream
                # Need a new session context since generator runs after endpoint returns
                db_generator = deps.get_db()
                session = next(db_generator)
                try:
                    assistant_msg = ChatMessage(
                        conversation_id=conversation_id,
                        role="assistant",
                        content=full_response
                    )
                    session.add(assistant_msg)
                    session.commit()
                except Exception as ex:
                    session.rollback()
                finally:
                    session.close()

    return StreamingResponse(event_generator(), media_type="text/plain")

@router.get("/history/{conversation_id}", response_model=List[MessageSchema])
def get_chat_history(
    conversation_id: str,
    db: Session = Depends(deps.get_db)
):
    history = db.query(ChatMessage).filter(
        ChatMessage.conversation_id == conversation_id
    ).order_by(ChatMessage.created_at.asc()).all()
    return history

@router.delete("/history/{conversation_id}")
def clear_chat_history(
    conversation_id: str,
    db: Session = Depends(deps.get_db)
):
    db.query(ChatMessage).filter(ChatMessage.conversation_id == conversation_id).delete()
    db.commit()
    return {"status": "success", "message": "History cleared"}
