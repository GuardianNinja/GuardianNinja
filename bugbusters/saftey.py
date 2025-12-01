from dataclasses import dataclass

@dataclass
class SafetyGate:
    child_safe: bool = True
    retreat_on_presence: bool = True

    def allow_operation(self, occupied: bool) -> bool:
        if self.child_safe and self.retreat_on_presence and occupied:
            # Pause operations in occupied rooms
            return False
        return True
