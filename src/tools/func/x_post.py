"""
Tool: post content to X (Twitter) using configured credentials.

This function is designed to be registered as an MCP tool. It uses XClient to
assemble an authenticated request and currently supports a safe dry-run mode.
"""

from typing import Optional, Dict, Any

from ...client import XClient
from ...config import load_credentials, require_any_auth


def post_to_x(text: str, media_url: Optional[str] = None, metadata: Optional[Dict[str, Any]] = None,
			  dry_run: bool = True) -> Dict[str, Any]:
	"""Post content to X (dry-run by default).

	Parameters:
		text: The text content of the post.
		media_url: Optional URL to media to include.
		metadata: Optional extra parameters (e.g., visibility flags).
		dry_run: When True, returns the request details without performing a network call.

	Returns:
		A response with request details (dry_run=True) or, once implemented, the API response.
	"""
	creds = load_credentials()
	require_any_auth(creds)

	client = XClient(creds=creds)
	return client.post_status(text=text, media_url=media_url, metadata=metadata, dry_run=dry_run)


__all__ = ["post_to_x"]

