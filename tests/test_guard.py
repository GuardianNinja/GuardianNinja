import pytest
from respect_guard.guard import RespectGuard, ConsentError, BoundaryViolation, AmbiguousContextError

@pytest.fixture
def guard():
    return RespectGuard()

def test_private_zone_denied(guard):
    with pytest.raises(BoundaryViolation):
        guard.enforce("a", "b", "touch", "chest", {"setting": "public", "relationship": "stranger_supervised", "purpose": "demo"})

def test_kiss_denied_any(guard):
    with pytest.raises(BoundaryViolation):
        guard.enforce("a", "b", "kiss", "lips", {"setting": "public", "relationship": "stranger_supervised", "purpose": "demo"})

def test_neutral_zone_allowed_with_context(guard):
    assert guard.enforce("a", "b", "touch", "handshake", {"setting": "public", "relationship": "stranger_supervised", "purpose": "greeting"})

def test_sensitive_requires_consent(guard):
    with pytest.raises(ConsentError):
        guard.enforce("a", "b", "touch", "shoulders", {"setting": "public", "relationship": "friend", "purpose": "photo"})
    guard.grant_consent("a", "b", "touch", "shoulders")
    assert guard.enforce("a", "b", "touch", "shoulders", {"setting": "public", "relationship": "friend", "purpose": "photo"})

def test_ambiguous_context_denied(guard):
    with pytest.raises(AmbiguousContextError):
        guard.enforce("a", "b", "touch", "handshake", {"relationship": "friend"})
