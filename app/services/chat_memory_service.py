class ChatMemoryService:

    def __init__(self):
        self.messages = []

    def add(self, role: str, content: str):
        self.messages.append({
            "role": role,
            "content": content
        })

    def get_history(self):
        return self.messages[-10:]

    def clear(self):
        self.messages = []


chat_memory_service = ChatMemoryService()