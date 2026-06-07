
from google import genai

from app.core.config import settings
from app.services.context_service import context_service
from app.services.chat_memory_service import chat_memory_service
from app.services.quick_response_service import quick_response_service
from app.repositories.message_repository import message_repository
from app.services.rag_service import rag_service
from app.repositories.session_repository import session_repository

class ChatService:

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    def generate_response(self, user_message: str):

        session_id = context_service.get_session_id()
 
        quick_reply  = quick_response_service.get_response(
            user_message
        )

        if quick_reply :
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

            return quick_reply
    
        # ---------- Analysis Context ----------
        analysis = context_service.get_analysis()

        if not analysis:
            return (
                "No equipment analysis is currently available.\n\n"
                "Please upload an equipment image first or provide "
                "equipment details and the issue you are facing."
            )

        context = f"""
            Equipment: {analysis.get('equipment', 'Unknown')}
            Issue: {analysis.get('issue', 'Unknown')}
            Severity: {analysis.get('severity', 'Unknown')}
            Root Cause: {analysis.get('root_cause', 'Unknown')}
            Recommended Action: {analysis.get('recommended_action', 'Unknown')}
            Safety Warning: {analysis.get('safety_warning', 'Unknown')}
            """

        # ---------- Conversation History ----------
        history = chat_memory_service.get_history()

        rag_context = rag_service.retrieve(
                user_message
        )
        
        conversation = "\n".join(
            [
                f"{msg['role']}: {msg['content']}"
                for msg in history
            ]
        )

        prompt = f"""
        You are an expert field service engineer.

        Current Equipment Analysis:
        {context}

        Conversation History:
        {conversation}

        Knowledge Base Context:
        {rag_context}

        Latest User Message:
        {user_message}

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

        try:

            response = self.client.models.generate_content(
                model="gemini-3.1-flash-lite",
                contents=prompt
            )

            answer = response.text

            # Save conversation
            chat_memory_service.add("user", user_message)
            chat_memory_service.add("assistant", answer)
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
            return answer

        except Exception as e:

            error = str(e)

            print(f"Gemini Chat Error: {error}")

            if "429" in error:
                return (
                    "⚠ AI rate limit reached. "
                    "Please try again in a minute."
                )

            if "503" in error:
                return (
                    "⚠ AI service is currently busy. "
                    "Please retry in a few moments."
                )

            return (
                "⚠ Unable to generate a response right now."
            )