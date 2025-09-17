import argparse
import json
import sys
from pathlib import Path

# Ensure repo root is on sys.path so `src` can be imported when running this file directly
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.tools.func.x_post import post_to_x


def main() -> None:
    parser = argparse.ArgumentParser(description="Dry-run post to X via MCP tool")
    parser.add_argument("text", help="Text content of the post")
    parser.add_argument("--media-url", dest="media_url", default=None, help="Optional media URL")
    parser.add_argument("--no-dry-run", dest="dry_run", action="store_false", help="Perform real call (not implemented)")
    args = parser.parse_args()

    resp = post_to_x(text=args.text, media_url=args.media_url, dry_run=args.dry_run)
    print(json.dumps(resp, indent=2))


if __name__ == "__main__":
    main()
