from google import genai

from app.core.config import settings
from app.services.context_service import context_service
from app.services.chat_memory_service import chat_memory_service


class ChatService:

    def __init__(self):
        self.client = genai.Client(
            api_key=settings.GEMINI_API_KEY
        )

    def generate_response(self, user_message: str):

        # ---------- Quick responses ----------
        msg = user_message.lower().strip()

        if msg in ["hi", "hello", "hey"]:
            return "Hello. How can I assist you today?"

        if "thank" in msg:
            return "You're welcome. Let me know if you need any further assistance."

        if msg in ["ok", "okay", "yes", "yep"]:
            return "Understood. Do you need help with anything else?"
        
        if msg in ["no", "nope", "nah"]:
            return "Understood. If you need assistance later, feel free to ask."

        if msg in ["ok", "okay"]:
            return "Understood. Do you need any further assistance?"

        if msg in ["thanks", "thank you"]:
            return "You're welcome. Let me know if you need anything else."

        if msg in [
            "done",
            "fixed",
            "resolved",
            "working fine now",
            "it's done",
            "its done"
        ]:
            return (
                "Great. Perform a final functionality test and monitor "
                "the equipment for a short period to ensure the issue "
                "is fully resolved."
            )

        if any(word in msg for word in ["done", "fixed", "resolved", "working"]):
            return (
                "Great. Perform a final verification test and monitor the equipment "
                "for a short period to ensure the issue is fully resolved."
            )
        
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

        Latest User Message:
        {user_message}

        Instructions:

        - Continue the conversation naturally.
        - Use the equipment analysis when relevant.
        - Do not repeat the same recommendation unnecessarily.
        - If the user says the issue is fixed, acknowledge it.
        - If the user asks for tools, provide tools.
        - If the user asks for troubleshooting, provide step-by-step guidance.
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