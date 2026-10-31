"""Security hygiene for django-ingredients tests (S3)."""

from __future__ import annotations

from pathlib import Path

FORBIDDEN_SUBSTRINGS = (
    "AKIA",
    "BEGIN RSA PRIVATE KEY",
    "BEGIN OPENSSH PRIVATE KEY",
    "xoxb-",
    "ghp_",
    "api_key=",
    "password=",
    "secret_key=",
)


def test_test_tree_has_no_secret_fingerprints():
    tests_root = Path(__file__).resolve().parent
    hygiene = Path(__file__).name
    hits: list[str] = []
    for path in tests_root.rglob("*.py"):
        if path.name == hygiene:
            continue
        lower = path.read_text(encoding="utf-8").lower()
        # settings.SECRET_KEY = "NOTASECRET" is an intentional sentinel — allow.
        if path.name == "settings.py":
            lower = lower.replace("secret_key", "")
        for needle in FORBIDDEN_SUBSTRINGS:
            if needle.lower() in lower:
                hits.append(f"{path.name}:{needle}")
    assert hits == [], f"secret-like fingerprints in tests: {hits}"


def test_urls_fixture_does_not_echo_user_input():
    """Template test urls must not ship reflected-input HttpResponse fixtures."""
    urls = Path(__file__).resolve().parent / "urls.py"
    text = urls.read_text(encoding="utf-8")
    assert "HttpResponse" not in text
    assert "mark_safe" not in text
