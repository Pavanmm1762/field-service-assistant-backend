from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from PIL import Image

from app.core.config import Settings
from app.services.ai.interfaces import (
    AIResponse,
    ChatMessage,
    EmbeddingResponse,
    ImageAnalysis,
    ToolCall,
)

logger = logging.getLogger(__name__)


class GeminiAdapter:
    provider_name = "gemini"

    def __init__(self, settings: Settings):
        from google import genai

        self.settings = settings
        self.client = genai.Client(api_key=settings.llm_api_key_value)

    async def chat(
        self,
        messages: list[ChatMessage],
        *,
        model: str | None = None,
        temperature: float | None = None,
    ) -> AIResponse:
        model_name = model or self.settings.LLM_MODEL
        prompt = self._messages_to_prompt(messages)
        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=model_name,
                contents=prompt,
            )
            return AIResponse(
                text=response.text or "",
                model=model_name,
                provider=self.provider_name,
                raw=response,
            )
        except Exception:
            logger.exception("Gemini chat request failed")
            raise

    async def chat_with_tools(
        self,
        messages: list[ChatMessage],
        tools: list[dict[str, Any]],
        *,
        model: str | None = None,
        temperature: float | None = None,
    ) -> AIResponse:
        model_name = model or self.settings.LLM_MODEL
        prompt = self._messages_to_prompt(messages)
        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=model_name,
                contents=prompt,
                config={"tools": tools},
            )
            return AIResponse(
                text=response.text or "",
                model=model_name,
                provider=self.provider_name,
                tool_calls=self._tool_calls(response),
                raw=response,
            )
        except Exception:
            logger.exception("Gemini tool chat request failed")
            raise

    async def embed(
        self,
        text: str,
        *,
        model: str | None = None,
    ) -> EmbeddingResponse:
        model_name = model or self.settings.LLM_EMBEDDING_MODEL or self.settings.LLM_MODEL
        try:
            response = await asyncio.to_thread(
                self.client.models.embed_content,
                model=model_name,
                contents=text,
            )
            return EmbeddingResponse(
                embedding=response.embeddings[0].values,
                model=model_name,
                provider=self.provider_name,
            )
        except Exception:
            logger.exception("Gemini embedding request failed")
            raise

    async def analyze_image(
        self,
        image_path: str,
        prompt: str,
        *,
        model: str | None = None,
    ) -> ImageAnalysis:
        model_name = model or self.settings.LLM_VISION_MODEL or self.settings.LLM_MODEL
        image = Image.open(image_path)
        try:
            response = await asyncio.to_thread(
                self.client.models.generate_content,
                model=model_name,
                contents=[prompt, image],
            )
            return self._image_analysis_from_text((response.text or "").strip())
        except Exception:
            logger.exception("Gemini image analysis request failed")
            raise
        finally:
            image.close()

    @staticmethod
    def _messages_to_prompt(messages: list[ChatMessage]) -> str:
        return "\n\n".join(f"{message.role}: {message.content}" for message in messages)

    @staticmethod
    def _image_analysis_from_text(text: str) -> ImageAnalysis:
        clean_text = text.strip()
        if clean_text.startswith("```json"):
            clean_text = clean_text.replace("```json", "").replace("```", "").strip()
        try:
            data = json.loads(clean_text)
        except json.JSONDecodeError:
            return ImageAnalysis(
                equipment="Unknown",
                issue="Unable to determine",
                severity="Low",
                confidence=0,
                fault_detected=False,
                raw_response=text,
            )
        return ImageAnalysis(
            equipment=data.get("equipment", "Unknown"),
            issue=data.get("issue", "Unknown"),
            severity=data.get("severity", "Low"),
            confidence=data.get("confidence", 0),
            fault_detected=data.get("fault_detected", False),
            root_cause=data.get("root_cause", ""),
            recommended_action=data.get("recommended_action", ""),
            tools_required=data.get("tools_required", []),
            safety_warning=data.get("safety_warning", ""),
        )

    @staticmethod
    def _tool_calls(response: Any) -> list[ToolCall]:
        calls = []
        for candidate in getattr(response, "candidates", []) or []:
            content = getattr(candidate, "content", None)
            for part in getattr(content, "parts", []) or []:
                function_call = getattr(part, "function_call", None)
                if not function_call:
                    continue
                arguments = getattr(function_call, "args", {}) or {}
                calls.append(
                    ToolCall(
                        name=getattr(function_call, "name", ""),
                        arguments=dict(arguments),
                    )
                )
        return calls
