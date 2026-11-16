"""Reddit Connector for HomePilot Market Intelligence Researcher.

Connects to Reddit via official OAuth 2.0 to extract full post text and nested
comment trees from Irish personal finance and housing discussion communities.
"""

import os
import logging
import re
from typing import Dict, Any, List, Optional
import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)


class RedditConnector:
    """Interface to Reddit Data API using OAuth 2.0.
    
    Supports extracting full post submissions and complete comment sections
    from public discussions without Cloudflare anti-bot blocks.
    """

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        user_agent: Optional[str] = None
    ):
        self.client_id = client_id or os.getenv("REDDIT_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("REDDIT_CLIENT_SECRET", "")
        self.username = username or os.getenv("REDDIT_USERNAME", "")
        self.password = password or os.getenv("REDDIT_PASSWORD", "")
        self.user_agent = user_agent or os.getenv(
            "REDDIT_USER_AGENT",
            f"HomePilot-Market-Intelligence/1.0 (by /u/{self.username or 'homepilot_ie'})"
        )
        self._token: Optional[str] = None
        self.client = httpx.Client(timeout=25.0)

    def is_configured(self) -> bool:
        """Determines if Reddit OAuth credentials are configured."""
        return bool(self.client_id and self.client_secret)

    def _get_access_token(self) -> Optional[str]:
        """Obtains an OAuth access token from Reddit."""
        if self._token:
            return self._token

        if not self.is_configured():
            return None

        try:
            token_url = "https://www.reddit.com/api/v1/access_token"
            auth = (self.client_id, self.client_secret)
            headers = {"User-Agent": self.user_agent}

            if self.username and self.password:
                data = {
                    "grant_type": "password",
                    "username": self.username,
                    "password": self.password
                }
            else:
                data = {"grant_type": "client_credentials"}

            response = self.client.post(token_url, auth=auth, data=data, headers=headers)
            response.raise_for_status()
            token_data = response.json()
            self._token = token_data.get("access_token")
            return self._token
        except Exception as e:
            logger.error(f"Failed to authenticate with Reddit OAuth: {e}")
            return None

    @staticmethod
    def extract_post_id(url_or_id: str) -> Optional[str]:
        """Extracts Reddit post ID from a standard URL or returns the bare ID."""
        if "/" not in url_or_id:
            return url_or_id.strip()

        # Matches /comments/{id}/ pattern
        match = re.search(r"/comments/([a-z0-9]+)", url_or_id.lower())
        if match:
            return match.group(1)
        return None

    def fetch_thread(self, url_or_id: str, max_comments: int = 50) -> Dict[str, Any]:
        """Fetches full post body and nested comment tree for a Reddit thread.
        
        Args:
            url_or_id: Reddit URL (e.g. 'https://reddit.com/r/irishpersonalfinance/comments/1xwxv80/...') or post ID.
            max_comments: Maximum top-level and nested comments to extract (default 50).
        """
        post_id = self.extract_post_id(url_or_id)
        if not post_id:
            return {
                "success": False,
                "error": f"Invalid Reddit URL or post ID: '{url_or_id}'."
            }

        token = self._get_access_token()
        if not token:
            return {
                "success": False,
                "status": "credentials_required",
                "error": "Reddit API credentials (REDDIT_CLIENT_ID and REDDIT_CLIENT_SECRET) are not configured.",
                "post_id": post_id
            }

        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "User-Agent": self.user_agent
            }
            # Look up thread via oauth.reddit.com
            api_url = f"https://oauth.reddit.com/comments/{post_id}"
            res = self.client.get(api_url, headers=headers)
            res.raise_for_status()
            data = res.json()

            # Object 0: Post Submission
            post_data = data[0]["data"]["children"][0]["data"]
            # Object 1: Comment Listing
            comments_listing = data[1]["data"]["children"]

            comments: List[Dict[str, Any]] = []

            def parse_comments(nodes: List[Dict[str, Any]], depth: int = 0):
                for node in nodes:
                    if len(comments) >= max_comments:
                        return
                    c_data = node.get("data", {})
                    body = c_data.get("body", "").strip()
                    if body and body != "[deleted]" and body != "[removed]":
                        comments.append({
                            "depth": depth,
                            "author": "[REDACTED_USER]",
                            "score": c_data.get("score", 0),
                            "body": body
                        })
                    # Recursive replies
                    replies = c_data.get("replies")
                    if isinstance(replies, dict):
                        sub_nodes = replies.get("data", {}).get("children", [])
                        parse_comments(sub_nodes, depth=depth + 1)

            parse_comments(comments_listing)

            return {
                "success": True,
                "platform": "reddit",
                "post_id": post_id,
                "url": f"https://www.reddit.com{post_data.get('permalink', '')}",
                "title": post_data.get("title", ""),
                "subreddit": post_data.get("subreddit", ""),
                "score": post_data.get("score", 0),
                "upvote_ratio": post_data.get("upvote_ratio", 1.0),
                "selftext": post_data.get("selftext", ""),
                "total_comments_in_thread": post_data.get("num_comments", 0),
                "comments_extracted": len(comments),
                "comments": comments
            }
        except Exception as e:
            logger.error(f"Error fetching Reddit thread {post_id}: {e}")
            return {
                "success": False,
                "status": "fetch_error",
                "error": f"Failed to fetch thread {post_id} via Reddit OAuth: {str(e)}",
                "post_id": post_id
            }
