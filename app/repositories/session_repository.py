from app.db.database import SessionLocal
from app.db.models.analysis_session import AnalysisSession


class SessionRepository:

    def create(self, analysis, image_path):

        db = SessionLocal()

        try:

            session = AnalysisSession(
                equipment=analysis["equipment"],
                issue=analysis["issue"],
                severity=analysis["severity"],
                confidence=analysis["confidence"],
                image_path=image_path
            )

            db.add(session)
            db.commit()
            db.refresh(session)

            return session

        finally:
            db.close()

    def get_all(self):

        db = SessionLocal()

        try:

            return (
                db.query(AnalysisSession)
                .order_by(
                    AnalysisSession.created_at.desc()
                )
                .all()
            )

        finally:
            db.close()

    def get_by_id(self, session_id):

        db = SessionLocal()

        try:

            return (
                db.query(AnalysisSession)
                .filter(
                    AnalysisSession.session_id == session_id
                )
                .first()
            )

        finally:
            db.close()

    def update_status(self, session_id: str, status: str):
        db = SessionLocal()

        try:
            session = (
                db.query(AnalysisSession)
                .filter(
                    AnalysisSession.session_id == session_id
                )
                .first()
            )

            if not session:
                return None

            session.status = status

            db.commit()
            db.refresh(session)

            return session

        finally:
            db.close()
            
session_repository = SessionRepository()