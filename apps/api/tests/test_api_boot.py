"""Verify the API boots and the demo-workflow endpoint returns all 9 agents."""

import asyncio
import sys
from pathlib import Path


def _find_project_root():
    d = Path(__file__).resolve().parent
    for _ in range(6):
        if (d / "packages").is_dir():
            return d
        d = d.parent
    return None


ROOT = _find_project_root()
API_DIR = Path(__file__).resolve().parent.parent
for p in (API_DIR, ROOT):
    if p is not None and str(p) not in sys.path:
        sys.path.insert(0, str(p))

# The full app import would crash at startup before the graphic-engine fixes
import app.main  # noqa: F401
print("API APP IMPORT: OK")

from app.api.agents import run_demo_workflow, DemoWorkflowRequest  # noqa: E402


async def main():
    body = DemoWorkflowRequest(keyword="trending AI model top 10", niche="technology")
    res = await run_demo_workflow(body)
    print("WORKFLOW SUCCESS:", res["success"])
    print("WORKFLOW ID:", res["workflow_id"])
    print("AGENTS RAN:", len(res["agents"]))
    for a in res["agents"]:
        keys = list(a["output"].keys())[:5]
        print(
            "  OK {0:12} {1:18} success={2} {3}ms keys={4}".format(
                a["name"], a["display"], a["success"], a["processing_time_ms"], keys
            )
        )
    print("MASTER:", res["master"])


asyncio.run(main())
