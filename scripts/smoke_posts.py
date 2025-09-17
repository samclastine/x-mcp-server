"""Quick smoke test for GET /2/users/{id}/tweets (dry-run).

Prints the assembled request with Authorization header redacted.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.tools.func.x_get_posts_by_id import get_posts_by_id


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
    # Example user id; this is just a dry run
    res = get_posts_by_id(
        user_id="2244994945",
        max_results=10,
        exclude=["retweets", "replies"],
        tweet_fields=["id", "text", "created_at", "public_metrics"],
        dry_run=True,
    )
    print(redact_headers(res))


if __name__ == "__main__":
    main()
