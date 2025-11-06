from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
import uuid

from core.database import get_db
from core.redis_manager import redis_manager
from schemas.chat_schema import ChatRequest, ChatResponse
from services.tool_service import ToolService

router = APIRouter(
    prefix="/api/v1/chat",
    tags=["Conversational RAG"]
)


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Chat endpoint that automatically decides whether to:
    1. Book an interview → Calls booking tool
    2. Answer a question → Uses RAG

    Multi-turn conversation is supported via Redis memory.
    """
    session_id = request.session_id or str(uuid.uuid4())

    try:
        chat_history = redis_manager.get_context(session_id, last_n=5)

        answer, is_booking = ToolService.process_query(
            query=request.query,
            chat_history=chat_history,
            db=db
        )


        redis_manager.save_message(session_id, "user", request.query)
        redis_manager.save_message(session_id, "assistant", answer)

        return ChatResponse(
            session_id=session_id,
            query=request.query,
            answer=answer,
            sources=[] if not is_booking else [] # No sources for booking
        )

    except Exception as e:
        print(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    try:
        history = redis_manager.get_history(session_id)
        return {"session_id": session_id, "total_messages": len(history), "messages": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/history/{session_id}")
async def clear_chat_history(session_id: str):
    try:
        redis_manager.clear_session(session_id)
        return {"message": f"History cleared for session {session_id}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
