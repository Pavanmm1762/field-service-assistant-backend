from __future__ import annotations

from typing import Any

from app.services.ai.interfaces import (
    AIAdapter,
    AIResponse,
    ChatMessage,
    EmbeddingResponse,
    ImageAnalysis,
)


class AIService:
    def __init__(self, adapter: AIAdapter):
        self._adapter = adapter

    async def chat(
        self,
        messages: list[ChatMessage],
        *,
        model: str | None = None,
        temperature: float | None = None,
    ) -> AIResponse:
        return await self._adapter.chat(
            messages,
            model=model,
            temperature=temperature,
        )

    async def chat_with_tools(
        self,
        messages: list[ChatMessage],
        tools: list[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float | None = None,
    ) -> AIResponse:
        return await self._adapter.chat_with_tools(
            messages,
            tools,
            model=model,
            temperature=temperature,
        )

    async def embed(
        self,
        text: str,
        *,
        model: str | None = None,
    ) -> EmbeddingResponse:
        return await self._adapter.embed(text, model=model)

    async def analyze_image(
        self,
        image_path: str,
        prompt: str,
        *,
        model: str | None = None,
    ) -> ImageAnalysis:
        return await self._adapter.analyze_image(
            image_path,
            prompt,
            model=model,
        )
