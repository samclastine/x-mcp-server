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

_REPO_ROOT = _Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in _sys.path:
    _sys.path.insert(0, str(_REPO_ROOT))

from src.tools.func.x_post import post_to_x


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


if __name__ == "__main__":
    # IMPORTANT: Do not print to STDOUT; FastMCP owns the protocol stream.
    mcp.run()
