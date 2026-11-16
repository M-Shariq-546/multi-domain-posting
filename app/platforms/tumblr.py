import base64
import hashlib
import hmac
import secrets
import time
from urllib.parse import quote

import httpx

from app.platforms.base import PostReceipt, ensure_success, require_credentials
from app.config import Settings


class TumblrPoster:
    name = "Tumblr"

    def __init__(self, settings: Settings):
        self.post_url_template = settings.tumblr_post_url_template
        self.consumer_key = settings.tumblr_consumer_key
        self.consumer_secret = settings.tumblr_consumer_secret
        self.token = settings.tumblr_token
        self.token_secret = settings.tumblr_token_secret
        self.blog_identifier = settings.tumblr_blog_identifier

    @staticmethod
    def _encoded(value: str) -> str:
        return quote(value, safe="~-._")

    def _authorization_header(self, url: str, body: dict[str, str]) -> str:
        oauth = {
            "oauth_consumer_key": self.consumer_key or "",
            "oauth_nonce": secrets.token_hex(16),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time.time())),
            "oauth_token": self.token or "",
            "oauth_version": "1.0",
        }
        parameters = sorted(
            (self._encoded(key), self._encoded(value))
            for key, value in [*oauth.items(), *body.items()]
        )
        normalized = "&".join(f"{key}={value}" for key, value in parameters)
        base_string = "&".join(
            (
                "POST",
                self._encoded(url),
                self._encoded(normalized),
            )
        )
        signing_key = f"{self._encoded(self.consumer_secret or '')}&{self._encoded(self.token_secret or '')}"
        digest = hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
        oauth["oauth_signature"] = base64.b64encode(digest).decode()
        header_parameters = sorted(
            (self._encoded(key), self._encoded(value))
            for key, value in oauth.items()
        )
        return "OAuth " + ", ".join(f'{key}="{value}"' for key, value in header_parameters)

    async def post(self, message: str, client: httpx.AsyncClient) -> PostReceipt:
        require_credentials(
            TUMBLR_POST_URL_TEMPLATE=self.post_url_template,
            TUMBLR_CONSUMER_KEY=self.consumer_key,
            TUMBLR_CONSUMER_SECRET=self.consumer_secret,
            TUMBLR_TOKEN=self.token,
            TUMBLR_TOKEN_SECRET=self.token_secret,
            TUMBLR_BLOG_IDENTIFIER=self.blog_identifier,
        )
        url = self.post_url_template.format(blog_identifier=self.blog_identifier)
        body = {"type": "text", "body": message, "state": "published"}
        response = await client.post(
            url,
            headers={"Authorization": self._authorization_header(url, body)},
            data=body,
        )
        await ensure_success(response)
        payload = response.json()
        if payload.get("meta", {}).get("status", 500) >= 400:
            raise RuntimeError("Tumblr rejected the post")
        result = payload.get("response", {})
        return PostReceipt(result.get("post_url"), None)
