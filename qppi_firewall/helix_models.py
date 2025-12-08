"""Five Helix Security Models"""
from .errors import PolicyViolation, ConsentRequired

def helix_data_integrity(policy, profile):
    """Helix 1: Data Integrity - Verify consent is active"""
    consent = profile.get("consent", {})
    if not consent.get("active", False):
        raise ConsentRequired("User consent is required")
    return True

def helix_runtime_safety(policy, runtime, context=None):
    """Helix 2: Runtime Safety - Verify context is allowed"""
    if context and context not in policy.get("contexts", []):
        raise PolicyViolation(f"Context '{context}' not allowed")
    return True

def helix_audit_reflection(policy, runtime):
    """Helix 3: Audit Reflection - Verify capabilities match policy"""
    allowed_caps = set(policy.get("capabilities", []))
    runtime_caps = set(k for k, v in runtime.items() if k.startswith("cap_") and v)
    
    if not runtime_caps.issubset(allowed_caps):
        unauthorized = runtime_caps - allowed_caps
        raise PolicyViolation(f"Unauthorized capabilities: {unauthorized}")
    return True

def helix_guardian_oversight(profile, action=None):
    """Helix 4: Guardian Oversight - Check for pause/emergency stop"""
    consent = profile.get("consent", {})
    if consent.get("paused", False):
        raise PolicyViolation("Guardian has paused access")
    return True

def helix_joy_ceremony(policy, context=None):
    """Helix 5: Joy Ceremony - Ensure UX constraints are present"""
    ux = policy.get("ux_constraints", {})
    if not ux:
        raise PolicyViolation("UX constraints required for joy ceremony")
    return True
