"""Quick smoke test for GET /2/users/:id/timelines/reverse_chronological (dry-run).

Uses the function wrapper directly; MCP tool registration is in server.py.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.tools.func.x_my_timeline import x_my_timeline


def redact_headers(obj):
    if not isinstance(obj, dict):
        return obj
    headers = obj.get("headers")
    if isinstance(headers, dict) and "Authorization" in headers:
        headers = headers.copy()
        headers["Authorization"] = "Bearer <REDACTED>"
        obj = obj.copy()
        obj["headers"] = headers
    return obj


def main() -> None:
    res = x_my_timeline(limit=25, pagination=None, dry_run=True)
    print(redact_headers(res))


if __name__ == "__main__":
    main()
