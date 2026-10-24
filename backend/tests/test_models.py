from app.db.session import Base, engine, SessionLocal
from app.models.user import User
from app.models.debate_session import DebateSession
from app.core.security import hash_password

def test_models_create_and_link():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    u = User(email="t@example.com", password_hash=hash_password("secret123"))
    db.add(u); db.commit(); db.refresh(u)
    s = DebateSession(user_id=u.id, topic="Is free will real?", context="intro")
    db.add(s); db.commit(); db.refresh(s)
    assert s.id > 0 and s.user_id == u.id
    db.close()
