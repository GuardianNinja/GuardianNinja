def test_monitor_thread_stops_cleanly(self):
    # auth callback for engage
    self.sys.auth_callback = test_auth_callback_factory([self.biometric])
    self.sys.engage_coupling()
    # allow monitor to run a short time
    time.sleep(0.5)
    # request safe disengage and ensure thread joins
    self.sys._safe_disengage()
    # If join succeeded, thread should not be alive
    thread = self.sys._monitor_thread
    if thread:
        self.assertFalse(thread.is_alive())

def test_power_loss_triggers_safe_disengage(self):
    self.sys.auth_callback = test_auth_callback_factory([self.biometric])
    self.sys.engage_coupling()
    self.sys.simulate_power_loss()
    self.assertFalse(self.sys.engaged)
    self.assertIn("AUTO SAFE DISENGAGE", " ".join(self.sys.support_logs) or "")
