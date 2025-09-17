"""
Tool: get posts authored by a user ID (GET /2/users/{id}/tweets).

Designed to be registered as an MCP tool. Supports dry-run for safe testing.
"""

from typing import Optional, Dict, Any, List

from ...client import XClient
from ...config import load_credentials, require_any_auth


def get_posts_by_id(
    user_id: str,
    since_id: Optional[str] = None,
    until_id: Optional[str] = None,
    max_results: Optional[int] = None,
    pagination_token: Optional[str] = None,
    exclude: Optional[List[str]] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    tweet_fields: Optional[List[str]] = None,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """Fetch posts authored by the specified user ID from X.

    See X API GET /2/users/{id}/tweets for parameter semantics.
    """
    creds = load_credentials()
    require_any_auth(creds)

    client = XClient(creds=creds)
    return client.get_user_tweets(
        user_id=user_id,
        since_id=since_id,
        until_id=until_id,
        max_results=max_results,
        pagination_token=pagination_token,
        exclude=exclude,
        start_time=start_time,
        end_time=end_time,
        tweet_fields=tweet_fields,
        dry_run=dry_run,
    )


__all__ = ["get_posts_by_id"]
