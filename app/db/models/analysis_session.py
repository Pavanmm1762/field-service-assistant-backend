import uuid

from sqlalchemy import (
    Column,
    String,
    Integer,
    Text,
    DateTime
)

from datetime import datetime

from app.db.base import Base


class AnalysisSession(Base):

    __tablename__ = "analysis_sessions"

    session_id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    equipment = Column(String(255))
    issue = Column(Text)
    severity = Column(String(50))
    confidence = Column(Integer)

    image_path = Column(Text)

    status = Column(
        String(50),
        default="Open"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )