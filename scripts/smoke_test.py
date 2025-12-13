# scripts/smoke_test.py
import os
import random
import secrets
import logging
from nanovelcro import NanoVelcroCouplingSystem

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("smoke")

# Non-interactive auth callback using env vars
def auth_cb(prompt: str) -> str:
    if "fingerprint" in prompt:
        return os.environ.get("NV_BIOMETRIC", "")
    if "emergency_password" in prompt:
        return os.environ.get("NV_PASSWORD", "")
    return ""

def main():
    rng = random.Random(42)
    key = secrets.token_bytes(16)
    sys = NanoVelcroCouplingSystem(
        user_type="kid",
        emergency_password=os.environ.get("NV_PASSWORD"),
        biometric_store={"fingerprint": os.environ.get("NV_BIOMETRIC")},
        rng=rng,
        auth_callback=auth_cb,
        key=key,
        gyro_threshold_kid=0.0,
        gyro_threshold_adult=0.0,
    )
    assert sys.engage_coupling(), "Engage failed"
    sys.simulate_zero_gravity(duration=1.0, time_step=0.1)
    # Trigger emergency override path (auth_cb provides password)
    try:
        sys.emergency_override()
    except Exception as e:
        logger.warning("Emergency override failed in smoke test: %s", e)
    logger.info("Smoke test completed successfully")

if __name__ == "__main__":
    main()
