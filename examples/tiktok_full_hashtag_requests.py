import os
import sys
from typing import Any, Dict

import requests


ROOT = "https://ensembledata.com/apis"
ENDPOINT = "/tt/hashtag/recent-posts"


def main() -> None:
    # Configure via env vars (preferred) or paste below
    pasted_token = "d27oMjsSy7Lw4G8K"
    token = os.environ.get("ENSEMBLEDATA_API_TOKEN", pasted_token)
    if not token or token == "PASTE_YOUR_TOKEN_HERE":
        raise SystemExit(
            "No API token provided. Set ENSEMBLEDATA_API_TOKEN or paste it in pasted_token."
        )

    hashtag = os.environ.get("ED_HASHTAG", "trending")
    days_str = os.environ.get("ED_DAYS", "90")
    max_cursor_str = os.environ.get("ED_MAX_CURSOR", "10000")
    remap_str = os.environ.get("ED_REMAP_OUTPUT", "true")

    try:
        days = int(days_str)
    except ValueError:
        days = 90

    try:
        max_cursor = int(max_cursor_str)
    except ValueError:
        max_cursor = 10000

    remap_output = str(remap_str).lower() in {"1", "true", "yes"}

    params: Dict[str, Any] = {
        "name": hashtag,
        "days": days,
        "remap_output": remap_output,
        "max_cursor": max_cursor,
        "token": token,
    }

    print(f"Requesting #{hashtag} (days={days}, max_cursor={max_cursor}, remap_output={remap_output})...")
    resp = requests.get(ROOT + ENDPOINT, params=params, timeout=120)

    try:
        data = resp.json()
    except Exception:
        print(f"Non-JSON response, status={resp.status_code}")
        print(resp.text[:1000])
        sys.exit(1)

    if resp.ok:
        # Expecting a JSON structure; print summary and sample
        posts = data.get("data") or data.get("posts") or data
        if isinstance(posts, list):
            print(f"Total posts: {len(posts)}")
            if posts:
                print("First post sample:")
                print(posts[0])
        else:
            print(data)
    else:
        print(f"Error status={resp.status_code}")
        print(data)


if __name__ == "__main__":
    main()


