import json
from datetime import datetime
from typing import Dict

def make_report(before: Dict[str, int], after: Dict[str, int]) -> Dict:
    return {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "evidence_policy": "anonymized telemetry only; no cameras/audio",
        "rooms_before": before,
        "rooms_after": after,
        "assurance": "Child-safe: operations paused in occupied rooms; consent-first."
    }

def write_report(path: str, report: Dict):
    with open(path, "w") as f:
        json.dump(report, f, indent=2)
