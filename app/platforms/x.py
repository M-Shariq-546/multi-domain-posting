import httpx

from app.platforms.base import PostReceipt, ensure_success, require_credentials
from app.config import Settings


class XPoster:
    name = "X"

    def __init__(self, settings: Settings):
        self.api_url = settings.x_api_url
        self.post_url_template = settings.x_post_url_template
        self.access_token = settings.x_access_token
        self.username = settings.x_username

    async def post(self, message: str, client: httpx.AsyncClient) -> PostReceipt:
        require_credentials(
            X_API_URL=self.api_url,
            X_ACCESS_TOKEN=self.access_token,
        )
        response = await client.post(
            self.api_url,
            headers={"Authorization": f"Bearer {self.access_token}"},
            json={"text": message},
        )
        await ensure_success(response)
        post_id = response.json()["data"]["id"]
        url = (
            self.post_url_template.format(username=self.username, post_id=post_id)
            if self.username and self.post_url_template
            else None
        )
        return PostReceipt(url, None)
