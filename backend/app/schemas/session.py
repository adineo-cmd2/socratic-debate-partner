from pydantic import BaseModel


class StartIn(BaseModel):
    topic: str
    context: str | None = ""


class RespondIn(BaseModel):
    session_id: int
    message: str


class FallacyOut(BaseModel):
    fallacy_type: str
    snippet: str
    confidence: float
