import asyncio

from app.services.ai.factory import get_ai_service


class EmbeddingService:
    def embed(self, text: str):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.embed_async(text))
        raise RuntimeError("Use embed_async() inside an async context.")

    async def embed_async(self, text: str):
        response = await get_ai_service().embed(text)
        return response.embedding
