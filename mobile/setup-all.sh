#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
echo "MSU Maintenance mobile - automated setup"
node scripts/setup.cjs
