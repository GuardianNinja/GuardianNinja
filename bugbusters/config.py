from dataclasses import dataclass

@dataclass
class Config:
    child_safe: bool = True
    retreat_on_presence: bool = True
    max_ticks: int = 200
    evidence_minimization: bool = True  # no cameras/audio, telemetry only
    room_activation_consent: bool = True
