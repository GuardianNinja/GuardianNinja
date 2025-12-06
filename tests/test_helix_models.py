import pytest
from qppi_firewall.helix_models import (
    helix_data_integrity,
    helix_runtime_safety,
    helix_audit_reflection,
    helix_guardian_oversight,
    helix_joy_ceremony,
)
from qppi_firewall.errors import PolicyViolation, ConsentRequired

def policy_base():
    return {
        "non_weapon": True,
        "digital_only": True,
        "contexts": ["Learning", "Play", "Baseline"],
        "rate_limits": {"max_sessions_per_day": 2, "cooldown_seconds": 1},
        "capabilities": ["cap_messaging"],
        "ux_constraints": {
            "no_jumpscare": True,
            "calm_transitions": True,
            "max_brightness": 0.7,
            "max_volume": 0.6,
            "joy_balance_timer_seconds": 300
        }
    }

def profile_consent(active=True, paused=False):
    return {"consent": {"active": active, "paused": paused}}

def test_data_integrity_requires_consent():
    with pytest.raises(ConsentRequired):
        helix_data_integrity(policy_base(), profile_consent(active=False))

def test_runtime_safety_context_lock():
    with pytest.raises(PolicyViolation):
        helix_runtime_safety(policy_base(), {}, context="Unknown")

def test_audit_parity_exceeds_capabilities():
    p = policy_base()
    runtime = {"cap_secret_feature": True}
    with pytest.raises(PolicyViolation):
        helix_audit_reflection(p, runtime)

def test_guardian_pause_blocks_session():
    with pytest.raises(PolicyViolation):
        helix_guardian_oversight(profile_consent(active=True, paused=True), action="start_session")

def test_joy_requires_constraints():
    p = policy_base()
    helix_joy_ceremony(p, context="Play")  # should pass
