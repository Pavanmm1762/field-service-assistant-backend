from fastapi import APIRouter, File, UploadFile
from pathlib import Path
import hashlib

from app.services.vision_service import VisionService
from app.services.cache_service import cache_service
from app.services.context_service import context_service
from app.models.response_models import ImageAnalysisResponse

router = APIRouter(prefix="/api", tags=["Image"])

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

vision_service = VisionService()


@router.post("/image/upload", response_model=ImageAnalysisResponse)
async def upload_image(file: UploadFile = File(...)):

    # Read once
    contents = await file.read()

    # Generate hash
    image_hash = hashlib.sha256(contents).hexdigest()

    # Check cache
    cached_result = cache_service.get(image_hash)

    if cached_result:
        context_service.set_analysis(cached_result)

        return {
            **cached_result,
            "filename": file.filename,
            "saved_path": "cached",
            "content_type": file.content_type
        }

    # Save file
    file_location = UPLOAD_DIR / file.filename

    with file_location.open("wb") as buffer:
        buffer.write(contents)

    # Analyze
    result = vision_service.analyze_image(str(file_location))

    # Cache result
    if (
        result.get("equipment") != "Unknown"
        and result.get("confidence", 0) >=50
    ):
        cache_service.set(image_hash, result)

    # Store latest analysis for chat context
    context_service.set_analysis(result)

    return {
        **result,
        "filename": file.filename,
        "saved_path": str(file_location),
        "content_type": file.content_type
    }