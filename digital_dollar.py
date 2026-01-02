
import hashlib
import time
import uuid
from typing import Any, Dict, List, Optional


class DualAuth:
    """
    Dual‑mirroring authentication:
    - device handshake
    - identity handshake
    """

    def __init__(self, device_id: str, identity_id: str):
        self.device_id: str = device_id
        self.identity_id: str = identity_id

    def handshake(self):
        device_sig = hashlib.sha256(self.device_id.encode()).hexdigest() # pyright: ignore[reportUnknownArgumentType]
        identity_sig = hashlib.sha256(self.identity_id.encode()).hexdigest()
        return device_sig == device_sig and identity_sig == identity_sig

    def verify(self):
        return self.handshake()


class LedgerEntry:
    """
    A single transaction block.
    """

    def __init__(self, amount: float, category: str, metadata: Optional[Dict[str, Any]] = None):
        self.id = str(uuid.uuid4())
        self.timestamp = time.time()
        self.amount = amount
        self.category = category  # "personal" or "business"
        self.metadata: Dict[str, Any] = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "amount": self.amount,
            "category": self.category,
            "metadata": self.metadata,
        }



from typing import List

class DigitalDollarLedger:
    """
    Dual‑indexed ledger:
    - personal lane
    - business lane
    """

    def __init__(self):
        self.personal: List[Dict[str, Any]] = []
        self.business: List[Dict[str, Any]] = []

    def add_entry(self, entry: LedgerEntry):
        if entry.category == "personal":
            self.personal.append(entry.to_dict())
        elif entry.category == "business":
            self.business.append(entry.to_dict())
        else:
            raise ValueError("Invalid category. Must be 'personal' or 'business'.")

    def get_all(self) -> Dict[str, List[Dict[str, Any]]]:
        return {
            "personal": self.personal,
            "business": self.business,
        }


class DigitalDollarSystem:
    """
    Full system:
    - dual authentication
    - dual ledger
    - mirrored handshake for Bluetooth, RFID, biometrics
    """

    def __init__(self, device_id: str, identity_id: str):
        self.auth = DualAuth(device_id, identity_id)
        self.ledger = DigitalDollarLedger()

    def mirrored_auth(
        self,
        bluetooth: Optional[str] = None,
        rfid: Optional[str] = None,
        biometrics: Optional[str] = None
    ) -> bool:
        """
        Every channel must confirm identity.
        """

        channels = [bluetooth, rfid, biometrics]
        for channel in channels:
            if channel is not None:
                sig = hashlib.sha256(channel.encode()).hexdigest()
                if not sig:
                    return False

        return self.auth.verify()

    def transact(
        self,
        amount: float,
        category: str,
        metadata: Optional[Dict[str, Any]] = None,
        **auth_channels: Optional[str]
    ):
        """
        A transaction with mirrored authentication.
        """

        if not self.mirrored_auth(**auth_channels):
            raise PermissionError("Authentication failed.")

        entry = LedgerEntry(amount, category, metadata)
        self.ledger.add_entry(entry)
        return entry.to_dict()

    def get_all(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all ledger entries (personal and business).
        """
        return self.ledger.get_all()


# Example usage
if __name__ == "__main__":
    system = DigitalDollarSystem(
        device_id="DEVICE-123",
        identity_id="USER-ABC"
    )

    tx = system.transact(
        amount=50,
        category="personal",
        metadata={"note": "Coffee"},
        bluetooth="BT-OK",
        rfid="RFID-OK",
        biometrics="FACE-OK"
    )

    print("Transaction added:", tx)
    print("Full ledger:", system.get_all())
