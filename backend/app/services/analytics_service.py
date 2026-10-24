"""Progress analytics: chart-ready JSON from a list of sessions."""


def _get(session, key: str, default=None):
    if isinstance(session, dict):
        return session.get(key, default)
    return getattr(session, key, default)


def _fallacy_count(session) -> int:
    fallacies = _get(session, "fallacies", None)
    if fallacies is None:
        fallacies = _get(session, "fallacy_records", None)
    if fallacies is None:
        return int(_get(session, "fallacy_count", 0) or 0)
    if isinstance(fallacies, (int, float)):
        return int(fallacies)
    return len(list(fallacies))


def _depth(session) -> float:
    for key in ("avg_depth", "depth", "max_depth"):
        value = _get(session, key, None)
        if value is not None:
            return float(value)
    return 0.0


def compute_progress(sessions: list) -> dict:
    """Return {depth_trend, fallacy_trend, topic_breadth} for charting."""
    sessions = list(sessions or [])
    depth_trend = [_depth(s) for s in sessions]
    fallacy_trend = [_fallacy_count(s) for s in sessions]
    topics = {_get(s, "topic") for s in sessions}
    topics.discard(None)
    topics.discard("")
    return {
        "depth_trend": depth_trend,
        "fallacy_trend": fallacy_trend,
        "topic_breadth": len(topics),
    }
