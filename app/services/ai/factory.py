from __future__ import annotations

import logging
from functools import lru_cache

from app.core.config import Settings, settings
from app.services.ai.ai_service import AIService
from app.services.ai.adapters.gemini import GeminiAdapter
from app.services.ai.adapters.openai_compatible import OpenAICompatibleAdapter
from app.services.ai.interfaces import AIProvider

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_ai_service() -> AIService:
    return build_ai_service(settings)


def build_ai_service(app_settings: Settings) -> AIService:
    provider = app_settings.LLM_PROVIDER.lower()

    if provider == AIProvider.GEMINI.value:
        adapter = GeminiAdapter(app_settings)
    elif provider == AIProvider.OPENAI_COMPATIBLE.value:
        adapter = OpenAICompatibleAdapter(app_settings)
    else:
        supported = ", ".join(provider.value for provider in AIProvider)
        raise ValueError(
            f"Unsupported LLM_PROVIDER '{app_settings.LLM_PROVIDER}'. "
            f"Supported providers: {supported}"
        )

    logger.info("Initialized AI provider adapter: %s", provider)
    return AIService(adapter)
