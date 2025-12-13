# nanovelcro.py
import time
import secrets
import logging
import threading
import random
from typing import Callable, Optional
import numpy as np

logger = logging.getLogger("NanoVelcro")
logging.basicConfig(level=logging.INFO)

def xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

class NanoVelcroCouplingSystem:
    def __init__(
        self,
        user_type: str = "adult",
        emergency_password: Optional[str] = None,
        biometric_store: Optional[dict] = None,
        rng: Optional[random.Random] = None,
        auth_callback: Optional[Callable[[str], str]] = None,
        key: Optional[bytes] = None,
        gyro_threshold_adult: float = 0.2,
        gyro_threshold_kid: float = 0.1,
    ):
        """
        - auth_callback(prompt) -> str : used for biometric/password input in tests or UI layers.
        - rng: inject random.Random(seed) for deterministic behavior in tests.
        - key: optional symmetric key (bytes) for deterministic encryption in tests.
        """
        self.engaged = False
        self.user_type = user_type
        self.gyro_firewall_active = False
        self._key = key or secrets.token_bytes(16)
        self._monitor_thread: Optional[threading.Thread] = None
        self._monitor_stop = threading.Event()
        self.support_logs = []
        self._emergency_password = emergency_password
        self._biometric_store = biometric_store or {"fingerprint": None}
        self.rng = rng or random.Random()
        # Use numpy Generator seeded from the same RNG for reproducibility
        self._np_rng = np.random.default_rng(self.rng.randint(0, 2**31 - 1))
        self.auth_callback = auth_callback
        self.gyro_threshold_adult = gyro_threshold_adult
        self.gyro_threshold_kid = gyro_threshold_kid
        self.power_ok = True
        logger.info("NanoVelcro system initialized for %s user.", user_type)

    # --- Encryption (symmetric, byte-safe) ---
    def _encrypt_bytes(self, data: bytes) -> bytes:
        return xor_bytes(data, self._key)

    def _encrypt_text(self, text: str) -> bytes:
        return self._encrypt_bytes(text.encode("utf-8"))

    def _decrypt_text(self, cipher: bytes) -> str:
        return self._encrypt_bytes(cipher).decode("utf-8")

    # --- Auth helpers ---
    def _get_auth_input(self, prompt: str) -> str:
        if self.auth_callback:
            return self.auth_callback(prompt)
        raise RuntimeError("No auth_callback provided for interactive input in this environment.")

    def set_biometric(self, fingerprint_hash: str):
        self._biometric_store["fingerprint"] = fingerprint_hash

    def set_emergency_password(self, pwd: str):
        self._emergency_password = pwd

    def _verify_biometric(self) -> bool:
        logger.info("Scanning biometric (fingerprint)...")
        scan_input = self._get_auth_input("fingerprint:")
        ok = scan_input == self._biometric_store.get("fingerprint")
        logger.info("Biometric verification: %s", "PASS" if ok else "FAIL")
        return ok

    # --- Lifecycle ---
    def engage_coupling(self):
        if self.engaged:
            logger.info("Coupling already engaged.")
            return False
        if not self._verify_biometric():
            logger.warning("Biometric authentication failed. Engagement denied.")
            return False
        if not self.power_ok:
            logger.warning("Power not OK. Cannot engage.")
            return False
        logger.info("Engaging nano-velcro coupling...")
        time.sleep(0.2)
        self.engaged = True
        self._start_gyro_firewall()
        self._start_monitoring()
        logger.info("Coupling engaged. Tether system active.")
        return True

    def disengage_with_button(self):
        if not self.engaged:
            logger.info("Coupling not engaged.")
            return False
        logger.info("Button pressed: attempting safe disengage...")
        if self._perform_safety_checks():
            self._safe_disengage()
            return True
        logger.warning("Disengagement blocked: safety checks failed.")
        return False

    def emergency_override(self):
        """
        Multi-factor override: requires biometric + emergency password.
        All overrides are logged in support_logs for audit.
        """
        if not self.engaged:
            logger.info("Coupling not engaged; no override needed.")
            return False
        logger.warning("Initiating emergency override protocol...")
        if not self._verify_biometric():
            logger.warning("Biometric authentication failed. Override denied.")
            return False
        if not self._emergency_password:
            logger.error("No emergency password configured; override denied.")
            return False
        pwd = self._get_auth_input("emergency_password:")
        if secrets.compare_digest(pwd, self._emergency_password):
            logger.warning("Emergency override accepted. Forcing disengage.")
            self.support_logs.append("EMERGENCY OVERRIDE ACTIVATED")
            self._safe_disengage()
            return True
        logger.warning("Incorrect emergency password. Override denied.")
        return False

    def _safe_disengage(self):
        self.engaged = False
        self._stop_gyro_firewall()
        self._stop_monitoring()
        logger.info("Coupling safely disengaged.")

    # --- Gyro firewall ---
    def _start_gyro_firewall(self):
        self.gyro_firewall_active = True
        logger.info("Gyroscopic firewall activated.")
        sample = "system_status: stable"
        cipher = self._encrypt_text(sample)
        logger.debug("Encrypted sample (hex): %s", cipher.hex())

    def _stop_gyro_firewall(self):
        self.gyro_firewall_active = False
        logger.info("Gyroscopic firewall deactivated.")

    # --- Safety checks ---
    def _perform_safety_checks(self) -> bool:
        logger.info("Running dual cross-validation and safety checks...")
        gyro_ok = self._gyro_check()
        enc_ok = self._encryption_validation()
        ok = gyro_ok and enc_ok and self.power_ok
        logger.info("Safety checks result: %s", "PASS" if ok else "FAIL")
        return ok

    def _gyro_check(self) -> bool:
        stability = self.rng.uniform(0.0, 1.0)
        threshold = self.gyro_threshold_kid if self.user_type == "kid" else self.gyro_threshold_adult
        logger.debug("Gyro stability=%.3f threshold=%.3f", stability, threshold)
        return stability > threshold

    def _encryption_validation(self) -> bool:
        test = "test_payload"
        cipher = self._encrypt_text(test)
        try:
            plain = self._decrypt_text(cipher)
            return plain == test
        except Exception:
            return False

    # --- Monitoring ---
    def _start_monitoring(self):
        self._monitor_stop.clear()
        self._monitor_thread = threading.Thread(target=self._monitor_support, daemon=False)
        self._monitor_thread.start()
        logger.info("Support monitoring started.")

    def _stop_monitoring(self):
        self._monitor_stop.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=3.0)
        logger.info("Support monitoring stopped. Logs: %s", self.support_logs)

    def _monitor_support(self):
        consecutive_alerts = 0
        while not self._monitor_stop.is_set() and self.engaged:
            status = "Stable" if self.rng.random() > 0.1 else "Alert: Instability detected!"
            self.support_logs.append(status)
            logger.info("Monitor: %s", status)
            if status.startswith("Alert"):
                consecutive_alerts += 1
            else:
                consecutive_alerts = 0
            if consecutive_alerts >= 2:
                logger.warning("Repeated instability detected: triggering emergency override.")
                # call emergency_override which will require auth_callback; if you want auto-bypass,
                # implement a separate emergency_release() that logs and forces disengage.
                try:
                    self.emergency_override()
                except RuntimeError:
                    # If no auth_callback provided, fallback to safe disengage and log
                    logger.error("No auth callback for override; performing safe disengage for safety.")
                    self.support_logs.append("AUTO SAFE DISENGAGE DUE TO INSTABILITY")
                    self._safe_disengage()
                break
            self._monitor_stop.wait(5.0)

    # --- Power simulation ---
    def simulate_power_loss(self):
        logger.warning("Simulating power loss.")
        self.power_ok = False
        if self.engaged:
            logger.info("Power loss while engaged: performing safe disengage.")
            self._safe_disengage()

    # --- Zero-g simulation ---
    def simulate_zero_gravity(self, duration: float = 10.0, time_step: float = 0.1):
        if not self.engaged:
            logger.info("Engage coupling first to simulate stabilized zero-gravity.")
            return []
        logger.info("Simulating zero-gravity physics with tether stabilization...")
        position = np.zeros(3)
        velocity = self._np_rng.uniform(-1.0, 1.0, 3)
        times = np.arange(0.0, duration, time_step)
        snapshots = []
        for t in times:
            if self.engaged:
                velocity *= 0.95
            position += velocity * time_step
            # record one snapshot per second for summary
            if abs((t % 1.0) - 0.0) < 1e-6:
                logger.info("Time %.1fs pos=%s vel=%s", t, np.round(position, 3).tolist(), np.round(velocity, 3).tolist())
                snapshots.append((float(t), position.copy(), velocity.copy()))
        logger.info("Simulation complete. Tether kept system stable.")
        return snapshots
