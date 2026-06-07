from fastapi import FastAPI
from app.api.image import router as image_router
from app.api.chat import router as chat_router
from app.api.history import router as history_router
from app.api.session import router as session_router
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="Field Service Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount(
    "/uploads",
    StaticFiles(directory="data/uploads"),
    name="uploads"
)
# routers
app.include_router(image_router)       
app.include_router(chat_router)
app.include_router(history_router)  # Include history router for history management endpoints
app.include_router(session_router)  # Include session router for session management endpoints

@app.get("/health")
async def health():
    return {"status": "healthy"}