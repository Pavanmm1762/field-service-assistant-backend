
from fastapi import APIRouter

from app.services.chat_service import ChatService
from app.models.request_models import ChatRequest

router = APIRouter(prefix="/api", tags=["Chat"])

chat_service = ChatService()

@router.post("/chat")
async def chat(request: ChatRequest):  
    # Process the chat message using the ChatService
    response = chat_service.generate_response(request.message)
    return {"message": response}