#!/usr/bin/env python3
"""
Deep Space Pulse Signal Processor
- Detects bursts in time-series intensity
- Estimates periodicity (e.g., ~44 min)
- Logs results in lineage-safe format
"""

import json
import math
from dataclasses import dataclass, asdict
from typing import List, Tuple, Optional

@dataclass
class Burst:
    t_unix: float          # seconds since epoch
    intensity: float       # arbitrary units
    band: str              # "radio", "xray", etc.

@dataclass
class DetectionResult:
    source_id: str
    bursts_count: int
    period_minutes: Optional[float]
    period_std_minutes: Optional[float]
    duty_cycle_sec: Optional[float]
    notes: str

def load_bursts(path: str) -> List[Burst]:
    """
    Input JSON lines, one record per burst:
    {"t_unix": 1733097600.0, "intensity": 12.3, "band": "radio"}
    """
    bursts = []
    with open(path, "r") as f:
        for line in f:
            if not line.strip():
                continue
            rec = json.loads(line)
            bursts.append(Burst(**rec))
    return bursts

def estimate_period_minutes(tstamps: List[float]) -> Tuple[Optional[float], Optional[float]]:
    """
    Estimate period using inter-burst differences and robust stats.
    Returns (mean_minutes, std_minutes) or (None, None) if insufficient data.
    """
    if len(tstamps) < 3:
        return None, None
    diffs = [ (tstamps[i+1] - tstamps[i]) for i in range(len(tstamps)-1) ]
    # Filter outliers via IQR
    diffs_sorted = sorted(diffs)
    q1 = diffs_sorted[len(diffs_sorted)//4]
    q3 = diffs_sorted[(3*len(diffs_sorted))//4]
    iqr = max(q3 - q1, 1e-6)
    lo = q1 - 1.5 * iqr
    hi = q3 + 1.5 * iqr
    diffs_filtered = [d for d in diffs if lo <= d <= hi]
    if len(diffs_filtered) == 0:
        diffs_filtered = diffs
    mean_sec = sum(diffs_filtered) / len(diffs_filtered)
    std_sec = math.sqrt(sum((d - mean_sec) ** 2 for d in diffs_filtered) / max(len(diffs_filtered) - 1, 1))
    return mean_sec / 60.0, std_sec / 60.0

def estimate_duty_cycle(bursts: List[Burst]) -> Optional[float]:
    """
    If burst windows are known, you can compute duty cycle.
    Here we approximate as a fixed 30s if given via notes or metadata.
    """
    # Placeholder: if you have duration, replace this with measured durations.
    return 30.0

def detect(source_id: str, input_path: str, output_path: str) -> DetectionResult:
    bursts = load_bursts(input_path)
    t_radio = [b.t_unix for b in bursts if b.band.lower() == "radio"]
    t_xray  = [b.t_unix for b in bursts if b.band.lower() == "xray"]
    t_all   = sorted(set(t_radio + t_xray))

    mean_min, std_min = estimate_period_minutes(t_all)
    duty_sec = estimate_duty_cycle(bursts)

    notes = []
    if mean_min is not None:
        notes.append(f"Estimated period ≈ {mean_min:.2f} min (σ ≈ {std_min:.2f} min).")
        if 43.0 <= mean_min <= 45.0:
            notes.append("Period consistent with 44-minute transient.")
    if len(t_radio) and len(t_xray):
        notes.append("Dual-band bursts detected (radio + X-ray).")
    elif len(t_radio):
        notes.append("Radio-only bursts detected.")
    elif len(t_xray):
        notes.append("X-ray-only bursts detected.")

    result = DetectionResult(
        source_id=source_id,
        bursts_count=len(t_all),
        period_minutes=mean_min,
        period_std_minutes=std_min,
        duty_cycle_sec=duty_sec,
        notes=" ".join(notes) if notes else "No periodicity estimated."
    )

    with open(output_path, "w") as f:
        json.dump(asdict(result), f, indent=2)
    return result

if __name__ == "__main__":
    # Example usage:
    # python signal_processor.py
    # (Adjust paths as needed; wrap in CLI for production.)
    res = detect(
        source_id="ASKAP J1832-0911",
        input_path="data/bursts.jsonl",
        output_path="logs/detection.json"
    )
    print(json.dumps(asdict(res), indent=2))
