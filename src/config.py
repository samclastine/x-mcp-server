"""Configuration loader for X API credentials.

Loads environment variables and optionally reads a .env file during development.
This module centralizes credential names and basic validation.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


def _maybe_load_dotenv() -> None:
    """Attempt to load a .env file in development environments.

    This function is safe to call in production; if python-dotenv isn't installed
    or no .env file exists, it will no-op.
    """
    try:
        from dotenv import load_dotenv  # type: ignore

        # Load .env from project root if present
        load_dotenv()
    except Exception:
        # Silently ignore missing package or other dotenv issues
        pass


ENV_PREFIX = "X_API_"


@dataclass(frozen=True)
class XCredentials:
    """Holds credentials for authenticating to the X API.

    Supported sets per X docs:
    - OAuth 1.0a: API Key/Secret + Access Token/Secret
    - OAuth 2.0: Client ID/Secret (for user access tokens) and/or App-only Access Token
    """

    api_key: Optional[str] = None
    api_key_secret: Optional[str] = None
    access_token: Optional[str] = None
    access_token_secret: Optional[str] = None
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    app_bearer_token: Optional[str] = None  # App-only access token (Bearer)

    @property
    def has_oauth1(self) -> bool:
        return all([
            self.api_key,
            self.api_key_secret,
            self.access_token,
            self.access_token_secret,
        ])

    @property
    def has_app_bearer(self) -> bool:
        return bool(self.app_bearer_token)

    @property
    def has_oauth2_client(self) -> bool:
        return all([
            self.client_id,
            self.client_secret,
        ])


def load_credentials() -> XCredentials:
    """Load credentials from environment variables.

    Environment variables (prefixed with X_API_):
    - API_KEY
    - API_KEY_SECRET
    - ACCESS_TOKEN
    - ACCESS_TOKEN_SECRET
    - CLIENT_ID
    - CLIENT_SECRET
    - APP_BEARER_TOKEN
    """

    _maybe_load_dotenv()

    def g(name: str) -> Optional[str]:
        return os.getenv(f"{ENV_PREFIX}{name}") or None

    return XCredentials(
        api_key=g("API_KEY"),
        api_key_secret=g("API_KEY_SECRET"),
        access_token=g("ACCESS_TOKEN"),
        access_token_secret=g("ACCESS_TOKEN_SECRET"),
        client_id=g("CLIENT_ID"),
        client_secret=g("CLIENT_SECRET"),
        app_bearer_token=g("APP_BEARER_TOKEN"),
    )


def require_any_auth(creds: XCredentials) -> None:
    """Raise a helpful error if no viable auth option is configured."""
    if not (creds.has_oauth1 or creds.has_app_bearer or creds.has_oauth2_client):
        raise RuntimeError(
            "No X API credentials found. Configure one of: "
            "OAuth 1.0a (API_KEY/API_KEY_SECRET + ACCESS_TOKEN/ACCESS_TOKEN_SECRET), "
            "App-only bearer (APP_BEARER_TOKEN), or OAuth2 client (CLIENT_ID/CLIENT_SECRET)."
        )
