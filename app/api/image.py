from fastapi import APIRouter, File, UploadFile
from app.services.vision_service import VisionService
from pathlib import Path

from app.models.response_models import ImageAnalysisResponse

router = APIRouter(prefix="/api", tags=["Image"])

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

vision_service = VisionService()

@router.post("/image/upload", response_model=ImageAnalysisResponse)
async def upload_image(file: UploadFile = File(...)):

    # Save the uploaded file to disk
    file_location = UPLOAD_DIR / file.filename  
    with file_location.open("wb") as buffer:
        buffer.write(await file.read())

    result = vision_service.analyze_image(str(file_location))

    return {
        **result,
        "filename": file.filename,
        "saved_path": str(file_location),
        "content_type": file.content_type
    }