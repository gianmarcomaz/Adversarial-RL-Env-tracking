#!/bin/bash
set -e

python /tests/verify.py

if [ ! -f /logs/verifier/reward.json ]; then
  echo 0 > /logs/verifier/reward.txt
fi
