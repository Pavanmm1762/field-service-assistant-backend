class ChatMemoryService:

    def __init__(self):
        self.messages = []

    def add(
        self,
        role: str,
        content: str,
        equipment: str | None = None,
    ):
        self.messages.append(
            {
                "role": role,
                "content": content,
                "equipment": equipment,
            }
        )

    def get_history(self):
        return self.messages[-10:]

    def get_last_equipment(self):

        for message in reversed(
            self.messages
        ):

            equipment = message.get(
                "equipment"
            )

            if equipment:
                return equipment

        return None

    def clear(self):
        self.messages = []


chat_memory_service = ChatMemoryService()