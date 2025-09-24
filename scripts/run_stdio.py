"""Run FastMCP server over STDIO transport without CLI nesting.

Handy when your client expects STDIO but you're driving it yourself.
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

# Ensure repo root on sys.path so 'fastmcp_server' resolves when run from any CWD
_REPO_ROOT = _Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in _sys.path:
    _sys.path.insert(0, str(_REPO_ROOT))

from fastmcp_server import app as mcp

if __name__ == "__main__":
    mcp.run(transport="stdio")
