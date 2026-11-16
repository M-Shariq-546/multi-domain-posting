from dataclasses import dataclass
from typing import Protocol

import httpx


@dataclass(frozen=True)
class PostReceipt:
    posted_url: str | None
    public_access: bool | None


class Poster(Protocol):
    name: str

    async def post(self, message: str, client: httpx.AsyncClient) -> PostReceipt: ...


def require_credentials(**values: str | None) -> None:
    missing = [name for name, value in values.items() if not value]
    if missing:
        raise RuntimeError(f"Missing required configuration: {', '.join(missing)}")


def provider_error(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        payload = None
    if isinstance(payload, dict):
        error = payload.get("error_description") or payload.get("error") or payload.get("message")
        if isinstance(error, str) and error:
            return f"HTTP {response.status_code}: {error[:300]}"
    return f"HTTP {response.status_code} from platform API"


async def ensure_success(response: httpx.Response) -> None:
    if response.is_error:
        raise RuntimeError(provider_error(response))
