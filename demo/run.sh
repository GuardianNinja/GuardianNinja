#!/usr/bin/env bash
# demo/run.sh - start demo services and write output.log
mkdir -p demo
echo "Starting Leaf Coin demo..." | tee demo/output.log
# Simulate watcher
python3 - <<'PY'
import time, json, hashlib
log = {"events":[]}
print("Watcher started")
time.sleep(1)
# Wait for test_transfer to create a trigger file
for _ in range(30):
    try:
        with open("demo/trigger.json") as f:
            t = json.load(f)
            break
    except:
        time.sleep(1)
# Simulate detection
event = {"type":"transfer","amount":t.get("amount",0)}
log["events"].append(event)
print("ALERT: large transfer detected")
print("ACTION: throttle applied; multisig lock engaged")
# Anchor log (simple hash)
h = hashlib.sha256(json.dumps(log).encode()).hexdigest()
anchor_url = f"https://timestamp.service/{h[:16]}"
with open("demo/output.log","a") as f:
    f.write(f'ANCHOR: hash: {h} | anchor_url: {anchor_url}\n')
print(f"ANCHOR: hash: {h} | anchor_url: {anchor_url}")
PY
