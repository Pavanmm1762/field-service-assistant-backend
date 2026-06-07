from app.db.database import engine

from app.db.models.analysis_session import AnalysisSession
from app.db.models.chat_message import ChatMessage

from app.db.base import Base


def init_db():

    Base.metadata.create_all(
        bind=engine
    )