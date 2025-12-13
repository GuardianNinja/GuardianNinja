#!/usr/bin/env bash
# demo/test_transfer.sh - simulate a large transfer
cat > demo/trigger.json <<JSON
{"amount":1000000,"from":"0xdead","to":"0xbeef"}
JSON
echo "Test transfer written to demo/trigger.json"
