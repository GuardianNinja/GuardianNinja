import time
import pytest
from qppi_firewall.storage import InMemoryStore
from qppi_firewall.firewall import FiveHelixFirewall
from qppi_firewall.errors import PolicyViolation, ConsentRequired, EmergencyStopEngaged

def policy():
    return {
        "non_weapon": True,
        "digital_only": True,
        "contexts": ["Learning", "Play", "Baseline"],
        "rate_limits": {"max_sessions_per_day": 1, "cooldown_seconds": 0},
        "capabilities": ["cap_messaging"],
        "ux_constraints": {
            "no_jumpscare": True,
            "calm_transitions": True,
            "max_brightness": 0.7,
            "max_volume": 0.6,
            "joy_balance_timer_seconds": 300
        }
    }

def test_apply_and_start_session():
    store = InMemoryStore(secret_key=b"key")
    fw = FiveHelixFirewall(store)
    store.set_profile("child", {"consent": {"active": True, "paused": False}})
    store.set_policy("min", policy())
    assert fw.apply_policy("child", "min")["ok"]
    assert fw.start_session("child", "min", "Learning")["ok"]
    assert fw.end_session("child")["ok"]

def test_emergency_stop_blocks_actions():
    store = InMemoryStore(secret_key=b"key")
    fw = FiveHelixFirewall(store)
    store.set_profile("child", {"consent": {"active": True, "paused": False}})
    store.set_policy("min", policy())
    fw.emergency_stop()
    with pytest.raises(EmergencyStopEngaged):
        fw.apply_policy("child", "min")

def test_rate_limit_blocks_second_session():
    store = InMemoryStore(secret_key=b"key")
    fw = FiveHelixFirewall(store)
    store.set_profile("child", {"consent": {"active": True, "paused": False}})
    store.set_policy("min", policy())
    fw.apply_policy("child", "min")
    fw.start_session("child", "min", "Learning")
    fw.end_session("child")
    with pytest.raises(PolicyViolation):
        fw.start_session("child", "min", "Play")
