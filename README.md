# x-mcp-server

A minimal Model Context Protocol (MCP) server skeleton in Python. The layout is set up to expose "tools" (functions) to an MCP client. The naming and placeholder file `x_post.py` suggest this server will eventually include a tool for posting to the X (Twitter) API, but the implementation is left for you to fill in.

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
├─ main.py                  # Current entrypoint (prints a greeting)
├─ pyproject.toml           # Project metadata and dependencies
├─ uv.lock                  # Lockfile (suggests use of the UV package manager)
├─ README.md                # You are here
└─ src/
	├─ client.py             # Placeholder GenericClient for external APIs
	└─ tools/
		└─ func/
			└─ x_post.py       # Placeholder for a tool (e.g., post to X)
```

## Current behavior

- Running `python main.py` prints: `Hello from x-mcp-server!`
- There is no server wiring yet; `mcp` is declared as a dependency and ready to be used to expose tools.
- `src/client.py` provides a `GenericClient` with a stubbed `make_request` method you can adapt for real APIs.
- `src/tools/func/x_post.py` contains a stub you can flesh out with the logic to post to an external service (e.g., X/Twitter).

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

You should see a greeting in the console.

## Configure authentication for X API

Anyone can bring their own X API credentials and use this MCP server.

1) Obtain credentials (summary from X docs):
	 - Create a developer account and an App (Project + App)
	 - Save these credentials securely:
		 - API Key and Secret (OAuth 1.0a)
		 - Access Token and Secret (OAuth 1.0a user context)
		 - Client ID and Client Secret (OAuth 2.0)
		 - App-only Access Token (Bearer) for public data

2) Create a `.env` file from the template and fill in values:

```powershell
Copy-Item .env.example .env
```

Supported environment variables (prefix `X_API_`):
- `API_KEY`
- `API_KEY_SECRET`
- `ACCESS_TOKEN`
- `ACCESS_TOKEN_SECRET`
- `CLIENT_ID`
- `CLIENT_SECRET`
- `APP_BEARER_TOKEN`

You only need one of these auth modes to start. For simple read-only/testing, `APP_BEARER_TOKEN` is easiest. For posting on behalf of a user, provide the OAuth 1.0a token set (API key/secret + access token/secret).

3) Validate setup with a dry run:

You can import and call the tool directly, or once the MCP server is wired, call it via the MCP client. For now, do a quick Python REPL test:

To avoid quoting issues in PowerShell, you can use the provided smoke script:

```powershell
python .\scripts\smoke_post.py "Hello X from MCP!"
```

Expected: a JSON blob showing the assembled URL, headers, and payload, without making a network request.

### Live posting (OAuth 1.0a user context)

Requirements:
- X OAuth 1.0a credentials in `.env`:
	- `X_API_API_KEY`
	- `X_API_API_KEY_SECRET`
	- `X_API_ACCESS_TOKEN`
	- `X_API_ACCESS_TOKEN_SECRET`
- App permissions that allow posting (tweet.write)

Run (be careful: this will attempt to post):

```powershell
python .\scripts\smoke_post.py "Your live tweet text" --no-dry-run
```

Notes:
- If only an app bearer token or OAuth2 client credentials are configured, the script will return a helpful error since posting requires user context.
- Consider rate limits and error responses from the X API; failures will include status codes and response JSON when available.

## Roadmap to a working MCP server

1. Add an MCP server in `main.py` (or `src/server.py`) that registers tool functions from `src/tools`.
2. Implement `x_post.post_to_x(...)` with real API calls using `src/client.py` (add auth, error handling, rate limits, etc.). OAuth1 request signing and/or OAuth2 token exchange will be required depending on auth mode. (OAuth1 live posting path is implemented.)
3. Expose the tool to the MCP runtime (e.g., via `@mcp.tool` decorator or explicit registration, depending on the SDK API version).
4. Document required environment variables/secrets for the external API.
5. Add a simple test or script to smoke-test the tool in isolation.

## Notes

- The Python version in `pyproject.toml` is set to `>=3.13`. If your environment uses an earlier version, either install Python 3.13 or relax this constraint.
- The README will evolve as the MCP server wiring and tools are implemented.

