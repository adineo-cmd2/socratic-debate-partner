from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.debate_session import DebateSession
from app.models.fallacy_record import FallacyRecord
from app.models.reasoning_graph import ReasoningGraph
from app.models.reasoning_message import ReasoningMessage
from app.models.user import User
from app.schemas.session import FallacyOut, RespondIn, StartIn
from app.services.fallacy_detector import detect_fallacies
from app.services.graph_builder import build_graph
from app.services.socratic_engine import generate_question

router = APIRouter()


def _owned_session(db: Session, sid: int, user_id: int) -> DebateSession:
    s = (
        db.query(DebateSession)
        .filter(DebateSession.id == sid, DebateSession.user_id == user_id)
        .first()
    )
    if s is None:
        raise HTTPException(status_code=404, detail="session not found")
    return s


def _fallacies_by_message(db: Session, session_id: int) -> dict:
    records = (
        db.query(FallacyRecord).filter(FallacyRecord.session_id == session_id).all()
    )
    grouped: dict[int, list] = {}
    for r in records:
        grouped.setdefault(r.message_id, []).append(
            {
                "fallacy_type": r.fallacy_type,
                "snippet": r.snippet,
                "confidence": r.confidence,
            }
        )
    return grouped


def _upsert_graph(db: Session, session_id: int) -> dict:
    messages = (
        db.query(ReasoningMessage)
        .filter(ReasoningMessage.session_id == session_id)
        .order_by(ReasoningMessage.id)
        .all()
    )
    grouped = _fallacies_by_message(db, session_id)
    chain = [
        {
            "role": m.role,
            "content": m.content,
            "depth": m.depth,
            "fallacies": grouped.get(m.id, []),
        }
        for m in messages
    ]
    data = build_graph(chain)
    existing = (
        db.query(ReasoningGraph)
        .filter(ReasoningGraph.session_id == session_id)
        .first()
    )
    if existing is None:
        db.add(ReasoningGraph(session_id=session_id, data=data))
    else:
        existing.data = data
    db.commit()
    return data


@router.post("/start")
def start(body: StartIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = DebateSession(user_id=user.id, topic=body.topic, context=body.context or "")
    db.add(s)
    db.commit()
    db.refresh(s)
    return {"session_id": s.id}


@router.post("/respond")
def respond(
    body: RespondIn, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    s = _owned_session(db, body.session_id, user.id)
    count = (
        db.query(ReasoningMessage)
        .filter(ReasoningMessage.session_id == s.id)
        .count()
    )
    user_depth = count + 1
    user_msg = ReasoningMessage(
        session_id=s.id, role="user", content=body.message, depth=user_depth
    )
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    found = detect_fallacies(body.message)
    for f in found:
        db.add(
            FallacyRecord(
                session_id=s.id,
                message_id=user_msg.id,
                fallacy_type=f["fallacy_type"],
                snippet=f["snippet"],
                confidence=f["confidence"],
            )
        )
    db.commit()

    history_rows = (
        db.query(ReasoningMessage)
        .filter(ReasoningMessage.session_id == s.id)
        .order_by(ReasoningMessage.id)
        .all()
    )
    history = [{"role": m.role, "content": m.content} for m in history_rows]
    question = generate_question(history, found, s.topic)

    ai_msg = ReasoningMessage(
        session_id=s.id, role="ai", content=question, depth=user_depth + 1
    )
    db.add(ai_msg)
    db.commit()

    _upsert_graph(db, s.id)
    return {
        "ai_question": question,
        "detected_fallacies": [FallacyOut(**f).model_dump() for f in found],
    }


@router.get("/{sid}/chain")
def chain(sid: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    s = _owned_session(db, sid, user.id)
    messages = (
        db.query(ReasoningMessage)
        .filter(ReasoningMessage.session_id == s.id)
        .order_by(ReasoningMessage.id)
        .all()
    )
    grouped = _fallacies_by_message(db, s.id)
    return {
        "session_id": s.id,
        "topic": s.topic,
        "chain": [
            {
                "id": m.id,
                "role": m.role,
                "content": m.content,
                "fallacies": grouped.get(m.id, []),
            }
            for m in messages
        ],
    }
