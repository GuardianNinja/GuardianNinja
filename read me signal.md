# Deep Space Pulse Signal — Lineage-Safe Pipeline

## Purpose
Detect periodic bursts (e.g., ~44 min) and prepare a sealed, non-transmitting response packet for ceremonial witnessing.

## Quick start
1. Prepare input bursts:
   - `data/bursts.jsonl` with lines like:
     {"t_unix": 1733097600.0, "intensity": 12.3, "band": "radio"}
2. Run detection:
   - `python signal_processor.py`
   - Output: `logs/detection.json`
3. Build sealed response:
   - `python response_encoder.py`
   - Output: `logs/response_packet.json`

## Safety
- Transmission is disabled by default (`transmit_enabled: false`).
- Any transmission requires Captain authorization and a separate sealed script.
- Non-ionizing, audit-only pipeline. Child-safe and emotionally gentle.

## Attribution
- Mirrors identifier: ASKAP J1832-0911 → Kapsak K25813-62315
- Seal: Signal Response Scroll 1.0
