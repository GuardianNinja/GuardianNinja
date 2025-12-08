"""Custom exceptions for QPPI Firewall"""

class PolicyViolation(Exception):
    """Raised when a policy is violated"""
    pass

class ConsentRequired(Exception):
    """Raised when consent is required but not provided"""
    pass

class EmergencyStopEngaged(Exception):
    """Raised when emergency stop is engaged"""
    pass
