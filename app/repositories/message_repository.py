from app.db.database import SessionLocal
from app.db.models.chat_message import ChatMessage


class MessageRepository:

    def create(
        self,
        session_id,
        role,
        content
    ):

        db = SessionLocal()

        try:

            message = ChatMessage(
                session_id=session_id,
                role=role,
                content=content
            )

            db.add(message)
            db.commit()

        finally:
            db.close()

    def get_by_session(
        self,
        session_id
    ):

        db = SessionLocal()

        try:

            return (
                db.query(ChatMessage)
                .filter(
                    ChatMessage.session_id == session_id
                )
                .order_by(
                    ChatMessage.created_at.asc()
                )
                .all()
            )

        finally:
            db.close()


message_repository = MessageRepository()