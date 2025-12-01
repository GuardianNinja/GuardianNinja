from dataclasses import dataclass, field
from typing import Dict, List, Tuple
import random

@dataclass
class Bot:
    id: int
    room: str
    health: float = 1.0

@dataclass
class Swarm:
    bots: List[Bot] = field(default_factory=list)
    exits: Dict[str, Tuple[int, int]] = field(default_factory=dict)

    def step(self, house_map: Dict[str, Dict], occupancy_check) -> Dict[str, int]:
        """
        One simulation tick. Bots avoid occupied rooms and move toward exits.
        Returns a per-room coverage count.
        """
        coverage = {room: 0 for room in house_map.keys()}
        for bot in self.bots:
            coverage[bot.room] += 1

            # Simple redundancy/self-healing: if bot health low, rest/regroup
            if bot.health < 0.5:
                bot.health = min(1.0, bot.health + 0.1)
                continue

            # Avoid occupied rooms when child-safe
            if occupancy_check(bot.room):
                # Retreat to adjacent non-occupied room if possible
                neighbors = house_map[bot.room].get("neighbors", [])
                random.shuffle(neighbors)
                moved = False
                for n in neighbors:
                    if not occupancy_check(n):
                        bot.room = n
                        moved = True
                        break
                if not moved:
                    # Hold position (safety first)
                    continue
            else:
                # Move toward exit (herding logic)
                neighbors = house_map[bot.room].get("neighbors", [])
                if neighbors:
                    bot.room = random.choice(neighbors)

            # Minor wear & tear
            bot.health = max(0.0, bot.health - 0.01)

        return coverage

    def all_outside(self, outside_room: str = "outside") -> bool:
        return all(bot.room == outside_room for bot in self.bots)
