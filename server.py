"""MCP server exposing an X posting tool via STDIO.

This uses FastMCP to register a single tool that posts text to X (Twitter).
Logs go to STDERR; do not print to STDOUT.
"""

from __future__ import annotations

import sys
import logging
from typing import Optional, Dict, Any

from mcp.server.fastmcp import FastMCP

# Ensure repo root is on sys.path so `uv run src/server.py` works
import sys as _sys
from pathlib import Path as _Path
import os as _os

# Ensure the repository root (this file's directory) is on sys.path so imports like `src.tools...` work
_REPO_ROOT = _Path(__file__).resolve().parent
if str(_REPO_ROOT) not in _sys.path:
    _sys.path.insert(0, str(_REPO_ROOT))

from src.tools.func.x_post import post_to_x
from src.tools.func.x_me import get_x_me
from src.tools.func.x_get_posts_by_id import get_posts_by_id as _get_posts_by_id
from src.tools.func.x_my_timeline import x_my_timeline as _x_my_timeline
from src.tools.func.x_like import like_tweet_by_tweetId as _like_tweet_by_tweetId


# ── logging to STDERR ─────────────────────────────────────────────────────────
logging.basicConfig(stream=sys.stderr, level=logging.INFO)
log = logging.getLogger("mcp-x-post")


# ── MCP server ───────────────────────────────────────────────────────────────
mcp = FastMCP("x-post")


@mcp.tool()
def x_post(
    text: str,
    media_url: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """Post text to X (Twitter).

    - dry_run=True (default) returns the request details without network calls.
    - dry_run=False attempts a live POST (requires OAuth1 credentials with write permissions).
    """
    return post_to_x(text=text, media_url=media_url, metadata=metadata, dry_run=dry_run)


@mcp.tool()
def x_me(
    user_fields: Optional[list[str]] = None,
    expansions: Optional[list[str]] = None,
    tweet_fields: Optional[list[str]] = None,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """Get the authenticated user's profile (GET /2/users/me).

    - user_fields: A list of user fields to include (maps to 'user.fields').
    - expansions: A list of expansions to include.
    - tweet_fields: A list of tweet fields to include.
    - dry_run=True (default) returns the request details without network calls.
    """
    return get_x_me(
        user_fields=user_fields,
        expansions=expansions,
        tweet_fields=tweet_fields,
        dry_run=dry_run,
    )


@mcp.tool()
def get_posts_by_id(
    user_id: str,
    since_id: Optional[str] = None,
    until_id: Optional[str] = None,
    max_results: Optional[int] = None,
    pagination_token: Optional[str] = None,
    exclude: Optional[list[str]] = None,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    tweet_fields: Optional[list[str]] = None,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """Get posts authored by a user ID (GET /2/users/{id}/tweets).

    - Auth: Prefers app bearer; falls back to OAuth1.
    - Supports common query params and dry-run mode.
    """
    return _get_posts_by_id(
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


@mcp.tool()
def x_my_timeline(
    limit: Optional[int] = None,
    pagination: Optional[str] = None,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """Get the reverse-chronological timeline for the authenticated user.

    Endpoint: GET /2/users/:id/timelines/reverse_chronological
    """
    if limit is not None and limit < 1:
        raise ValueError("limit must be >= 1")
    return _x_my_timeline(limit=limit, pagination=pagination, dry_run=dry_run)


@mcp.tool()
def get__my_timeline(
    limit: Optional[int] = None,
    pagination: Optional[str] = None,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """Alias of x_my_timeline (GET /2/users/:id/timelines/reverse_chronological)."""
    if limit is not None and limit < 1:
        raise ValueError("limit must be >= 1")
    return _x_my_timeline(limit=limit, pagination=pagination, dry_run=dry_run)


@mcp.tool()
def like_tweet_by_tweetId(
    tweet_id: str,
    user_id: Optional[str] = None,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """Like a Tweet by ID on behalf of the authenticated user (POST /2/users/{id}/likes).

    - tweet_id: Target Tweet ID to like.
    - user_id: Optional source user ID; if omitted in live mode, it will be resolved via /users/me.
    - dry_run=True returns the request details without network calls.
    """
    return _like_tweet_by_tweetId(tweet_id=tweet_id, user_id=user_id, dry_run=dry_run)


if __name__ == "__main__":
    # IMPORTANT: Do not print to STDOUT; FastMCP owns the protocol stream.
    #
    # In some hosting environments (e.g., when embedded under an already-running asyncio loop),
    # starting a fresh loop may raise "Already running asyncio in this thread". If you need to
    # import this module without auto-starting the server, set MCP_AUTORUN=0 in the environment
    # and invoke `mcp.run()` yourself from a compatible context.
    if _os.getenv("MCP_AUTORUN", "1") != "0":
        mcp.run()
