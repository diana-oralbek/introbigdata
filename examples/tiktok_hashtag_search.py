import os
from typing import Any, Dict, List, Optional

from ensembledata.api import EDClient


def fetch_hashtag_posts_manual(client: EDClient, hashtag: str, max_pages: int = 5) -> List[Dict[str, Any]]:
    """Fetch posts using the basic Hashtag Search with manual cursor handling.

    A safety cap of max_pages prevents excessive calls by default.
    """
    cursor: Optional[int] = 0
    all_posts: List[Dict[str, Any]] = []

    for _ in range(max_pages):
        result = client.tiktok.hashtag_search(hashtag=hashtag, cursor=cursor)
        posts = result.data.get("data", [])
        all_posts.extend(posts)

        next_cursor = result.data.get("nextCursor")
        if next_cursor is None:
            break
        cursor = next_cursor

    return all_posts


def fetch_hashtag_posts_full(client: EDClient, hashtag: str, max_cursor: Optional[int] = None, days: Optional[int] = None) -> List[Dict[str, Any]]:
    """Fetch posts using the Full Hashtag Search (automatic cursor handling)."""
    result = client.tiktok.full_hashtag_search(hashtag=hashtag, max_cursor=max_cursor, days=days)
    return result.data.get("data", [])


def main() -> None:
    # Configure token: prefer env var, otherwise paste below
    pasted_token = "d27oMjsSy7Lw4G8K"
    token = os.environ.get("ENSEMBLEDATA_API_TOKEN", pasted_token)
    if not token or token == "PASTE_YOUR_TOKEN_HERE":
        raise SystemExit(
            "No API token provided. Set ENSEMBLEDATA_API_TOKEN or paste it in pasted_token."
        )

    client = EDClient(token)

    hashtag = os.environ.get("ED_HASHTAG", "trending")
    print(f"Using hashtag: #{hashtag}")

    # 1) Basic Hashtag Search with manual cursor handling
    max_pages_env = os.environ.get("ED_MAX_PAGES")
    try:
        max_pages = int(max_pages_env) if max_pages_env else 5
    except ValueError:
        max_pages = 5
    print(f"\n[Manual Cursor] Fetching up to {max_pages} pages (set ED_MAX_PAGES to change)...")
    posts_manual = fetch_hashtag_posts_manual(client, hashtag=hashtag, max_pages=max_pages)
    print(f"Manual cursor posts fetched: {len(posts_manual)}")
    if posts_manual:
        print("Sample manual result (first post):")
        print(posts_manual[0])

    # 2) Full Hashtag Search with automatic cursor handling
    print("\n[Full Hashtag Search] Fetching with max_cursor=2000, days=7...")
    posts_full = fetch_hashtag_posts_full(client, hashtag=hashtag, max_cursor=2_000, days=7)
    print(f"Full search posts fetched: {len(posts_full)}")
    if posts_full:
        print("Sample full result (first post):")
        print(posts_full[0])


if __name__ == "__main__":
    main()


