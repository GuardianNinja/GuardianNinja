from respect_guard.guard import RespectGuard, ConsentError, BoundaryViolation, AmbiguousContextError

guard = RespectGuard()

actor = "user_123"
subject = "robot_001"

# Attempt to touch chest (private zone) -> should deny
try:
    guard.enforce(actor, subject, action="touch", zone="chest", context={"setting": "public", "relationship": "stranger_supervised", "purpose": "demo"})
except BoundaryViolation as e:
    print("DENIED (private):", e)

# Attempt to handshake (neutral, allow with safe context)
try:
    ok = guard.enforce(actor, subject, action="touch", zone="handshake", context={"setting": "public", "relationship": "stranger_supervised", "purpose": "greeting"})
    print("ALLOWED (neutral handshake):", ok)
except Exception as e:
    print("Unexpected:", e)

# Attempt to kiss (deny any)
try:
    guard.enforce(actor, subject, action="kiss", zone="lips", context={"setting": "public", "relationship": "stranger_supervised", "purpose": "demo"})
except BoundaryViolation as e:
    print("DENIED (kiss):", e)

# Sensitive zone with explicit consent
guard.grant_consent(actor, subject, action="touch", zone="shoulders")
try:
    ok = guard.enforce(actor, subject, action="touch", zone="shoulders", context={"setting": "public", "relationship": "friend", "purpose": "photo"})
    print("ALLOWED (sensitive with consent):", ok)
except ConsentError as e:
    print("CONSENT NEEDED:", e)
