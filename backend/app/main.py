from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import analytics, fallacy, graph, sessions
from app.core.config import get_settings
from app.db.base import Base
from app.db.session import engine

import app.models.user  # noqa: F401 register tables
import app.models.debate_session  # noqa: F401
import app.models.reasoning_message  # noqa: F401
import app.models.fallacy_record  # noqa: F401
import app.models.reasoning_graph  # noqa: F401

Base.metadata.create_all(bind=engine)

settings = get_settings()

app = FastAPI(title="Socratic Debate Partner")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin, "http://127.0.0.1:4321"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/healthz")
def healthz():
    return {"ok": True}


app.include_router(sessions.router, prefix="/api/session", tags=["session"])
app.include_router(graph.router, prefix="/api/session", tags=["graph"])
app.include_router(fallacy.router, prefix="/api/user", tags=["user"])
app.include_router(analytics.router, prefix="/api/user", tags=["user"])
