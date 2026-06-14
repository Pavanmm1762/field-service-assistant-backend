import logging

from app.db.database import engine

from app.db.models.analysis_session import AnalysisSession
from app.db.models.chat_message import ChatMessage
from app.db.models.document import Document
from app.db.models.document_chunk import DocumentChunk

from app.db.base import Base

logger = logging.getLogger(__name__)

def init_db():
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Done")