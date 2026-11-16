import asyncio
import logging
from datetime import datetime, timezone

import httpx

from app.platforms.base import Poster
from app.schemas import PlatformResult, PostingResponse

logger = logging.getLogger(__name__)


class PostingService:
    def __init__(self, posters: list[Poster], timeout_seconds: float = 20.0):
        self.posters = posters
        self.timeout_seconds = timeout_seconds

    async def publish(self, message: str) -> PostingResponse:
        async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
            results = await asyncio.gather(
                *(self._publish_one(poster, message, client) for poster in self.posters)
            )
        return PostingResponse(
            success=any(result.status == "success" for result in results),
            results=results,
        )

    async def _publish_one(self, poster: Poster, message: str, client: httpx.AsyncClient) -> PlatformResult:
        try:
            receipt = await poster.post(message, client)
            posted_at = datetime.now(timezone.utc)
            return PlatformResult(
                platform=poster.name,
                status="success",
                posted_url=receipt.posted_url,
                public_access=receipt.public_access,
                date=posted_at.date(),
                time=posted_at.time().replace(tzinfo=None),
                error=None,
            )
        except (httpx.HTTPError, RuntimeError, KeyError, ValueError) as exc:
            return PlatformResult(
                platform=poster.name,
                status="failed",
                posted_url=None,
                public_access=False,
                date=None,
                time=None,
                error=str(exc)[:500] or exc.__class__.__name__,
            )
        except Exception:
            logger.exception("Unexpected error posting to %s", poster.name)
            return PlatformResult(
                platform=poster.name,
                status="failed",
                posted_url=None,
                public_access=False,
                date=None,
                time=None,
                error="Unexpected platform integration error",
            )
