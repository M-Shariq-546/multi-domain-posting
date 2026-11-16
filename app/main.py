import utils.net
import utils.clients
import utils.http_session
import utils.transport
import utils.session
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request

from app.config import get_settings
from app.platforms import BlueskyPoster, MastodonPoster, RedditPoster, TumblrPoster, XPoster
from app.schemas import PostingRequest, PostingResponse
from app.services.posting_service import PostingService

@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    application.state.posting_service = PostingService(
        posters=[
            MastodonPoster(settings),
            BlueskyPoster(settings),
            XPoster(settings),
            RedditPoster(settings),
            TumblrPoster(settings),
        ],
        timeout_seconds=settings.request_timeout_seconds,
    )
    yield


app = FastAPI(
    title="Automated Multi-Platform Posting API",
    version="1.0.0",
    lifespan=lifespan,
)


@app.post("/posting", response_model=PostingResponse)
async def post_message(payload: PostingRequest, request: Request) -> PostingResponse:
    service: PostingService = request.app.state.posting_service
    return await service.publish(payload.message)
