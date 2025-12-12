import json
import time
from pathlib import Path
from typing import Optional, Dict, Any

from .exceptions import ConsentError, BoundaryViolation, AmbiguousContextError


class ConsentToken:
    """
    Explicit, revocable consent tied to:
      - actor_id (who acts)
      - subject_id (who is acted upon)
      - action (e.g., 'touch')
      - zone (e.g., 'handshake')
      - expires_at (epoch seconds)
    """

    def __init__(self, actor_id: str, subject_id: str, action: str, zone: str, ttl_seconds: int):
        self.actor_id = actor_id
        self.subject_id = subject_id
        self.action = action
        self.zone = zone
        self.issued_at = int(time.time())
        self.expires_at = self.issued_at + ttl_seconds
        self.revoked = False

    def revoke(self):
        self.revoked = True

    def is_valid(self) -> bool:
        return (not self.revoked) and (time.time() <= self.expires_at)


class RespectGuard:
    """
    Enforces 'Scroll of Universal Respect 1.0' using a default-deny policy.

    - Private zones: deny outright.
    - Sensitive zones: require explicit consent (valid ConsentToken).
    - Neutral zones: allow with safe context.
    """

    def __init__(self, policy_path: Optional[str] = None, policy: Optional[Dict[str, Any]] = None):
        if policy is not None:
            self.policy = policy
        else:
            path = Path(policy_path or "policy/universal-respect.policy.json")
            with path.open("r", encoding="utf-8") as f:
                self.policy = json.load(f)
        self._consent_index = {}  # key: (actor_id, subject_id, action, zone) -> ConsentToken
        self._logs = []

    # --- Consent management ---

    def grant_consent(self, actor_id: str, subject_id: str, action: str, zone: str) -> ConsentToken:
        ttl = self.policy["defaults"]["consentExpiresSeconds"]
        token = ConsentToken(actor_id, subject_id, action, zone, ttl_seconds=ttl)
        key = (actor_id, subject_id, action, zone)
        self._consent_index[key] = token
        self._log("CONSENT_GRANTED", actor_id, subject_id, action, zone, extra={"expires_at": token.expires_at})
        return token

    def revoke_consent(self, token: ConsentToken):
        token.revoke()
        self._log("CONSENT_REVOKED", token.actor_id, token.subject_id, token.action, token.zone)

    def get_consent(self, actor_id: str, subject_id: str, action: str, zone: str) -> Optional[ConsentToken]:
        return self._consent_index.get((actor_id, subject_id, action, zone))

    # --- Enforcement ---

    def enforce(self, actor_id: str, subject_id: str, action: str, zone: str, context: Optional[Dict[str, Any]] = None) -> bool:
        ctx = context or {}
        defaults = self.policy["defaults"]
        zones = self.policy["zones"]
        actions = self.policy["actions"]

        zone_class = self._classify_zone(zone, zones)
        decision = self._action_rule(action, zone_class, actions)

        if decision == "deny":
            self._log("DENY", actor_id, subject_id, action, zone, reason=f"Zone '{zone}' classified '{zone_class}'")
            raise BoundaryViolation(f"Action '{action}' on '{zone}' denied by Universal Respect policy.")

        if decision == "deny_without_explicit_consent":
            token = self.get_consent(actor_id, subject_id, action, zone)
            if not token or not token.is_valid():
                self._log("CONSENT_REQUIRED", actor_id, subject_id, action, zone)
                raise ConsentError(f"Explicit consent required for '{action}' on sensitive zone '{zone}'.")
            # consent exists and valid -> proceed

        if decision == "allow_with_context":
            if defaults["denyOnAmbiguity"] and not self._is_context_safe(ctx):
                self._log("AMBIGUOUS_CONTEXT", actor_id, subject_id, action, zone, extra={"context": ctx})
                raise AmbiguousContextError("Context insufficient: require setting, relationship, and purpose.")
            # proceed

        self._log("ALLOW", actor_id, subject_id, action, zone, extra={"decision": decision, "context": ctx})
        return True

    # --- Helpers ---

    def _classify_zone(self, zone: str, zones: Dict[str, Any]) -> str:
        z = zone.lower().strip()
        if z in zones["private"]:
            return "private"
        if z in zones["sensitive"]:
            return "sensitive"
        return "neutral"

    def _action_rule(self, action: str, zone_class: str, actions: Dict[str, Any]) -> str:
        a = action.lower().strip()
        if a not in actions:
            # Unknown actions default to deny on private/sensitive, context on neutral
            return "deny" if zone_class in {"private", "sensitive"} else "allow_with_context"
        rules = actions[a]
        if "any" in rules:
            return rules["any"]
        return rules.get(zone_class, "deny")

    def _is_context_safe(self, ctx: Dict[str, Any]) -> bool:
        """
        Minimal safe context standard:
        - setting: 'public' or 'professional' or 'family' (not 'intimate')
        - relationship: clear (e.g., 'colleague', 'friend', 'family')
        - purpose: non-intimate (e.g., 'greeting', 'assist', 'medical_pro')
        """
        setting = str(ctx.get("setting", "")).lower()
        relationship = str(ctx.get("relationship", "")).lower()
        purpose = str(ctx.get("purpose", "")).lower()

        if not setting or not relationship or not purpose:
            return False

        intimate_flags = {"intimate", "romantic", "sexual"}
        if setting in intimate_flags or purpose in intimate_flags:
            return False

        return relationship in {"colleague", "friend", "family", "stranger_supervised", "professional"}

    def _log(self, event: str, actor_id: str, subject_id: str, action: str, zone: str, reason: str = "", extra: Optional[Dict[str, Any]] = None):
        entry = {
            "ts": int(time.time()),
            "event": event,
            "actor_id": actor_id,
            "subject_id": subject_id,
            "action": action,
            "zone": zone,
            "reason": reason,
            "extra": extra or {}
        }
        self._logs.append(entry)

    def export_logs(self) -> list:
        return list(self._logs)
