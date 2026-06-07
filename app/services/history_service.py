from pathlib import Path

from app.repositories.session_repository import (
    session_repository
)
from app.repositories.message_repository import (
    message_repository
)
from app.utils.equipment_icons import (
    get_equipment_icon          
)

class HistoryService:

    def get_sessions(self):

        sessions = session_repository.get_all()

        return [
            {
                "id": s.session_id,
                "equipment": s.equipment,
                "equipmentIcon": get_equipment_icon(
                    s.equipment
                ),
                "issue": s.issue,
                "severity": s.severity,
                "confidence": s.confidence,
                "status": s.status,
                "technician": "AI Assistant",
                "timestamp": s.created_at.isoformat()
            }
            for s in sessions
        ]

    def get_session(self, session_id):

        session = session_repository.get_by_id(
            session_id
        )

        if not session:
            return None

        messages = message_repository.get_by_session(
            session_id
        )

        filename = Path(session.image_path).name

        return {
            "id": session.session_id,
            "equipment": session.equipment,
            "equipmentIcon": get_equipment_icon(session.equipment),
            "issue": session.issue,
            "severity": session.severity,
            "confidence": session.confidence,
            "status": session.status,
            "technician": "AI Assistant",

            "timestamp": session.created_at.isoformat(),

            "rootCause": getattr(
                session,
                "root_cause",
                ""
            ),

            "recommendedAction": getattr(
                session,
                "recommended_action",
                ""
            ),

            "safetyWarning": getattr(
                session,
                "safety_warning",
                ""
            ),

            "imageUrl":  f"/uploads/{filename}",

            "conversation": [
                {
                    "id": str(index),
                    "role": m.role,
                    "content": m.content,
                    "timestamp": m.created_at.isoformat()
                }
                for index, m in enumerate(messages)
            ]
        }

history_service = HistoryService()