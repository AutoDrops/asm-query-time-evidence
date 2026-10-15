#!/bin/sh
# One command: recompute all report tables from cached rows (offline).
cd "$(dirname "$0")" && python3 scripts/recompute.py | tee results/tables.md
