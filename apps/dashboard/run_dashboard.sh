#!/bin/bash
# Starts the Next.js dashboard as a detached background process.
# Usage: ./run_dashboard.sh   (stop with: pkill -f "next dev")
set -e
cd "$(dirname "$0")"

export PINTREST_DASH_DIR="$(pwd)"
export PINTREST_NODE="$(command -v node)"

LAUNCHER=$(mktemp /tmp/start_dash_XXXXXX.py)
cat > "$LAUNCHER" << 'PYEOF'
import os, sys
os.setsid()  # detach into a new session so the server survives shell exit
if os.fork() > 0:
    sys.exit(0)
os.chdir(os.environ.get("PINTREST_DASH_DIR", "."))
node = os.environ.get("PINTREST_NODE", "node")
os.execv(node, [node, "node_modules/next/dist/bin/next", "dev", "-p", "3000"])
PYEOF

nohup python3 "$LAUNCHER" > /tmp/pinterest_dashboard.log 2>&1 &
echo "Dashboard starting on http://localhost:3000"
