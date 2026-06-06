from pydantic import BaseModel


class ImageAnalysisResponse(BaseModel):
    equipment: str
    issue: str
    severity: str
    confidence: int
    filename: str
    saved_path: str
    content_type: str | None = None

class ChatResponse(BaseModel):
    message: str
