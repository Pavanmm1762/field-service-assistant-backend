import asyncio

from app.services.ai.factory import get_ai_service
from app.services.ai.interfaces import ChatMessage


async def main():
    response = await get_ai_service().chat(
        [
            ChatMessage(
                role="user",
                content="Hello",
            )
        ]
    )
    print(response.text)


asyncio.run(main())
