"""
Quantum Ball Toy 1.0
Inspired by Cisco-style playful physics and planetary sensing.

This module defines a QuantumBallToy with:
- multiple named "modes" (states)
- a simple notion of superposition (multiple active modes)
- collapse() to choose one state
- basic event hooks for logging / teaching moments
"""

from __future__ import annotations
import random
from dataclasses import dataclass, field
from typing import List, Callable, Optional


@dataclass
class QuantumMode:
    """Represents one possible mode / state of the toy."""
    name: str
    color: str
    energy_level: int  # arbitrary teaching metric, 1–10
    description: str


@dataclass
class QuantumBallToy:
    """
    A conceptual quantum ball toy.

    This is teaching code, not physics-accurate.
    Designed to be extended for:
    - UI (CLI, web, game engine)
    - sensor inputs
    - logging to "captain's log" or similar archives
    """
    name: str = "Q-Sphere"
    modes: List[QuantumMode] = field(default_factory=list) # pyright: ignore[reportUnknownVariableType]
    superposed_indices: List[int] = field(default_factory=list) # pyright: ignore[reportUnknownVariableType]
    on_collapse: Optional[Callable[[QuantumMode], None]] = None
    on_superposition_change: Optional[Callable[[List[QuantumMode]], None]] = None

    def add_mode(self, mode: QuantumMode) -> None:
        """Add a new possible mode/state."""
        self.modes.append(mode)

    def set_superposition(self, indices: List[int]) -> None:
        """
        Set which modes are currently in 'superposition'.

        Indices refer to positions in self.modes.
        """
        if not indices:
            raise ValueError("Superposition must contain at least one mode index.")

        # ensure indices are valid
        for i in indices:
            if i < 0 or i >= len(self.modes):
                raise IndexError(f"Invalid mode index: {i}")

        self.superposed_indices = indices

        if self.on_superposition_change:
            self.on_superposition_change(self.superposed_modes)

    @property
    def superposed_modes(self) -> List[QuantumMode]:
        """Return the current superposed modes."""
        return [self.modes[i] for i in self.superposed_indices]

    def collapse(self, strategy: str = "random") -> QuantumMode:
        """
        Collapse the superposition into a single mode.

        strategy:
        - "random": equal probability
        - "energy_weighted": weight by energy_level
        """
        if not self.superposed_indices:
            raise RuntimeError("No superposed modes set; cannot collapse.")

        if strategy == "random":
            chosen_index = random.choice(self.superposed_indices)
        elif strategy == "energy_weighted":
            chosen_index = self._collapse_energy_weighted()
        else:
            raise ValueError(f"Unknown collapse strategy: {strategy}")

        chosen_mode = self.modes[chosen_index]

        # After collapse, we can consider the toy to be in a single-mode state
        self.superposed_indices = [chosen_index]

        if self.on_collapse:
            self.on_collapse(chosen_mode)

        return chosen_mode

    def _collapse_energy_weighted(self) -> int:
        """Internal helper to pick based on energy_level weights."""
        weights = [self.modes[i].energy_level for i in self.superposed_indices]
        total = sum(weights)
        if total <= 0:
            # fallback to random if all energy levels are zero
            return random.choice(self.superposed_indices)

        r = random.uniform(0, total)
        cumulative = 0.0
        for idx, w in zip(self.superposed_indices, weights):
            cumulative += w
            if r <= cumulative:
                return idx

        # numeric safety fallback
        return self.superposed_indices[-1]


def default_quantum_ball() -> QuantumBallToy:
    """
    Factory to build a 'Cisco-flavored' default toy
    with a few playful modes.
    """
    toy = QuantumBallToy(name="Planck Punk")

    toy.add_mode(QuantumMode(
        name="Quantum Bop",
        color="electric blue",
        energy_level=7,
        description="Rhythmic bouncing with playful, high-energy pulses."
    ))

    toy.add_mode(QuantumMode(
        name="Schrödinger Glow",
        color="violet",
        energy_level=4,
        description="Soft, uncertain glow that flickers between possibilities."
    ))

    toy.add_mode(QuantumMode(
        name="Phase Drift",
        color="teal",
        energy_level=9,
        description="Erratic movement that feels like it glitches between positions."
    ))

    toy.add_mode(QuantumMode(
        name="Calm Ground State",
        color="warm white",
        energy_level=2,
        description="Rest mode for breath, regulation, and reset."
    ))

    return toy


if __name__ == "__main__":
    # Demo: run this file directly to see a simple text-based behavior.
    toy = default_quantum_ball()

    # Optional: attach simple logging callbacks
    def log_collapse(mode: QuantumMode) -> None:
        print(f"[COLLAPSE] Toy collapsed into: {mode.name} ({mode.color})")
        print(f"  Energy: {mode.energy_level}")
        print(f"  Description: {mode.description}")
        print()

    def log_superposition(modes: List[QuantumMode]) -> None:
        print("[SUPERPOSITION] Current possible modes:")
        for m in modes:
            print(f"  - {m.name} (energy {m.energy_level})")
        print()

    toy.on_collapse = log_collapse
    toy.on_superposition_change = log_superposition

    # Example teaching run
    print(f"Loaded toy: {toy.name}")
    print("Setting superposition to all modes...\n")
    toy.set_superposition(list(range(len(toy.modes))))

    print("Collapsing 5 times (energy-weighted):\n")
    for _ in range(5):
        toy.collapse(strategy="energy_weighted")
