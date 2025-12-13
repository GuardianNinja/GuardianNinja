# test_nanovelcro.py
import unittest
import random
import secrets
from nanovelcro import NanoVelcroCouplingSystem

def test_auth_callback_factory(inputs):
    """Return an auth_callback that pops values from inputs list."""
    def cb(prompt):
        return inputs.pop(0)
    return cb

class TestNanoVelcro(unittest.TestCase):
    def setUp(self):
        # deterministic RNG
        self.rng = random.Random(42)
        # deterministic symmetric key for tests
        self.test_key = secrets.token_bytes(16)
        # test biometric and password
        self.biometric = "test_fp"
        self.password = "safe_pwd_123"
        # auth inputs will be consumed in order by auth_callback
        self.auth_inputs = [self.biometric, self.password]
        self.auth_cb = test_auth_callback_factory(self.auth_inputs.copy())

        self.sys = NanoVelcroCouplingSystem(
            user_type="kid",
            emergency_password=self.password,
            biometric_store={"fingerprint": self.biometric},
            rng=self.rng,
            auth_callback=self.auth_cb,
            key=self.test_key,
            gyro_threshold_kid=0.0,  # make gyro check pass deterministically
            gyro_threshold_adult=0.0
        )

    def test_encrypt_decrypt_roundtrip(self):
        text = "hello_test"
        cipher = self.sys._encrypt_text(text)
        plain = self.sys._decrypt_text(cipher)
        self.assertEqual(plain, text)

    def test_engage_and_disengage(self):
        # auth_callback will provide biometric then password when needed
        engaged = self.sys.engage_coupling()
        self.assertTrue(engaged)
        # simulate safe disengage (gyro thresholds set to 0 so checks pass)
        ok = self.sys.disengage_with_button()
        self.assertTrue(ok)
        self.assertFalse(self.sys.engaged)

    def test_emergency_override_requires_auth(self):
        # re-create auth inputs for this test
        auth_inputs = [self.biometric, self.password]
        self.sys.auth_callback = test_auth_callback_factory(auth_inputs)
        self.sys.engage_coupling()
        # now call emergency_override (will consume biometric + password)
        result = self.sys.emergency_override()
        self.assertTrue(result)
        self.assertFalse(self.sys.engaged)
        self.assertIn("EMERGENCY OVERRIDE ACTIVATED", self.sys.support_logs)

    def test_zero_g_simulation_returns_snapshots(self):
        # set up auth callback again
        self.sys.auth_callback = test_auth_callback_factory([self.biometric])
        self.sys.engage_coupling()
        snaps = self.sys.simulate_zero_gravity(duration=3.0, time_step=0.1)
        # should have ~3 snapshots (one per second)
        self.assertTrue(len(snaps) >= 3)
        self.sys._safe_disengage()

if __name__ == "__main__":
    unittest.main()
