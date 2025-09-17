"""Quick smoke test for GET /2/users/me (dry-run).

Runs the get_x_me function in dry_run mode so no network call is made.
"""

import sys
from pathlib import Path

# Ensure repo root on path
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.tools.func.x_me import get_x_me


def main() -> None:
    res = get_x_me(
        user_fields=["id", "name", "username", "created_at", "verified"],
        expansions=None,
        tweet_fields=None,
        dry_run=True,
    )
    # Redact Authorization header if present
    if isinstance(res, dict) and isinstance(res.get("headers"), dict) and "Authorization" in res["headers"]:
        red = res.copy()
        red_h = red["headers"].copy()
        red_h["Authorization"] = "Bearer <REDACTED>"
        red["headers"] = red_h
        print(red)
    else:
        print(res)


if __name__ == "__main__":
    main()
