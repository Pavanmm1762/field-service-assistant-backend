from __future__ import annotations

from enum import StrEnum
from typing import Any, Protocol

from pydantic import BaseModel, Field


class AIProvider(StrEnum):
    GEMINI = "gemini"
    OPENAI_COMPATIBLE = "openai_compatible"


class ChatMessage(BaseModel):
    role: str
    content: str


class ToolCall(BaseModel):
    id: str | None = None
    name: str
    arguments: dict[str, Any] = Field(default_factory=dict)


class AIUsage(BaseModel):
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    total_tokens: int | None = None


class AIResponse(BaseModel):
    text: str
    model: str | None = None
    provider: str
    tool_calls: list[ToolCall] = Field(default_factory=list)
    raw: Any | None = None
    usage: AIUsage | None = None


class EmbeddingResponse(BaseModel):
    embedding: list[float]
    model: str | None = None
    provider: str


class ImageAnalysis(BaseModel):
    equipment: str = "Unknown"
    issue: str = "Unknown"
    severity: str = "Low"
    confidence: int = 0
    fault_detected: bool = False
    root_cause: str = ""
    recommended_action: str = ""
    tools_required: list[str] = Field(default_factory=list)
    safety_warning: str = ""
    raw_response: str | None = None


class AIAdapter(Protocol):
    async def chat(
        self,
        messages: list[ChatMessage],
        *,
        model: str | None = None,
        temperature: float | None = None,
    ) -> AIResponse:
        ...

    async def chat_with_tools(
        self,
        messages: list[ChatMessage],
        tools: list[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float | None = None,
    ) -> AIResponse:
        ...

    async def embed(
        self,
        text: str,
        *,
        model: str | None = None,
    ) -> EmbeddingResponse:
        ...

    async def analyze_image(
        self,
        image_path: str,
        prompt: str,
        *,
        model: str | None = None,
    ) -> ImageAnalysis:
        ...
