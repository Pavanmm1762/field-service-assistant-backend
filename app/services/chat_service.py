import asyncio
import logging

from app.repositories.message_repository import message_repository
from app.repositories.session_repository import session_repository
from app.services.ai.factory import get_ai_service
from app.services.ai.interfaces import ChatMessage
from app.services.chat_memory_service import chat_memory_service
from app.services.context_service import context_service
from app.services.quick_response_service import quick_response_service
from app.services.rag_service import rag_service
from app.utils.equipment_normalizer import EquipmentNormalizer

logger = logging.getLogger(__name__)


class ChatService:
    def generate_response(self, user_message: str):
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(self.generate_response_async(user_message))
        raise RuntimeError("Use generate_response_async() inside an async context.")

    async def generate_response_async(self, user_message: str):
        session_id = context_service.get_session_id()

        quick_reply = quick_response_service.get_response(user_message)

        if quick_reply:
            if (
                session_id
                and user_message.lower().strip()
                in [
                    "done",
                    "fixed",
                    "resolved",
                    "working fine now",
                    "it's done",
                    "its done"
                ]
            ):
                session_repository.update_status(
                    session_id,
                    "Resolved"
                )
            chat_memory_service.add(
                "user",
                user_message

            )

            chat_memory_service.add(
                "assistant",
                quick_reply
            )

            if session_id:
                message_repository.create(
                    session_id,
                    "user",
                    user_message
                )
                message_repository.create(
                    session_id,
                    "assistant",
                    quick_reply
                )

            return {"message": quick_reply, "sources": []}

        analysis = (
            context_service.get_analysis()
        )

        rag_context = ""
        sources = []
        equipment = None

        if analysis:
            equipment = (
                EquipmentNormalizer.normalize(
                    analysis.get(
                        "equipment"
                    )
                )
            )
            logger.info(
                "Equipment identified from analysis: %s",
                equipment,
            )
        
        # If equipment is not identified from analysis, try to detect it from user message
        if not equipment:
            equipment = (
                EquipmentNormalizer.detect_from_text(
                    user_message
                )
            )
            logger.info(
                "Equipment detected from user message: %s",
                equipment,
            )

        if not equipment:
            equipment = (
                chat_memory_service.get_last_equipment()
            )

            logger.info(
                "Equipment from chat memory: %s",
                equipment,
            )

        if equipment:
            rag_result  = (
                await rag_service.retrieve_async(
                    question=user_message,  
                    equipment=equipment,
                )
            )
            rag_context = rag_result["context"]
            sources = rag_result["sources"]

        if not equipment and not analysis:
            rag_context = ""
            sources = []

        if not analysis and not rag_context and not equipment:
            return {
                "message": (
                    "Please upload an equipment image "
                    "or provide equipment details."
                ),
                "sources": [],
            }
        
        history = chat_memory_service.get_history()

        conversation = "\n".join(
            [
                f"{msg['role']}: {msg['content']}"
                for msg in history
            ]
        )
 
        prompt_sections = [
            "You are an expert field service engineer."
        ]

        if analysis:
            prompt_sections.append(
                f"""
                Current Equipment Analysis:

                Equipment: {analysis.get('equipment')}
                Issue: {analysis.get('issue')}
                Severity: {analysis.get('severity')}
                Root Cause: {analysis.get('root_cause')}
                Recommended Action: {analysis.get('recommended_action')}
                Safety Warning: {analysis.get('safety_warning')}
                """
            )

        if conversation:
            prompt_sections.append(
                f"""
                Conversation History:

                {conversation}
                """
            )

        if rag_context:

            prompt_sections.append(
                f"""
                Knowledge Base Context:

                {rag_context}
                
                Sources:
                {sources}
                """
            )
        

        prompt_sections.append(
            f"""
            Latest User Message:

            {user_message}
            """
        )

        prompt_sections.append(
            """
            Instructions:

            - Continue the conversation naturally.
            - Use the equipment analysis when relevant.
            - Use the Knowledge Base Context first when it contains relevant information.
            - If the answer exists in the retrieved manual content, prioritize that answer.
            - Do not invent manual procedures that are not present in the retrieved context.
            - Do not repeat the same recommendation unnecessarily.
            - Troubleshoot interactively.
            - Ask for one or two diagnostic observations at a time.
            - Do not provide long troubleshooting checklists unless explicitly requested.
            - Gather information step-by-step before concluding the root cause.
            - If no clear fault is identified, do not provide repair steps.
            - Ask the user for the specific problem or symptoms.
            - Do not assume equipment is faulty.
            - If the user says the issue is fixed, acknowledge it.
            - If the user asks for tools, provide tools.
            - If the user asks for troubleshooting, provide step-by-step guidance.
            - Assume the user is the technician unless explicitly stated otherwise.
            - Do not repeatedly recommend calling an electrician, landlord, facility manager, or technician.
            - Provide technician-level guidance.
            - Escalation should only be recommended when the repair exceeds the detected issue or presents unacceptable risk.
            - Keep responses concise.
            - Maximum 150 words.
            - Focus on technician-level support.
            """
        )

        prompt = "\n".join(prompt_sections)

        try:
            response = await get_ai_service().chat(
                [
                    ChatMessage(
                        role="user",
                        content=prompt
                    )
                ]
            )

            answer = response.text

            chat_memory_service.add(
                role="user",
                content=user_message,
                equipment=equipment,
            )
            chat_memory_service.add(
                role="assistant",
                content=answer
            )
            if session_id:
                message_repository.create(
                    session_id=session_id,
                    role="user",
                    content=user_message
                )
                message_repository.create(
                    session_id=session_id,
                    role="assistant",
                    content=answer
                )

            return {
                "message": answer,
                "sources": sources,
            }

        except Exception as exc:
            error = str(exc)
            logger.exception("AI chat failed: %s", error)

            if "429" in error:
                return (
                    "AI rate limit reached. "
                    "Please try again in a minute."
                )

            if "503" in error:
                return (
                    "AI service is currently busy. "
                    "Please retry in a few moments."
                )

            return "Unable to generate a response right now."
