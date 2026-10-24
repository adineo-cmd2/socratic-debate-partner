"""Reasoning-graph builder: message chain -> nodes/edges structure."""

_LABEL_LEN = 80
# User messages at this effective depth (explicit depth field, else position)
# with no fallacies count as supported claims.
SUPPORTED_DEPTH = 3


def _status(role: str, fallacies: list, depth: int) -> str:
    if role == "ai":
        return "open"
    if fallacies:
        return "challenged"
    if depth >= SUPPORTED_DEPTH:
        return "supported"
    return "open"


def build_graph(messages: list[dict]) -> dict:
    """Build {nodes: [{id, label, status}], edges: [{from, to}]} from a chain.

    Each message becomes one node; edges link consecutive nodes. Status:
    ai -> open; user with fallacies -> challenged; user at depth/index >= 4
    -> supported; otherwise open.
    """
    nodes = []
    for i, msg in enumerate(messages or []):
        content = str(msg.get("content", ""))
        fallacies = msg.get("fallacies") or []
        depth = msg.get("depth", i)
        nodes.append(
            {
                "id": i,
                "label": content[:_LABEL_LEN],
                "status": _status(msg.get("role", "user"), fallacies, depth),
            }
        )
    edges = [{"from": i, "to": i + 1} for i in range(len(nodes) - 1)]
    return {"nodes": nodes, "edges": edges}
