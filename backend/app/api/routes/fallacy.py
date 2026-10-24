from collections import Counter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.debate_session import DebateSession
from app.models.fallacy_record import FallacyRecord
from app.models.user import User

router = APIRouter()


@router.get("/fallacy-profile")
def fallacy_profile(
    db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    session_ids = [
        r[0]
        for r in db.query(DebateSession.id)
        .filter(DebateSession.user_id == user.id)
        .all()
    ]
    if not session_ids:
        return {"profile": []}
    records = (
        db.query(FallacyRecord)
        .filter(FallacyRecord.session_id.in_(session_ids))
        .order_by(FallacyRecord.id)
        .all()
    )
    counts = Counter(r.fallacy_type for r in records)
    examples: dict[str, list] = {}
    for r in records:
        lst = examples.setdefault(r.fallacy_type, [])
        if len(lst) < 3:
            lst.append(r.snippet)
    profile = [
        {"fallacy_type": t, "count": counts[t], "examples": examples[t]}
        for t in sorted(counts, key=lambda k: counts[k], reverse=True)
    ]
    return {"profile": profile}
