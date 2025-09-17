"""Quick smoke test for POST /2/users/{id}/likes (dry-run).

Prints the assembled request with Authorization header redacted.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.tools.func.x_like import like_tweet_by_tweetId


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
    res = like_tweet_by_tweetId(tweet_id="1346889436626259968", dry_run=True)
    print(redact_headers(res))


if __name__ == "__main__":
    main()
