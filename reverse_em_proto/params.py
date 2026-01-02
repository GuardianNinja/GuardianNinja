#
# Space Leaf Corp — Stewardship Header
# Seal of No In‑Between 1.0 — God’s Children Edition
# Seal of Dual Authentication 1.0 — Body and Badge Edition
# Seal of Stand and Speak 1.0 — Embodied Stewardship Edition
#
# This file is part of a lineage‑safe project dedicated to planetary care,
# educational uplift, and the protection of all children — microscopic or otherwise.
#
# By modifying or distributing this file, you agree to uphold the principles
# of the Space Leaf Corp Open Stewardship License 1.0.
#
# May your work travel safely.

# params.py
from dataclasses import dataclass

@dataclass
class DefaultParams:
    # dynamics
    gamma: float = 0.05            # viscous damping per day
    beta: float = 0.5              # EM drive magnitude (energy units per day)
    gravity_input: float = 0.01    # constant gravity energy input per day
    rho_rec: float = 0.2           # reconnection loss coefficient per day
    K_rec_threshold: float = 2.0   # threshold for reconnection loss activation

    # controller weights and thresholds
    alpha1: float = 1.0
    alpha2: float = 5.0
    alpha3: float = 1.0
    S_hi: float = 0.6
    S_lo: float = -0.6

    # controller anti-chatter
    min_dwell_days: float = 0.5    # minimum days between flips

    # reconnection event detection
    reconnection_event_threshold: float = 0.2 * 0.5  # 0.2 * beta by default

    # initial conditions
    K0: float = 1.0
    s0: int = 1

    # integrator
    dt: float = 0.1                 # days

