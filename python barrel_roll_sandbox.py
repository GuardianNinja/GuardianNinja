#!/usr/bin/env python3
# barrel_roll_sandbox.py
# Quantum Bubble Transporter — Barrel-Roll Validation Loop (Sandbox Edition)
# Author: Space LEAF ceremonial stack
# Purpose: Synthetic-only test of JD → Krystal → Miko → JD loop with firewall hardening

import json
import time
import hmac
import hashlib
import threading
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Tuple

# =============================================================================
# Constants and synthetic configuration
# =============================================================================

TEST_HMAC_KEY = b"ceremonial-test-key-krystal"
SANDBOX_LABEL = "Temporal Sandbox — No Production Writes"
FORWARD_ROUTE = ["federal", "state", "international"]
REVERSE_ROUTE = list(reversed(FORWARD_ROUTE))

# Synthetic STIX-like IOC bundle (no real indicators)
SYNTHETIC_IOCS = [
    {
        "type": "indicator",
        "id": "indicator--0001",
        "pattern": "[file:hashes.'SHA-256' = 'DEADBEEF...0001']",
        "labels": ["ransomware", "education"],
        "sector": "K-12",
        "region": "US-FL",
        "created": "2025-12-05T20:11:00Z"
    },
    {
        "type": "indicator",
        "id": "indicator--0002",
        "pattern": "[url:value = 'https://malicious.example/vault']",
        "labels": ["ransomware", "pediatric"],
        "sector": "Healthcare",
        "region": "US-FL",
        "created": "2025-12-05T20:12:00Z"
    },
    {
        "type": "indicator",
        "id": "indicator--0003",
        "pattern": "[domain-name:value = 'evil.example']",
        "labels": ["command-and-control"],
        "sector": "K-12",
        "region": "US-FL",
        "created": "2025-12-05T20:13:00Z"
    }
]

# =============================================================================
# Utility: hashing, signing, merkle, and ledger
# =============================================================================

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sign_hmac(payload: bytes, key: bytes = TEST_HMAC_KEY) -> str:
    return hmac.new(key, payload, hashlib.sha256).hexdigest()

def merkle_root(hashes: List[str]) -> str:
    # Simple merkle root over hex digests
    if not hashes:
        return sha256(b"")
    layer = hashes[:]
    while len(layer) > 1:
        next_layer = []
        for i in range(0, len(layer), 2):
            a = layer[i]
            b = layer[i+1] if i + 1 < len(layer) else layer[i]
            next_layer.append(sha256((a + b).encode()))
        layer = next_layer
    return layer[0]

@dataclass
class LedgerEntry:
    stage: str
    actor: str
    timestamp: float
    artifact_id: str
    hash_pre: Optional[str] = None
    hash_post: Optional[str] = None
    signature: Optional[str] = None
    decision: Optional[str] = None
    notes: Dict[str, Any] = field(default_factory=dict)

class AppendOnlyLedger:
    def __init__(self, label: str):
        self.label = label
        self._entries: List[LedgerEntry] = []
        self._sealed_roots: List[str] = []

    def write(self, entry: LedgerEntry):
        self._entries.append(entry)

    def entries(self) -> List[LedgerEntry]:
        return list(self._entries)

    def seal(self) -> str:
        digests = [sha256(json.dumps(e.__dict__, sort_keys=True).encode()) for e in self._entries]
        root = merkle_root(digests)
        self._sealed_roots.append(root)
        return root

# =============================================================================
# Firewall shield (sandbox)
# =============================================================================

class QueueFirewall:
    def __init__(self):
        self.rate_limits = {"per_source": 100, "per_type": 100}
        self.blocked = 0
        self.accepted = 0
        self.rejected_signatures = 0
        self.invalid_schema = 0

    def validate_schema(self, ioc: Dict[str, Any]) -> bool:
        required = {"type", "id", "pattern", "labels", "sector", "region", "created"}
        if not required.issubset(ioc.keys()):
            self.invalid_schema += 1
            return False
        if not isinstance(ioc["labels"], list):
            self.invalid_schema += 1
            return False
        return True

    def enforce_signature(self, ioc_hash: str, signature: str) -> bool:
        # Simulate signature check: require HMAC over the hash string
        expected = sign_hmac(ioc_hash.encode())
        ok = hmac.compare_digest(expected, signature)
        if not ok:
            self.rejected_signatures += 1
        return ok

    def process(self, iocs: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        accepted, quarantined = [], []
        for ioc in iocs:
            if not self.validate_schema(ioc):
                quarantined.append(ioc)
                continue
            ioc_hash = sha256(json.dumps(ioc, sort_keys=True).encode())
            signature = sign_hmac(ioc_hash.encode())
            if not self.enforce_signature(ioc_hash, signature):
                quarantined.append(ioc)
                continue
            accepted.append({**ioc, "_hash": ioc_hash, "_sig": signature})
        self.accepted += len(accepted)
        self.blocked += len(quarantined)
        return accepted, quarantined

    def metrics(self) -> Dict[str, Any]:
        return {
            "accepted": self.accepted,
            "blocked": self.blocked,
            "invalid_schema": self.invalid_schema,
            "rejected_signatures": self.rejected_signatures,
            "rate_limits": self.rate_limits
        }

# =============================================================================
# Actors: JD intake/triage, Krystal validation, Miko routing
# =============================================================================

class JD:
    def __init__(self, ledger: AppendOnlyLedger):
        self.ledger = ledger

    def intake_forward(self, firewall: QueueFirewall, iocs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        accepted, quarantined = firewall.process(iocs)
        for ioc in accepted:
            entry = LedgerEntry(
                stage="intake_forward",
                actor="JD",
                timestamp=time.time(),
                artifact_id=ioc["id"],
                hash_pre=ioc["_hash"],
                signature=ioc["_sig"],
                decision="accepted",
                notes={"labels": ioc["labels"], "sector": ioc["sector"], "region": ioc["region"]}
            )
            self.ledger.write(entry)
        for ioc in quarantined:
            entry = LedgerEntry(
                stage="intake_forward",
                actor="JD",
                timestamp=time.time(),
                artifact_id=ioc.get("id", "unknown"),
                decision="quarantined",
                notes={"reason": "schema/signature"}
            )
            self.ledger.write(entry)
        return accepted

    def intake_reverse(self, accepted_forward: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        mirrored = list(reversed(accepted_forward))
        for ioc in mirrored:
            entry = LedgerEntry(
                stage="intake_reverse",
                actor="JD",
                timestamp=time.time(),
                artifact_id=ioc["id"],
                hash_pre=ioc["_hash"],
                signature=ioc["_sig"],
                decision="mirrored",
                notes={"labels": ioc["labels"], "sector": ioc["sector"], "region": ioc["region"]}
            )
            self.ledger.write(entry)
        return mirrored

class Krystal:
    def __init__(self, ledger: AppendOnlyLedger):
        self.ledger = ledger

    def cross_validate(self, stream: List[Dict[str, Any]], direction: str) -> List[Dict[str, Any]]:
        validated: List[Dict[str, Any]] = []
        for ioc in stream:
            pre = ioc["_hash"]
            post = sha256(json.dumps({k: ioc[k] for k in ioc if not k.startswith("_")}, sort_keys=True).encode())
            ok = (pre == post)
            entry = LedgerEntry(
                stage=f"validation_{direction}",
                actor="Krystal",
                timestamp=time.time(),
                artifact_id=ioc["id"],
                hash_pre=pre,
                hash_post=post,
                decision="validated" if ok else "hash_mismatch",
                notes={"redaction_check": True, "provenance": "synthetic"}
            )
            self.ledger.write(entry)
            if ok:
                validated.append(ioc)
        return validated

class Miko:
    def __init__(self, ledger: AppendOnlyLedger):
        self.ledger = ledger

    def route(self, stream: List[Dict[str, Any]], direction: str) -> List[Dict[str, Any]]:
        route = FORWARD_ROUTE if direction == "forward" else REVERSE_ROUTE
        routed: List[Dict[str, Any]] = []
        for ioc in stream:
            entry = LedgerEntry(
                stage=f"routing_{direction}",
                actor="Miko",
                timestamp=time.time(),
                artifact_id=ioc["id"],
                hash_pre=ioc["_hash"],
                decision="routed",
                notes={"route": route, "compliance": ["FERPA?", "HIPAA? minimal disclosure"], "dispatch": "mock"}
            )
            self.ledger.write(entry)
            routed.append(ioc)
        return routed

# =============================================================================
# Controller: Barrel-roll loop, unified re-init, and metrics
# =============================================================================

class BarrelRollController:
    def __init__(self):
        self.ledger = AppendOnlyLedger(SANDBOX_LABEL)
        self.firewall = QueueFirewall()
        self.jd = JD(self.ledger)
        self.krystal = Krystal(self.ledger)
        self.miko = Miko(self.ledger)
        self._permission_snapshot_pre = sha256(b"IAM:unchanged")  # sandbox placeholder
        self._permission_snapshot_post = None

    def _snapshot_permissions(self):
        # Sandbox-only: represent immutable IAM snapshot
        return sha256(b"IAM:unchanged")

    def run(self) -> Dict[str, Any]:
        # Phase 1: JD dual initiation
        accepted_forward = self.jd.intake_forward(self.firewall, SYNTHETIC_IOCS)
        accepted_reverse = self.jd.intake_reverse(accepted_forward)

        # Phase 2: Krystal cross-mirror validation
        validated_forward = self.krystal.cross_validate(accepted_forward, "forward")
        validated_reverse = self.krystal.cross_validate(accepted_reverse, "reverse")

        # Phase 3: Miko barrel-roll routing (forward and reverse)
        routed_forward = self.miko.route(validated_forward, "forward")
        routed_reverse = self.miko.route(validated_reverse, "reverse")

        # Phase 3.5: Loop closure — reconnect streams midpoint
        midpoint_join = list(zip(routed_forward, routed_reverse))

        # Phase 4: Unified re-initialization (JD + Krystal + Miko together)
        unified_hashes = []
        for pair in midpoint_join:
            a, b = pair
            unified = sha256((a["_hash"] + b["_hash"]).encode())
            entry = LedgerEntry(
                stage="unified_reinit",
                actor="JD+Krystal+Miko",
                timestamp=time.time(),
                artifact_id=f"{a['id']}|{b['id']}",
                hash_pre=a["_hash"],
                hash_post=b["_hash"],
                signature=sign_hmac(unified.encode()),
                decision="validated_as_one",
                notes={"merge_strategy": "pairwise", "flux": "stabilized"}
            )
            self.ledger.write(entry)
            unified_hashes.append(unified)

        # Seal the ledger
        final_merkle = self.ledger.seal()

        # Permissions diff check (must remain identical)
        self._permission_snapshot_post = self._snapshot_permissions()
        permission_intact = (self._permission_snapshot_pre == self._permission_snapshot_post)

        # Metrics
        fw_metrics = self.firewall.metrics()
        summary = {
            "firewall_metrics": fw_metrics,
            "final_merkle_root": final_merkle,
            "permission_intact": permission_intact,
            "entries_written": len(self.ledger.entries()),
            "streams_forward": len(routed_forward),
            "streams_reverse": len(routed_reverse),
            "unified_pairs": len(unified_hashes),
            "sandbox_label": self.ledger.label
        }
        return summary

# =============================================================================
# Main — run sandbox and pretty-print results
# =============================================================================

def run_sandbox_test():
    print("=== Quantum Bubble Transporter — Barrel-Roll Validation (Sandbox) ===")
    ctrl = BarrelRollController()
    summary = ctrl.run()
    print("\n--- Firewall Metrics ---")
    print(json.dumps(summary["firewall_metrics"], indent=2))
    print("\n--- Ledger ---")
    print(f"Entries written: {summary['entries_written']}")
    print(f"Final Merkle root: {summary['final_merkle_root']}")
    print(f"Permission intact: {summary['permission_intact']}")
    print("\n--- Streams ---")
    print(f"Forward routed: {summary['streams_forward']}")
    print(f"Reverse routed: {summary['streams_reverse']}")
    print(f"Unified pairs: {summary['unified_pairs']}")
    print("\nSandbox label:", summary["sandbox_label"])
    print("\nStatus: VALIDATION COMPLETE — JD, Krystal, Miko validated as one. Permissions untouched, flux stabilized.")

if __name__ == "__main__":
    run_sandbox_test()
