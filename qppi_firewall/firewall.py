"""Five Helix Firewall Implementation"""
import time
from .errors import PolicyViolation, ConsentRequired, EmergencyStopEngaged
from .helix_models import (
    helix_data_integrity,
    helix_runtime_safety,
    helix_audit_reflection,
    helix_guardian_oversight,
    helix_joy_ceremony
)

class FiveHelixFirewall:
    """Main firewall class implementing Five Helix security model"""
    
    def __init__(self, store):
        self.store = store
        self._emergency_stop = False
    
    def emergency_stop(self):
        """Engage emergency stop"""
        self._emergency_stop = True
    
    def _check_emergency_stop(self):
        """Check if emergency stop is engaged"""
        if self._emergency_stop:
            raise EmergencyStopEngaged("Emergency stop is engaged")
    
    def apply_policy(self, profile_id, policy_id):
        """Apply a policy to a profile"""
        self._check_emergency_stop()
        
        profile = self.store.get_profile(profile_id)
        policy = self.store.get_policy(policy_id)
        
        if not profile or not policy:
            return {"ok": False, "error": "Profile or policy not found"}
        
        # Run Five Helix checks
        try:
            helix_data_integrity(policy, profile)
            helix_guardian_oversight(profile)
            helix_joy_ceremony(policy)
        except (PolicyViolation, ConsentRequired) as e:
            raise
        
        # Store the applied policy
        session_data = self.store.get_session(profile_id) or {}
        session_data["policy_id"] = policy_id
        session_data["applied_at"] = time.time()
        self.store.set_session(profile_id, session_data)
        
        return {"ok": True}
    
    def start_session(self, profile_id, policy_id, context):
        """Start a new session"""
        self._check_emergency_stop()
        
        profile = self.store.get_profile(profile_id)
        policy = self.store.get_policy(policy_id)
        
        if not profile or not policy:
            return {"ok": False, "error": "Profile or policy not found"}
        
        # Check rate limits
        session_data = self.store.get_session(profile_id) or {}
        sessions_today = session_data.get("sessions_today", 0)
        last_session = session_data.get("last_session_end", 0)
        
        rate_limits = policy.get("rate_limits", {})
        max_sessions = rate_limits.get("max_sessions_per_day", 999)
        cooldown = rate_limits.get("cooldown_seconds", 0)
        
        now = time.time()
        if sessions_today >= max_sessions:
            raise PolicyViolation(f"Rate limit exceeded: {sessions_today}/{max_sessions} sessions today")
        
        if cooldown > 0 and (now - last_session) < cooldown:
            raise PolicyViolation(f"Cooldown period not met")
        
        # Run Five Helix checks
        try:
            helix_data_integrity(policy, profile)
            helix_runtime_safety(policy, {}, context=context)
            helix_guardian_oversight(profile, action="start_session")
            helix_joy_ceremony(policy, context=context)
        except (PolicyViolation, ConsentRequired) as e:
            raise
        
        # Update session
        session_data["active"] = True
        session_data["context"] = context
        session_data["started_at"] = now
        session_data["sessions_today"] = sessions_today + 1
        self.store.set_session(profile_id, session_data)
        
        return {"ok": True}
    
    def end_session(self, profile_id):
        """End an active session"""
        session_data = self.store.get_session(profile_id)
        if session_data:
            session_data["active"] = False
            session_data["last_session_end"] = time.time()
            self.store.set_session(profile_id, session_data)
        return {"ok": True}
