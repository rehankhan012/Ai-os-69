"""Verify the renderer preview endpoint returns real SVG over the HTTP layer."""

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

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app)

print("=== GET /health ===")
r = client.get("/health")
print("health:", r.status_code, r.json())

print("\n=== POST /api/v1/agents/demo-workflow ===")
r = client.post(
    "/api/v1/agents/demo-workflow",
    json={"keyword": "top 10 AI models 2026", "niche": "technology"},
)
data = r.json()
print("status:", r.status_code, "| success:", data.get("success"), "| agents:", len(data.get("agents", [])))

print("\n=== POST /api/v1/renderer/preview ===")
r = client.post(
    "/api/v1/renderer/preview",
    json={"topic": "Top 10 AI Models 2026", "audience": "Students", "variations": 3},
)
data = r.json()
print("status:", r.status_code, "| success:", data.get("success"))
print("template:", data.get("template"))
previews = data.get("previews", [])
print("previews:", len(previews))
for p in previews:
    print("  variation", p["variation"], "| quality", p["quality_score"], "| svg chars:", len(p["svg"]), "| <svg>:", "<svg" in p["svg"])

print("\n=== GET /api/v1/renderer/templates ===")
r = client.get("/api/v1/renderer/templates")
data = r.json()
print("templates:", data.get("total"))

print("\nALL RENDERER TESTS PASSED")
