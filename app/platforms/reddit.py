import httpx

from app.platforms.base import PostReceipt, ensure_success, require_credentials
from app.config import Settings


class RedditPoster:
    name = "Reddit"

    def __init__(self, settings: Settings):
        self.submit_url = settings.reddit_submit_url
        self.access_token = settings.reddit_access_token
        self.subreddit = settings.reddit_subreddit
        self.title = settings.reddit_title

    async def post(self, message: str, client: httpx.AsyncClient) -> PostReceipt:
        require_credentials(
            REDDIT_SUBMIT_URL=self.submit_url,
            REDDIT_ACCESS_TOKEN=self.access_token,
            REDDIT_SUBREDDIT=self.subreddit,
        )
        response = await client.post(
            self.submit_url,
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "User-Agent": "automated-multipost/1.0",
            },
            data={
                "api_type": "json",
                "kind": "self",
                "sr": self.subreddit,
                "title": self.title,
                "text": message,
            },
        )
        await ensure_success(response)
        payload = response.json()
        errors = payload.get("json", {}).get("errors", [])
        if errors:
            raise RuntimeError(f"Reddit rejected submission: {errors[0][1]}")
        data = payload.get("json", {}).get("data", {})
        return PostReceipt(data.get("url"), None)
