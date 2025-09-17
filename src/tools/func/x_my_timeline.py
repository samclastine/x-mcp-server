"""
Tool: get reverse-chronological timeline for the authenticated user.

Endpoint: GET /2/users/:id/timelines/reverse_chronological
"""

from typing import Optional, Dict, Any

from ...client import XClient
from ...config import load_credentials, require_any_auth


def x_my_timeline(
    limit: Optional[int] = None,
    pagination: Optional[str] = None,
    dry_run: bool = True,
) -> Dict[str, Any]:
    """Fetch the authenticated user's reverse-chronological timeline.

    Parameters:
        limit: Max number of results (maps to max_results)
        pagination: Cursor / next_token (maps to pagination_token)
        dry_run: When True, returns request details without network calls.

    Response (200, application/json):
        Returns an object with `data` as a non-empty array of Tweet objects. When tweet.fields are requested,
        Tweet objects can include:
        - attachments, author_id (string), community_id (string), context_annotations (array),
          conversation_id (string), created_at (ISO8601), display_text_range ([start, end]), edit_controls,
          edit_history_tweet_ids (array of string IDs), entities, geo, id (string), in_reply_to_user_id (string),
          lang (BCP47), non_public_metrics, note_tweet, organic_metrics, possibly_sensitive (bool),
          promoted_metrics, public_metrics, referenced_tweets (array), reply_settings (enum), scopes,
          source (deprecated), suggested_source_links (array), text (string), username (string), withheld (object).
    """
    creds = load_credentials()
    require_any_auth(creds)

    client = XClient(creds=creds)
    return client.get_my_reverse_chronological(
        max_results=limit,
        pagination_token=pagination,
        dry_run=dry_run,
    )


__all__ = ["x_my_timeline"]
