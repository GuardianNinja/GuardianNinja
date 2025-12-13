# safety_supervisor.py  -- run on primary safety MCU
import time
from crypto import sign_blob  # signing helper for audit logs

SAMPLE_INTERVAL = 0.05  # 50 ms
LOAD_THRESHOLD = 50.0   # kg equivalent per limb (example)
DROP_RATE_THRESHOLD = 10.0  # sudden drop kg/s
HEARTBEAT_TIMEOUT = 1.0  # seconds for secondary watchdog

state = "NORMAL"  # NORMAL, WARNING, FAILSAFE, EMERGENCY_DESCENT

def read_sensors():
    return {
        "load_left": read_adc(0),
        "load_right": read_adc(1),
        "accel_z": read_accel_z(),
        "timestamp": time.time()
    }

def check_redundancy(primary, secondary):
    # simple cross-check; more advanced fusion recommended
    for k in ("load_left","load_right"):
        if abs(primary[k] - secondary[k]) > (0.2 * max(primary[k],1.0)):
            return False
    return True

def trigger_failsafe(reason):
    global state
    state = "FAILSAFE"
    engage_mechanical_release(False)  # ensure safe mode engaged
    log_event({"event":"FAILSAFE","reason":reason,"ts":time.time()})
    notify_ops("FAILSAFE", reason)

def emergency_descent():
    global state
    state = "EMERGENCY_DESCENT"
    enable_descent_mode()
    log_event({"event":"EMERGENCY_DESCENT","ts":time.time()})
    notify_ops("EMERGENCY_DESCENT","automatic descent engaged")

def log_event(payload):
    payload["signed"] = sign_blob(payload)  # immutable audit
    send_to_local_store(payload)

def main_loop():
    last_secondary_hb = time.time()
    while True:
        primary = read_sensors()
        secondary = read_secondary_sensors()  # from independent MCU
        now = time.time()

        # heartbeat check
        if now - last_secondary_hb > HEARTBEAT_TIMEOUT:
            trigger_failsafe("secondary_watchdog_timeout")
            continue

        # redundancy check
        if not check_redundancy(primary, secondary):
            trigger_failsafe("sensor_mismatch")
            continue

        # load and drop detection
        for limb in ("load_left","load_right"):
            if primary[limb] > LOAD_THRESHOLD:
                trigger_failsafe("overload_"+limb)
                break

        # sudden drop detection (simple derivative)
        if detect_sudden_drop(primary, secondary, DROP_RATE_THRESHOLD):
            emergency_descent()
            continue

        # normal operation
        log_event({"event":"HEARTBEAT","ts":now,"loads":[primary["load_left"],primary["load_right"]]})
        time.sleep(SAMPLE_INTERVAL)

if __name__ == "__main__":
    main_loop()
