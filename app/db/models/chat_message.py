import uuid

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    ForeignKey
)

from datetime import datetime

from app.db.base import Base


class ChatMessage(Base):

    __tablename__ = "chat_messages"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    session_id = Column(
        String,
        ForeignKey("analysis_sessions.session_id")
    )

    role = Column(String(20))

    content = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )