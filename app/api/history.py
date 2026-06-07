from fastapi import APIRouter, HTTPException
from app.services.history_service import history_service

router = APIRouter(
    prefix="/api",
    tags=["History"]
)


@router.get("/history")
async def get_history():

    return history_service.get_sessions()


@router.get("/history/{session_id}")
async def get_session(session_id: str):

    session = history_service.get_session(
        session_id
    )

    if not session:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    return session