#!/bin/bash
# Starts the public blog site (Darkverse) as a detached background process.
# Usage: ./run_site.sh   (stop with: pkill -f "next dev -p 3001")
set -e
cd "$(dirname "$0")"

export PINTREST_SITE_DIR="$(pwd)"
export PINTREST_NODE="$(command -v node)"

LAUNCHER=$(mktemp /tmp/start_site_XXXXXX)
cat > "$LAUNCHER" << 'PYEOF'
import os, sys
os.setsid()  # detach into a new session so the server survives shell exit
if os.fork() > 0:
    sys.exit(0)
os.chdir(os.environ.get("PINTREST_SITE_DIR", "."))
node = os.environ.get("PINTREST_NODE", "node")
os.execv(node, [node, "node_modules/next/dist/bin/next", "dev", "-p", "3001"])
PYEOF

nohup python3 "$LAUNCHER" > /tmp/pinterest_site.log 2>&1 &
echo "Blog site starting on http://localhost:3001"
