# x-mcp-server

Production-ready scaffold for an X (Twitter) posting tool intended to be exposed by a Model Context Protocol (MCP) server. It includes a small client for OAuth 1.0a signed requests and a tool function you can register in your MCP server.

## What this project is

- Python package targeting Python 3.13+
- Uses the `mcp` Python package (with CLI extras) to build an MCP-compliant server
- Clean separation between:
  - entry point (`main.py`)
  - external service client(s) (`src/client.py`)
  - tool implementations (`src/tools/**`)

## Repository structure

```
.
├─ main.py                  # Entrypoint placeholder
├─ pyproject.toml           # Project metadata and dependencies
├─ uv.lock                  # Lockfile (suggests use of the UV package manager)
├─ README.md                # You are here
└─ src/
	├─ client.py             # XClient with OAuth1 posting
	└─ tools/
		└─ func/
			└─ x_post.py       # Tool: post_to_x(text, ...)
```

## Current behavior

- Provides an OAuth 1.0a–signed client for posting to X using user context.
- Exposes a tool function `post_to_x(text, media_url=None, metadata=None, dry_run=True)` you can register in an MCP server.
- When `dry_run=True` (default), it returns the request details without making a network call.
- When `dry_run=False` and OAuth1 credentials are configured, it attempts to POST to `https://api.x.com/2/tweets`.

## Tech stack

- Python >= 3.13
- [`mcp[cli]`](https://pypi.org/project/mcp/) (declared in `pyproject.toml`)
- Optional: [UV](https://github.com/astral-sh/uv) for dependency management (lockfile present)

## Getting started (local)

1) Create a virtual environment and install deps (pick one):

PowerShell (pip):

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
```

PowerShell (UV):

```powershell
uv venv --python 3.13
.\.venv\Scripts\Activate.ps1
uv sync
```

2) Run the current entry point:

```powershell
python .\main.py
```

This repository ships a tool and client; the `main.py` is a placeholder. You’ll typically import and register the tool in your MCP server process.

## Configure authentication for X API (step by step)

Anyone can bring their own X API credentials and use this tool.

1) Sign up and create an App
- Go to the X Developer Portal and create a Project + App.
- In User authentication settings, enable OAuth 1.0a and set App permissions to “Read and write”.
- Provide a Callback URL (e.g., http://localhost/callback) and Website URL if prompted.

2) Generate and save credentials (OAuth 1.0a user context)
- API Key → `X_API_API_KEY`
- API Key Secret → `X_API_API_KEY_SECRET`
- Access Token → `X_API_ACCESS_TOKEN`
- Access Token Secret → `X_API_ACCESS_TOKEN_SECRET`

3) Create your local `.env`
```powershell
Copy-Item .env.example .env
# Open .env and paste the four OAuth1 values above
```

4) Important: If you change App permissions to include write, regenerate the Access Token & Secret so they inherit write access, and update your `.env`.

Optional variables:
- OAuth 2.0 client (for future flows): `X_API_CLIENT_ID`, `X_API_CLIENT_SECRET`
- App-only bearer token (read-only): `X_API_APP_BEARER_TOKEN`

## Using the tool in your MCP server

You can run the included MCP server that exposes `x_post` over STDIO, or import the function directly.

### Run the included MCP server

This starts a FastMCP server named `x-post` that exposes the `x_post` tool.

With UV (recommended):
```powershell
uv run src/server.py
```

With Python directly:
```powershell
python src/server.py
```

Use any MCP-compatible client to call the `x_post` tool with parameters:
- text (str, required)
- media_url (str, optional)
- metadata (object, optional)
- dry_run (bool, default true)

### Use the function directly (non-MCP)

A minimal example:

```python
from src.tools.func.x_post import post_to_x

# Dry run (no network):
print(post_to_x(text="Hello from MCP tool", dry_run=True))

# Live post (requires OAuth1 credentials and write permission):
print(post_to_x(text="Posting via MCP tool", dry_run=False))
```

Notes:
- Posting requires OAuth 1.0a user context credentials and an X plan that permits write access.
- If only a bearer token or OAuth2 client credentials are present, the tool will return a clear error explaining that user context is required for posting.

## Roadmap to a working MCP server

1. Add an MCP server in `main.py` (or `src/server.py`) and register `post_to_x`.
2. OAuth1 live posting path is implemented in `src/client.py`; extend for media uploads as needed.
3. Expose the tool to the MCP runtime (decorator or registration – per MCP SDK version).
4. Document required environment variables/secrets (see `.env.example`).
5. Add rate limit handling and retries for production workloads.

## Notes

- The Python version in `pyproject.toml` is set to `>=3.13`. If your environment uses an earlier version, either install Python 3.13 or relax this constraint.
- Keep your real `.env` out of version control. Only commit `.env.example`.

