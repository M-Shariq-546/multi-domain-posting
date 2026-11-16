import httpx

from app.platforms.base import PostReceipt, ensure_success, require_credentials
from app.config import Settings


class MastodonPoster:
    name = "Mastodon"

    def __init__(self, settings: Settings):
        self.api_url = settings.mastodon_api_url
        self.access_token = settings.mastodon_access_token

    async def post(self, message: str, client: httpx.AsyncClient) -> PostReceipt:
        require_credentials(MASTODON_API_URL=self.api_url, MASTODON_ACCESS_TOKEN=self.access_token)
        response = await client.post(
            self.api_url,
            headers={"Authorization": f"Bearer {self.access_token}"},
            data={"status": message, "visibility": "public"},
        )
        await ensure_success(response)
        data = response.json()
        return PostReceipt(data.get("url"), True)
