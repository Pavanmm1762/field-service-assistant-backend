from pydantic import BaseModel
from typing import List


class ImageAnalysisResponse(BaseModel):
    equipment: str
    issue: str
    severity: str
    confidence: int
    fault_detected: bool

    root_cause: str
    recommended_action: str
    tools_required: List[str]
    safety_warning: str

    filename: str
    saved_path: str
    content_type: str | None = None


class ChatResponse(BaseModel):
    message: str