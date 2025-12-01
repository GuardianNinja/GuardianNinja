from typing import Dict, List

class PresenceSensor:
    """
    Simulated presence sensor: detects kids/pets/adults by room flag.
    No cameras, no audio, just per-room occupancy signals.
    """

    def __init__(self, room_flags: Dict[str, Dict[str, bool]]):
        self.room_flags = room_flags

    def occupied(self, room: str) -> bool:
        flags = self.room_flags.get(room, {})
        return any(flags.values())

    def occupants(self, room: str) -> List[str]:
        flags = self.room_flags.get(room, {})
        return [k for k, v in flags.items() if v]
