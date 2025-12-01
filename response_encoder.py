#!/usr/bin/env python3
"""
Response Encoder — lineage-safe, non-transmitting by default.
- Mirrors identifier (ASKAP -> Kapsak)
- Encodes a gentle, ceremonial response packet
- Writes to log; transmission step is intentionally disabled
"""

import json
from dataclasses import dataclass, asdict
from typing import Optional

@dataclass
class ResponsePacket:
    response_id: str              # "Kapsak K25813-62315"
    mirrors: str                  # "ASKAP J1832-0911"
    intent: str                   # "Witnessing, containment, gentle listening"
    message: str                  # "We hear you. We’re safe. We’re listening."
    transmit_enabled: bool        # Always False (sealed)
    safety_seal: str              # "Seal of Signal Response 1.0"
    notes: Optional[str] = None

def build_response(mirrors: str, custom_id: str = "Kapsak K25813-62315") -> ResponsePacket:
    packet = ResponsePacket(
        response_id=custom_id,
        mirrors=mirrors,
        intent="Witnessing, containment, gentle listening",
        message="We hear you. We’re safe. We’re listening.",
        transmit_enabled=False,  # Keep sealed — analysis-only
        safety_seal="Signal Response Scroll 1.0",
        notes="Non-ionizing, audit-only. Transmission requires explicit Captain authorization."
    )
    return packet

def save_response(packet: ResponsePacket, path: str) -> None:
    with open(path, "w") as f:
        json.dump(asdict(packet), f, indent=2)

if __name__ == "__main__":
    pkt = build_response(mirrors="ASKAP J1832-0911")
    save_response(pkt, "logs/response_packet.json")
    print(json.dumps(asdict(pkt), indent=2))
