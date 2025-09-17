"""
Tool: get the authenticated user's X profile via GET /2/users/me.

This function is designed to be registered as an MCP tool. It uses XClient to
assemble an authenticated request and supports a safe dry-run mode.
"""

from typing import Optional, Dict, Any, List

from ...client import XClient
from ...config import load_credentials, require_any_auth


def get_x_me(
    user_fields: Optional[List[str]] = None,
    expansions: Optional[List[str]] = None,
    tweet_fields: Optional[List[str]] = None,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """Fetch the authenticated user's profile from X.

    Parameters:
        user_fields: Optional list of user fields to include.
        expansions: Optional list of expansions.
        tweet_fields: Optional list of tweet fields.
        dry_run: When True, returns the request details without performing a network call.

    Returns:
        A response with request details (dry_run=True) or the API response (dry_run=False).
    """
    creds = load_credentials()
    require_any_auth(creds)

    client = XClient(creds=creds)
    return client.get_me(
        user_fields=user_fields,
        expansions=expansions,
        tweet_fields=tweet_fields,
        dry_run=dry_run,
    )


__all__ = ["get_x_me"]
