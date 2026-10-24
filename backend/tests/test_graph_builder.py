from app.services.graph_builder import build_graph


def test_chain_builds_nodes_and_edges():
    msgs = [
        {"role": "user", "content": "Free will exists.", "fallacies": []},
        {"role": "ai", "content": "What evidence supports that?"},
        {
            "role": "user",
            "content": "I feel it.",
            "fallacies": [{"fallacy_type": "emotional_reasoning"}],
        },
    ]
    g = build_graph(msgs)
    assert len(g["nodes"]) == 3 and len(g["edges"]) == 2
    assert g["nodes"][2]["status"] == "challenged"
