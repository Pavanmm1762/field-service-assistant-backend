from fastapi import FastAPI
from app.api.image import router as image_router
from app.api.chat import router as chat_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Field Service Assistant")

origins = [
    "http://localhost:5173",
    "https://field-service-assistant-frontend.vercel.app/"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# routers
app.include_router(image_router)
app.include_router(chat_router)


@app.get("/health")
async def health():
    return {"status": "healthy"}