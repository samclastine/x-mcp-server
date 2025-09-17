"""
Client module for external APIs used by this MCP server.

Includes:
- GenericClient: Basic placeholder for demonstration
- XClient: Auth-aware client for X (Twitter) API, sourcing credentials from env
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional

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


# Default clients
client = GenericClient()
x_client = XClient()

# Export public API
__all__ = ["GenericClient", "client", "XClient", "x_client"]