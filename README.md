# x-mcp-server

Production-ready scaffold for an X (Twitter) toolset exposed by a Model Context Protocol (MCP) server. It includes a client for common endpoints and multiple MCP tools (post, profile, timelines, likes), with safe dry-run support.

## What this project is

- Python package targeting Python 3.13+
- Uses the `mcp` Python package (with CLI extras) to build an MCP-compliant server
- Clean separation between:
	- entry point / server (`src/server.py`)
	- external service client(s) (`src/client.py`)
	- tool implementations (`src/tools/**`)

## Repository structure

```
.
├─ server.py                # MCP server exposing tools over STDIO
├─ pyproject.toml           # Project metadata and dependencies
├─ uv.lock                  # Lockfile (suggests use of the UV package manager)
├─ README.md                # You are here
└─ src/
	├─ client.py             # XClient with OAuth1 posting
	└─ tools/
		└─ func/
			├─ x_post.py              # Tool: post_to_x(text, ...)
			├─ x_me.py                # Tool: get_x_me(...)
			├─ x_get_posts_by_id.py   # Tool: get_posts_by_id(...)
			├─ x_my_timeline.py       # Tool: x_my_timeline(...)
			└─ x_like.py              # Tool: like_tweet_by_tweetId(...)
```

## Current behavior

- Provides an OAuth 1.0a–capable client for X APIs and a collection of MCP tools.
- All tools support `dry_run=True` to return the assembled request (URL, headers, params/payload) without making a network call.

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

This starts a FastMCP server named `x-post` that exposes the tools below over STDIO.

With UV (recommended):
```powershell
uv run src/server.py
```

With Python directly:
```powershell
python src/server.py
```

Use any MCP-compatible client to call the tools documented below.

## Available MCP tools

Each tool supports `dry_run` (default True) to safely preview the outbound request.

1) x_post
	 - Action: Post text to X (Tweets)
	 - Endpoint: POST /2/tweets
	 - Inputs:
		 - text (string, required)
		 - media_url (string, optional)
		 - metadata (object, optional)
		 - dry_run (boolean, default true)
	 - Auth: Requires OAuth1 user context for live posting

2) x_me
	 - Action: Get the authenticated user's profile
	 - Endpoint: GET /2/users/me
	 - Inputs:
		 - user_fields (string[]), expansions (string[]), tweet_fields (string[]), dry_run (boolean)
	 - Auth: Requires OAuth1 user context for live calls

3) get_posts_by_id
	 - Action: Get posts authored by a specific user by ID
	 - Endpoint: GET /2/users/{id}/tweets
	 - Inputs:
		 - user_id (string, required)
		 - since_id, until_id, max_results, pagination_token, exclude (string[]), start_time, end_time, tweet_fields (string[]), dry_run
	 - Auth: Prefers App Bearer (read), falls back to OAuth1

4) x_my_timeline (and alias get__my_timeline)
	 - Action: Get reverse-chronological timeline for the authenticated user
	 - Endpoint: GET /2/users/:id/timelines/reverse_chronological
	 - Inputs:
		 - limit (integer >= 1), pagination (string), dry_run (boolean)
	 - Auth: Requires OAuth1 user context for live calls (resolves :id via /users/me)

5) like_tweet_by_tweetId
	 - Action: Like a Tweet by ID on behalf of the authenticated user
	 - Endpoint: POST /2/users/{id}/likes
	 - Inputs:
		 - tweet_id (string, required)
		 - user_id (string, optional; if omitted in live mode, resolved via /users/me)
		 - dry_run (boolean)
	 - Auth: Requires OAuth1 user context for live calls

### Use the functions directly (non-MCP)

A minimal example:

```python
from src.tools.func.x_post import post_to_x

# Dry run (no network):
print(post_to_x(text="Hello from MCP tool", dry_run=True))

# Live post (requires OAuth1 credentials and write permission):
print(post_to_x(text="Posting via MCP tool", dry_run=False))

# Dry-run examples for other tools
from src.tools.func.x_me import get_x_me
from src.tools.func.x_get_posts_by_id import get_posts_by_id
from src.tools.func.x_my_timeline import x_my_timeline
from src.tools.func.x_like import like_tweet_by_tweetId

print(get_x_me(dry_run=True))
print(get_posts_by_id(user_id="2244994945", max_results=5, dry_run=True))
print(x_my_timeline(limit=25, dry_run=True))
print(like_tweet_by_tweetId(tweet_id="1346889436626259968", dry_run=True))
```

Notes:
- Live posting and write actions require OAuth 1.0a user context credentials and an X plan that permits write access.
- Read endpoints may work with App Bearer; user-context endpoints require OAuth1.
- All tools support `dry_run=True` so you can preview requests without hitting the network.

## Roadmap to a working MCP server

1. Add an MCP server in `main.py` (or `src/server.py`) and register `post_to_x`.
2. OAuth1 live posting path is implemented in `src/client.py`; extend for media uploads as needed.
3. Expose the tool to the MCP runtime (decorator or registration – per MCP SDK version).
4. Document required environment variables/secrets (see `.env.example`).
5. Add rate limit handling and retries for production workloads.

## Notes

- The Python version in `pyproject.toml` is set to `>=3.13`. If your environment uses an earlier version, either install Python 3.13 or relax this constraint.
- Keep your real `.env` out of version control. Only commit `.env.example`.

