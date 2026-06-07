# app/api/session.py

from fastapi import APIRouter
from app.services.context_service import context_service
from app.services.chat_memory_service import chat_memory_service

router = APIRouter(prefix="/api", tags=["Session"])

@router.post("/session/reset")
async def reset_session():

    context_service.clear()

    chat_memory_service.clear()

    return {
        "message": "Session reset"
    }