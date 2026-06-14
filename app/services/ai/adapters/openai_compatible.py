from __future__ import annotations

import base64
import json
import logging
from pathlib import Path
from typing import Any

from app.core.config import Settings
from app.services.ai.interfaces import (
    AIResponse,
    AIUsage,
    ChatMessage,
    EmbeddingResponse,
    ImageAnalysis,
    ToolCall,
)

logger = logging.getLogger(__name__)


class OpenAICompatibleAdapter:
    provider_name = "openai_compatible"

    def __init__(self, settings: Settings):
        from openai import AsyncAzureOpenAI, AsyncOpenAI

        self.settings = settings
        api_key = settings.llm_api_key_value

        if settings.LLM_API_TYPE == "azure":
            self.client = AsyncAzureOpenAI(
                api_key=api_key,
                azure_endpoint=settings.LLM_BASE_URL,
                api_version=settings.LLM_API_VERSION,
            )
        else:
            self.chat_client = AsyncOpenAI(
                api_key=api_key,
                base_url=settings.CHAT_BASE_URL,
            )

            self.vision_client = AsyncOpenAI(
                api_key=api_key,
                base_url=settings.VISION_BASE_URL,
            )

            self.embedding_client = AsyncOpenAI(
                api_key=api_key,
                base_url=settings.EMBEDDING_BASE_URL,
            )

            self.reranker_client = (
                AsyncOpenAI(
                    api_key=api_key,
                    base_url=settings.RERANKER_BASE_URL,
                )
                if settings.RERANKER_BASE_URL
                else None
            )

    async def chat(
        self,
        messages: list[ChatMessage],
        *,
        model: str | None = None,
        temperature: float | None = None,
    ) -> AIResponse:
        model_name = model or self.settings.LLM_MODEL
        try:
            response = await self.chat_client.chat.completions.create(
                model=model_name,
                messages=[message.model_dump() for message in messages],
                temperature=temperature,
                extra_body={
                    "chat_template_kwargs": {
                        "enable_thinking": False
                    }
                }
            )
            choice = response.choices[0].message
            return AIResponse(
                text=choice.content or "",
                model=response.model or model_name,
                provider=self.provider_name,
                raw=response.model_dump(),
                usage=self._usage(response),
            )
        except Exception:
            logger.exception("OpenAI-compatible chat request failed")
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
        try:
            response = await self.chat_client.chat.completions.create(
                model=model_name,
                messages=[message.model_dump() for message in messages],
                tools=tools,
                temperature=temperature,
            )
            choice = response.choices[0].message
            return AIResponse(
                text=choice.content or "",
                model=response.model or model_name,
                provider=self.provider_name,
                tool_calls=self._tool_calls(choice),
                raw=response.model_dump(),
                usage=self._usage(response),
            )
        except Exception:
            logger.exception("OpenAI-compatible tool chat request failed")
            raise

    async def embed(
        self,
        text: str,
        *,
        model: str | None = None,
    ) -> EmbeddingResponse:
        model_name = model or self.settings.LLM_EMBEDDING_MODEL or self.settings.LLM_MODEL
        try:
            response = await self.embedding_client.embeddings.create(
                model=model_name,
                input=text,
            )
            return EmbeddingResponse(
                embedding=response.data[0].embedding,
                model=response.model or model_name,
                provider=self.provider_name,
            )
        except Exception:
            logger.exception("OpenAI-compatible embedding request failed")
            raise

    async def analyze_image(
        self,
        image_path: str,
        prompt: str,
        *,
        model: str | None = None,
    ) -> ImageAnalysis:
        model_name = model or self.settings.LLM_VISION_MODEL or self.settings.LLM_MODEL
        path = Path(image_path)
        data_url = self._image_data_url(path)
        try:
            response = await self.vision_client.chat.completions.create(
                model=model_name,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": data_url},
                            },
                        ],
                    }
                ],
            )
            text = response.choices[0].message.content or ""
            return self._image_analysis_from_text(text)
        except Exception:
            logger.exception("OpenAI-compatible image analysis request failed")
            raise

    @staticmethod
    def _image_data_url(path: Path) -> str:
        suffix = path.suffix.lower().lstrip(".") or "jpeg"
        mime = "jpeg" if suffix == "jpg" else suffix
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        return f"data:image/{mime};base64,{encoded}"

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
    def _tool_calls(message: Any) -> list[ToolCall]:
        calls = []
        for tool_call in message.tool_calls or []:
            function = tool_call.function
            try:
                arguments = json.loads(function.arguments or "{}")
            except json.JSONDecodeError:
                arguments = {"raw_arguments": function.arguments}
            calls.append(
                ToolCall(
                    id=tool_call.id,
                    name=function.name,
                    arguments=arguments,
                )
            )
        return calls

    @staticmethod
    def _usage(response: Any) -> AIUsage | None:
        usage = getattr(response, "usage", None)
        if not usage:
            return None
        return AIUsage(
            prompt_tokens=getattr(usage, "prompt_tokens", None),
            completion_tokens=getattr(usage, "completion_tokens", None),
            total_tokens=getattr(usage, "total_tokens", None),
        )
