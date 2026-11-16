import re
from datetime import datetime, timezone

import httpx

from app.platforms.base import PostReceipt, ensure_success, require_credentials
from app.config import Settings


class BlueskyPoster:
    name = "Bluesky"

    def __init__(self, settings: Settings):
        self.xrpc_url = (settings.bluesky_xrpc_url or "").rstrip("/")
        self.post_url_template = settings.bluesky_post_url_template
        self.identifier = settings.bluesky_identifier
        self.app_password = settings.bluesky_app_password

    async def post(self, message: str, client: httpx.AsyncClient) -> PostReceipt:
        require_credentials(
            BLUESKY_XRPC_URL=self.xrpc_url,
            BLUESKY_POST_URL_TEMPLATE=self.post_url_template,
            BLUESKY_IDENTIFIER=self.identifier,
            BLUESKY_APP_PASSWORD=self.app_password,
        )
        session_response = await client.post(
            f"{self.xrpc_url}/com.atproto.server.createSession",
            json={"identifier": self.identifier, "password": self.app_password},
        )
        await ensure_success(session_response)
        session = session_response.json()
        did = session["did"]
        access_jwt = session["accessJwt"]

        link = next(
            match.rstrip(".,!?;:)]}")
            for match in re.findall(r"https?://[^\s<>\"']+", message, re.IGNORECASE)
        )
        start = message.index(link)
        byte_start = len(message[:start].encode("utf-8"))
        byte_end = byte_start + len(link.encode("utf-8"))
        record = {
            "$type": "app.bsky.feed.post",
            "text": message,
            "createdAt": datetime.now(timezone.utc).isoformat(),
            "facets": [
                {
                    "index": {"byteStart": byte_start, "byteEnd": byte_end},
                    "features": [{"$type": "app.bsky.richtext.facet#link", "uri": link}],
                }
            ],
        }
        response = await client.post(
            f"{self.xrpc_url}/com.atproto.repo.createRecord",
            headers={"Authorization": f"Bearer {access_jwt}"},
            json={"repo": did, "collection": "app.bsky.feed.post", "record": record},
        )
        await ensure_success(response)
        uri = response.json()["uri"]
        rkey = uri.rsplit("/", 1)[-1]
        handle = session.get("handle") or self.identifier
        return PostReceipt(
            self.post_url_template.format(handle=handle, rkey=rkey),
            True,
        )
