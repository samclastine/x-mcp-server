"""
Client module for external APIs used by this MCP server.

Includes:
- GenericClient: Basic placeholder for demonstration
- XClient: Auth-aware client for X (Twitter) API, sourcing credentials from env
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, List

from .config import XCredentials, load_credentials

import json
import time
from urllib.parse import urljoin

import requests
from requests_oauthlib import OAuth1


# Example client class - customize as needed
class GenericClient:
    """Generic client for external services"""

    def __init__(self, api_key: str = None, base_url: str = None):
        self.api_key = api_key
        self.base_url = base_url or "https://api.example.com"

    def make_request(self, endpoint: str, params: dict = None) -> dict:
        """Make a generic API request"""
        # This is a placeholder - implement actual API calls as needed
        return {
            "success": True,
            "endpoint": endpoint,
            "params": params or {},
            "note": "This is a placeholder implementation. Replace with actual API logic.",
        }


@dataclass
class XClient:
    """Client for interacting with the X (Twitter) API.

    This version focuses on assembling headers/credentials. Actual HTTP calls are
    intentionally omitted. You can integrate httpx/requests and OAuth1 signing later.
    """

    base_url: str = "https://api.x.com/2"
    creds: XCredentials = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.creds is None:
            self.creds = load_credentials()

    def build_headers(self) -> Dict[str, str]:
        """Return headers for the best-available auth configuration.

        Preference order:
        1) App-only bearer token
        2) OAuth 1.0a (requires request signing at request time)
        3) OAuth 2.0 client (requires token exchange before use)
        """
        if self.creds.app_bearer_token:
            return {"Authorization": f"Bearer {self.creds.app_bearer_token}"}

        # For OAuth 1.0a signed requests, the Authorization header is generated per-request.
        # Here, we return a placeholder indicating OAuth1 will be used if configured.
        if self.creds.has_oauth1:
            return {"X-Auth-Mode": "oauth1-signed-request"}

        # For OAuth2 client credentials, you'd normally exchange for a token first.
        if self.creds.has_oauth2_client:
            return {"X-Auth-Mode": "oauth2-client-needs-token"}

        return {}

    def post_status(self, text: str, media_url: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None,
                    dry_run: bool = True) -> Dict[str, Any]:
        """Post a status update (stubbed).

        If dry_run is True, no network requests are made; we return the assembled
        details, which is safe for local testing.
        """
        headers = self.build_headers()
        payload = {
            "text": text,
            "media_url": media_url,
            "metadata": metadata or {},
        }
        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "url": f"{self.base_url}/tweets",
                "headers": headers,
                "payload": payload,
                "note": "This is a dry run. Wire up real HTTP calls and signing to post.",
            }
        # Live request path
        url = urljoin(self.base_url + '/', 'tweets')

        # Prefer OAuth1 user context if available (required for posting on behalf of a user)
        if self.creds.has_oauth1:
            auth = OAuth1(
                self.creds.api_key,
                self.creds.api_key_secret,
                self.creds.access_token,
                self.creds.access_token_secret,
                signature_type='auth_header',
            )
            try:
                resp = requests.post(url, json={"text": text}, auth=auth, timeout=30)
            except requests.RequestException as e:
                return {"success": False, "error": f"Network error: {e}"}

            # Try to parse JSON regardless of status code
            try:
                data = resp.json()
            except ValueError:
                data = {"raw": resp.text}

            if 200 <= resp.status_code < 300:
                return {"success": True, "status": resp.status_code, "data": data}
            else:
                return {
                    "success": False,
                    "status": resp.status_code,
                    "error": data if isinstance(data, dict) else {"message": data},
                }

        # OAuth2 user tokens or app bearer alone are insufficient for posting without a user access token.
        # If only app bearer or client credentials are present, inform the user clearly.
        mode = (
            "app_bearer" if self.creds.has_app_bearer else
            ("oauth2_client" if self.creds.has_oauth2_client else "none")
        )
        return {
            "success": False,
            "error": (
                "Posting requires user context. Provide OAuth 1.0a credentials (API_KEY/API_KEY_SECRET + "
                "ACCESS_TOKEN/ACCESS_TOKEN_SECRET) or implement OAuth2 user token exchange."
            ),
            "auth_mode_detected": mode,
        }

    def get_me(
        self,
        user_fields: Optional[List[str]] = None,
        expansions: Optional[List[str]] = None,
        tweet_fields: Optional[List[str]] = None,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        """Retrieve the authenticated user's profile (GET /2/users/me).

        Parameters:
            user_fields: Optional list of user fields to include (maps to 'user.fields').
            expansions: Optional list of expansions to include.
            tweet_fields: Optional list of tweet fields to include (when expansions reference tweets).
            dry_run: When True, returns the request details without performing a network call.

        Returns:
            A dict containing either the dry-run request details or the live response.
        """
        params: Dict[str, str] = {}
        if user_fields:
            params["user.fields"] = ",".join(user_fields)
        if expansions:
            params["expansions"] = ",".join(expansions)
        if tweet_fields:
            params["tweet.fields"] = ",".join(tweet_fields)

        headers = self.build_headers()

        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "url": f"{self.base_url}/users/me",
                "headers": headers,
                "params": params,
                "note": "This is a dry run. Wire up real HTTP calls and signing to fetch.",
            }

        url = urljoin(self.base_url + '/', 'users/me')

        # Prefer OAuth1 user context if available (typical for user-authenticated endpoints)
        if self.creds.has_oauth1:
            auth = OAuth1(
                self.creds.api_key,
                self.creds.api_key_secret,
                self.creds.access_token,
                self.creds.access_token_secret,
                signature_type='auth_header',
            )
            try:
                resp = requests.get(url, params=params, auth=auth, timeout=30)
            except requests.RequestException as e:
                return {"success": False, "error": f"Network error: {e}"}

            try:
                data = resp.json()
            except ValueError:
                data = {"raw": resp.text}

            if 200 <= resp.status_code < 300:
                return {"success": True, "status": resp.status_code, "data": data}
            else:
                return {
                    "success": False,
                    "status": resp.status_code,
                    "error": data if isinstance(data, dict) else {"message": data},
                }

        # App-only bearer or OAuth2 client creds are not sufficient for /users/me without a user token
        mode = (
            "app_bearer" if self.creds.has_app_bearer else
            ("oauth2_client" if self.creds.has_oauth2_client else "none")
        )
        return {
            "success": False,
            "error": (
                "GET /2/users/me requires user context. Provide OAuth 1.0a credentials "
                "(API_KEY/API_KEY_SECRET + ACCESS_TOKEN/ACCESS_TOKEN_SECRET) or implement OAuth2 user token exchange."
            ),
            "auth_mode_detected": mode,
        }

    def get_user_tweets(
        self,
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
        """Retrieve posts authored by a user ID (GET /2/users/{id}/tweets).

        Auth:
            Prefers app-only bearer token if available. Falls back to OAuth1 user context.

        Parameters mirror X API query params. Times are ISO8601 strings.
        """
        params: Dict[str, Any] = {}
        if since_id:
            params["since_id"] = since_id
        if until_id:
            params["until_id"] = until_id
        if max_results is not None:
            params["max_results"] = max_results
        if pagination_token:
            params["pagination_token"] = pagination_token
        if exclude:
            params["exclude"] = ",".join(exclude)
        if start_time:
            params["start_time"] = start_time
        if end_time:
            params["end_time"] = end_time
        if tweet_fields:
            params["tweet.fields"] = ",".join(tweet_fields)

        # Build headers in case of bearer usage
        headers = self.build_headers()

        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "url": f"{self.base_url}/users/{user_id}/tweets",
                "headers": headers,
                "params": params,
                "note": "This is a dry run. Wire up or use live call when ready.",
            }

        url = urljoin(self.base_url + '/', f"users/{user_id}/tweets")

        # Prefer Bearer when available for this endpoint
        if self.creds.has_app_bearer:
            try:
                resp = requests.get(url, params=params, headers={"Authorization": f"Bearer {self.creds.app_bearer_token}"}, timeout=30)
            except requests.RequestException as e:
                return {"success": False, "error": f"Network error: {e}"}

            try:
                data = resp.json()
            except ValueError:
                data = {"raw": resp.text}

            if 200 <= resp.status_code < 300:
                return {"success": True, "status": resp.status_code, "data": data}
            else:
                return {
                    "success": False,
                    "status": resp.status_code,
                    "error": data if isinstance(data, dict) else {"message": data},
                }

        # Fallback to OAuth1 user context
        if self.creds.has_oauth1:
            auth = OAuth1(
                self.creds.api_key,
                self.creds.api_key_secret,
                self.creds.access_token,
                self.creds.access_token_secret,
                signature_type='auth_header',
            )
            try:
                resp = requests.get(url, params=params, auth=auth, timeout=30)
            except requests.RequestException as e:
                return {"success": False, "error": f"Network error: {e}"}

            try:
                data = resp.json()
            except ValueError:
                data = {"raw": resp.text}

            if 200 <= resp.status_code < 300:
                return {"success": True, "status": resp.status_code, "data": data}
            else:
                return {
                    "success": False,
                    "status": resp.status_code,
                    "error": data if isinstance(data, dict) else {"message": data},
                }

        mode = (
            "none"
        )
        return {
            "success": False,
            "error": (
                "GET /2/users/{id}/tweets requires either an app bearer token (APP_BEARER_TOKEN) "
                "or OAuth 1.0a user context (API_KEY/API_KEY_SECRET + ACCESS_TOKEN/ACCESS_TOKEN_SECRET)."
            ),
            "auth_mode_detected": mode,
        }

    def like_tweet(
        self,
        tweet_id: str,
        user_id: Optional[str] = None,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        """Like a Tweet on behalf of the authenticated user (POST /2/users/{id}/likes).

        Auth:
            Requires user context. This implementation supports OAuth 1.0a user context.

        Parameters:
            tweet_id: The target Tweet ID to like.
            user_id: Optional explicit user ID; if not provided in live mode, we'll resolve via GET /2/users/me.
            dry_run: When True, returns request details without network calls.

        Response (200, application/json):
            - data.liked: boolean — Whether the like action is reflected as liked=true.
            - errors: object[] — Optional errors array.
        """
        payload = {"tweet_id": tweet_id}
        headers = self.build_headers()

        # Dry run path
        if dry_run:
            url_user = user_id if user_id else ":id"
            return {
                "success": True,
                "dry_run": True,
                "url": f"{self.base_url}/users/{url_user}/likes",
                "headers": headers,
                "payload": payload,
                "note": "Dry run. Live call requires OAuth1 user context; user_id will be resolved from /users/me if omitted.",
            }

        # Live path: must have OAuth1
        if not self.creds.has_oauth1:
            mode = (
                "app_bearer" if self.creds.has_app_bearer else (
                    "oauth2_client" if self.creds.has_oauth2_client else "none"
                )
            )
            return {
                "success": False,
                "error": (
                    "POST /2/users/{id}/likes requires user context. Provide OAuth 1.0a credentials "
                    "(API_KEY/API_KEY_SECRET + ACCESS_TOKEN/ACCESS_TOKEN_SECRET)."
                ),
                "auth_mode_detected": mode,
            }

        # Resolve user id when not provided
        resolved_user_id = user_id
        if not resolved_user_id:
            me = self.get_me(dry_run=False)
            if not me.get("success"):
                return {"success": False, "error": "Failed to resolve authenticated user ID", "details": me}
            data = me.get("data")
            try:
                # Try common shapes
                if isinstance(data, dict) and "id" in data:
                    resolved_user_id = data["id"]
                elif isinstance(data, dict) and "data" in data and isinstance(data["data"], dict) and "id" in data["data"]:
                    resolved_user_id = data["data"]["id"]
            except Exception:
                pass
            if not resolved_user_id:
                return {"success": False, "error": "Could not extract user id from /users/me response", "details": me}

        url = urljoin(self.base_url + '/', f"users/{resolved_user_id}/likes")

        auth = OAuth1(
            self.creds.api_key,
            self.creds.api_key_secret,
            self.creds.access_token,
            self.creds.access_token_secret,
            signature_type='auth_header',
        )
        try:
            resp = requests.post(url, json=payload, auth=auth, timeout=30)
        except requests.RequestException as e:
            return {"success": False, "error": f"Network error: {e}"}

        try:
            data = resp.json()
        except ValueError:
            data = {"raw": resp.text}

        if 200 <= resp.status_code < 300:
            return {"success": True, "status": resp.status_code, "data": data}
        else:
            return {
                "success": False,
                "status": resp.status_code,
                "error": data if isinstance(data, dict) else {"message": data},
            }

    def get_reverse_chronological(
        self,
        user_id: str,
        max_results: Optional[int] = None,
        pagination_token: Optional[str] = None,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        """Get reverse-chronological timeline for a given user (GET /2/users/{id}/timelines/reverse_chronological).

        Requires user context (OAuth1). App-only bearer is typically not sufficient for this endpoint.

        Response (200, application/json):
            The request has succeeded. Returns an object with a non-empty `data` array of Tweet objects.

            Tweet object common fields include (when requested via tweet.fields):
            - attachments: object — Types of attachments present in the Tweet.
            - author_id: string — Author's user ID (e.g., "2244994945").
            - community_id: string — Community identifier.
            - context_annotations: object[] — Context annotations for the Tweet.
            - conversation_id: string — Conversation root Tweet ID (e.g., "1346889436626259968").
            - created_at: string<date-time> — Creation timestamp (e.g., "2021-01-06T18:40:40.000Z").
            - display_text_range: integer[2] — Start (inclusive) and end (exclusive) indices of displayed text.
            - edit_controls: object — Edit window info and related metadata.
            - edit_history_tweet_ids: string[] — IDs in the edit chain.
            - entities: object — Entities such as hashtags, mentions, urls.
            - geo: object — Location info if provided.
            - id: string — Tweet ID as string.
            - in_reply_to_user_id: string — User ID this Tweet is replying to.
            - lang: string — BCP47 language tag (e.g., "en").
            - non_public_metrics: object — Nonpublic engagement metrics.
            - note_tweet: object — Full content for long-form Tweets.
            - organic_metrics: object — Organic nonpublic engagement metrics.
            - possibly_sensitive: boolean — Whether URLs/content are marked sensitive.
            - promoted_metrics: object — Promoted nonpublic engagement metrics.
            - public_metrics: object — Public engagement metrics.
            - referenced_tweets: object[] — Referenced Tweets (retweets, quotes, replies).
            - reply_settings: enum<string> — Who can reply (everyone, mentioned_users, subscribers, verified, following, other).
            - scopes: object — Scopes for this Tweet.
            - source: string — Deprecated.
            - suggested_source_links: object[] — Suggested source links.
            - text: string — Tweet text content.
            - username: string — The user's handle.
            - withheld: object — Withholding details, if any.
        """
        params: Dict[str, Any] = {}
        if max_results is not None:
            params["max_results"] = max_results
        if pagination_token:
            params["pagination_token"] = pagination_token

        headers = self.build_headers()

        if dry_run:
            return {
                "success": True,
                "dry_run": True,
                "url": f"{self.base_url}/users/{user_id}/timelines/reverse_chronological",
                "headers": headers,
                "params": params,
                "note": "This is a dry run. Live calls require OAuth1 user context.",
            }

        url = urljoin(self.base_url + '/', f"users/{user_id}/timelines/reverse_chronological")

        if self.creds.has_oauth1:
            auth = OAuth1(
                self.creds.api_key,
                self.creds.api_key_secret,
                self.creds.access_token,
                self.creds.access_token_secret,
                signature_type='auth_header',
            )
            try:
                resp = requests.get(url, params=params, auth=auth, timeout=30)
            except requests.RequestException as e:
                return {"success": False, "error": f"Network error: {e}"}

            try:
                data = resp.json()
            except ValueError:
                data = {"raw": resp.text}

            if 200 <= resp.status_code < 300:
                return {"success": True, "status": resp.status_code, "data": data}
            else:
                return {
                    "success": False,
                    "status": resp.status_code,
                    "error": data if isinstance(data, dict) else {"message": data},
                }

        return {
            "success": False,
            "error": (
                "GET /2/users/{id}/timelines/reverse_chronological requires user context. "
                "Provide OAuth 1.0a credentials (API_KEY/API_KEY_SECRET + ACCESS_TOKEN/ACCESS_TOKEN_SECRET)."
            ),
            "auth_mode_detected": (
                "oauth1" if self.creds.has_oauth1 else (
                    "app_bearer" if self.creds.has_app_bearer else (
                        "oauth2_client" if self.creds.has_oauth2_client else "none"
                    )
                )
            ),
        }

    def get_my_reverse_chronological(
        self,
        max_results: Optional[int] = None,
        pagination_token: Optional[str] = None,
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        """Get reverse-chronological timeline for the authenticated user.

        Live mode resolves the user ID via GET /2/users/me (OAuth1) then requests the timeline.

        Response (200, application/json):
            The request has succeeded. Returns an object with a non-empty `data` array of Tweet objects.

            Tweet object common fields include (when requested via tweet.fields):
            - attachments, author_id, community_id, context_annotations, conversation_id, created_at,
              display_text_range, edit_controls, edit_history_tweet_ids, entities, geo, id,
              in_reply_to_user_id, lang, non_public_metrics, note_tweet, organic_metrics,
              possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets, reply_settings,
              scopes, source (deprecated), suggested_source_links, text, username, withheld.
        """
        if dry_run:
            headers = self.build_headers()
            params: Dict[str, Any] = {}
            if max_results is not None:
                params["max_results"] = max_results
            if pagination_token:
                params["pagination_token"] = pagination_token
            return {
                "success": True,
                "dry_run": True,
                "url": f"{self.base_url}/users/:id/timelines/reverse_chronological",
                "headers": headers,
                "params": params,
                "note": "Dry run. Live call will resolve :id via /users/me using OAuth1.",
            }

        # Live: resolve user id
        me = self.get_me(dry_run=False)
        if not me.get("success"):
            return {
                "success": False,
                "error": "Failed to resolve authenticated user ID",
                "details": me,
            }
        try:
            user_id = me["data"]["data"]["id"] if "data" in me.get("data", {}) else me["data"]["id"]
        except Exception:
            # Attempt to normalize common shapes
            data = me.get("data")
            if isinstance(data, dict) and "data" in data and isinstance(data["data"], dict) and "id" in data["data"]:
                user_id = data["data"]["id"]
            elif isinstance(data, dict) and "id" in data:
                user_id = data["id"]
            else:
                return {"success": False, "error": "Could not extract user id from /users/me response", "details": me}

        return self.get_reverse_chronological(
            user_id=user_id,
            max_results=max_results,
            pagination_token=pagination_token,
            dry_run=False,
        )


# Default clients
client = GenericClient()
x_client = XClient()

# Export public API
__all__ = ["GenericClient", "client", "XClient", "x_client"]