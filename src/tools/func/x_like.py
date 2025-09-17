"""
Tool: Like a Tweet by ID on behalf of the authenticated user.

Endpoint: POST /2/users/{id}/likes
"""

from typing import Optional, Dict, Any

from ...client import XClient
from ...config import load_credentials, require_any_auth


def like_tweet_by_tweetId(
    tweet_id: str,
    user_id: Optional[str] = None,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """Cause the authenticated user to like the specified Tweet.

    Parameters:
        tweet_id: The ID of the Tweet to like.
        user_id: Optional explicit source user ID; if omitted (live mode), will resolve via /users/me.
        dry_run: When True, returns request details without network calls.

    Response (200, application/json):
        - data.liked: boolean
        - errors: object[] (optional)
    """
    creds = load_credentials()
    require_any_auth(creds)

    client = XClient(creds=creds)
    return client.like_tweet(tweet_id=tweet_id, user_id=user_id, dry_run=dry_run)


__all__ = ["like_tweet_by_tweetId"]
