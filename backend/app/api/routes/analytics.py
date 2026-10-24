from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.debate_session import DebateSession
from app.models.fallacy_record import FallacyRecord
from app.models.reasoning_message import ReasoningMessage
from app.models.user import User
from app.services.analytics_service import compute_progress

router = APIRouter()


@router.get("/progress")
def progress(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    sessions = (
        db.query(DebateSession)
        .filter(DebateSession.user_id == user.id)
        .order_by(DebateSession.id)
        .all()
    )
    payload = []
    for s in sessions:
        msg_count = (
            db.query(ReasoningMessage)
            .filter(ReasoningMessage.session_id == s.id)
            .count()
        )
        fall_count = (
            db.query(FallacyRecord)
            .filter(FallacyRecord.session_id == s.id)
            .count()
        )
        payload.append(
            {"topic": s.topic, "depth": float(msg_count), "fallacy_count": fall_count}
        )
    return compute_progress(payload)
