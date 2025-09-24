# Deploying to FastMCP Cloud

This repository is ready for FastMCP Cloud.

## Requirements
- Python 3.13 (configured in `pyproject.toml`)
- Dependencies: managed via `pyproject.toml` (Cloud will auto-install)
- Entry point server object exported as `app`

## Entry points
- `fastmcp_server.py:app` (primary)
- `app.py:app` (alias for convenience)

Cloud will ignore any `if __name__ == "__main__"` blocks.

## Environment variables (X API)
Set these in the Cloud environment:
- `X_API_API_KEY`
- `X_API_API_KEY_SECRET`
- `X_API_ACCESS_TOKEN`
- `X_API_ACCESS_TOKEN_SECRET`

## Minimal example (for reference only)
```python
from fastmcp.server.server import FastMCP
app = FastMCP("my-server")
@app.tool()
def hello(name: str) -> str:
    return f"Hello, {name}"
```

## Local validation
- Inspect tools:
```powershell
uv run fastmcp inspect fastmcp_server.py
```
- Dev + Inspector:
```powershell
uv run fastmcp dev fastmcp_server.py --python 3.13 --with httpx
```
- Direct runners (no CLI nesting):
```powershell
uv run python .\scripts\run_http.py
uv run python .\scripts\run_stdio.py
```
