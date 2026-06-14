from uuid import uuid4

from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    filename = Column(String, nullable=False)

    checksum = Column(
        String,
        nullable=False,
        unique=True
    )

    equipment = Column(String)

    file_path = Column(
        String,
        nullable=False
    )

    status = Column(
        String,
        nullable=False
    )

    chunk_count = Column(
        Integer,
        default=0
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )