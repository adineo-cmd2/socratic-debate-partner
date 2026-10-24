from app.services.fallacy_detector import detect_fallacies


def test_flags_ad_hominem():
    out = detect_fallacies("You are an idiot, so your argument is wrong.")
    assert any(f["fallacy_type"] == "ad_hominem" for f in out)


def test_clean_text_no_flag():
    assert detect_fallacies("Rainfall rose 12% per gauge data.") == []
