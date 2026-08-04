#!/bin/bash
# Starts the AI Content OS API server as a detached background process.
# Usage: ./run_server.sh   (stop with: pkill -f "uvicorn app.main")
set -e
cd "$(dirname "$0")"

export PINTREST_API_DIR="$(pwd)"

LAUNCHER=$(mktemp /tmp/start_api_XXXXXX.py)
cat > "$LAUNCHER" << 'PYEOF'
import os, sys
os.setsid()  # detach into a new session so the server survives shell exit
if os.fork() > 0:
    sys.exit(0)
os.chdir(os.environ.get("PINTREST_API_DIR", "."))
os.execv(
    os.path.abspath(".venv/bin/python"),
    [".venv/bin/python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"],
)
PYEOF

nohup .venv/bin/python "$LAUNCHER" > /tmp/pinterest_api.log 2>&1 &
echo "API starting... check http://localhost:8000/health"
