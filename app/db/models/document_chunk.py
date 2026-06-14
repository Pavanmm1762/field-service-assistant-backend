from uuid import uuid4

from pgvector.sqlalchemy import Vector

from sqlalchemy import (
    Column,
    Integer,
    Text,
    ForeignKey,
    DateTime,
)
from sqlalchemy.dialects.postgresql import (
    UUID,
    JSONB,
)
from sqlalchemy.sql import func

from app.db.base import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    document_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "documents.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    chunk_index = Column(
        Integer,
        nullable=False,
    )

    chunk_text = Column(
        Text,
        nullable=False,
    )

    embedding = Column(
        Vector(4096),
        nullable=False,
    )

    chunk_metadata = Column(
        JSONB,
        nullable=True,
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
    )