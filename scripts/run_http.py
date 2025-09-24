"""Run FastMCP server over HTTP transport without CLI nesting.

This avoids the 'Already running asyncio' error by running FastMCP directly
without the fastmcp CLI managing its own event loop.
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path
import asyncio


# Ensure repo root on sys.path so 'fastmcp_server' resolves when run from any CWD
_REPO_ROOT = _Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in _sys.path:
    _sys.path.insert(0, str(_REPO_ROOT))

from fastmcp_server import mcp


if __name__ == "__main__":
    # Run with default stdio transport first
    mcp.run()