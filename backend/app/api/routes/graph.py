from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.debate_session import DebateSession
from app.models.fallacy_record import FallacyRecord
from app.models.reasoning_graph import ReasoningGraph
from app.models.reasoning_message import ReasoningMessage
from app.models.user import User
from app.services.graph_builder import build_graph

router = APIRouter()


@router.get("/{sid}/graph")
def get_graph(sid: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = (
        db.query(DebateSession)
        .filter(DebateSession.id == sid, DebateSession.user_id == user.id)
        .first()
    )
    if s is None:
        raise HTTPException(status_code=404, detail="session not found")
    stored = (
        db.query(ReasoningGraph).filter(ReasoningGraph.session_id == sid).first()
    )
    if stored is not None and isinstance(stored.data, dict) and "nodes" in stored.data:
        return stored.data
    messages = (
        db.query(ReasoningMessage)
        .filter(ReasoningMessage.session_id == sid)
        .order_by(ReasoningMessage.id)
        .all()
    )
    records = db.query(FallacyRecord).filter(FallacyRecord.session_id == sid).all()
    grouped: dict[int, list] = {}
    for r in records:
        grouped.setdefault(r.message_id, []).append({"fallacy_type": r.fallacy_type})
    chain = [
        {
            "role": m.role,
            "content": m.content,
            "depth": m.depth,
            "fallacies": grouped.get(m.id, []),
        }
        for m in messages
    ]
    return build_graph(chain)
