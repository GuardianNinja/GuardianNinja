class ConsentError(Exception):
    """Raised when an action requires explicit consent but none is present."""

class BoundaryViolation(Exception):
    """Raised when an action violates the universal respect policy."""

class AmbiguousContextError(Exception):
    """Raised when context is insufficient to determine a safe decision."""
