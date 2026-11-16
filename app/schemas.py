import re
from datetime import date, time
from typing import Literal

from pydantic import AnyHttpUrl, BaseModel, ConfigDict, Field, TypeAdapter, field_validator

_URL_PATTERN = re.compile(r"(?:https?://|ftp://|www\.)[^\s<>\"']+", re.IGNORECASE)
_TRAILING_PUNCTUATION = ".,!?;:)]}"
_HTTP_URL_ADAPTER = TypeAdapter(AnyHttpUrl)


class PostingRequest(BaseModel):
    message: str = Field(min_length=1, max_length=200)

    @field_validator("message")
    @classmethod
    def require_one_valid_cta_link(cls, message: str) -> str:
        links = [match.rstrip(_TRAILING_PUNCTUATION) for match in _URL_PATTERN.findall(message)]
        if len(links) != 1:
            raise ValueError("message must contain exactly one CTA link")
        if not links[0].lower().startswith(("http://", "https://")):
            raise ValueError("CTA link must use http or https")
        try:
            _HTTP_URL_ADAPTER.validate_python(links[0])
        except ValueError as exc:
            raise ValueError("CTA link must be a valid http or https URL") from exc
        return message


class PlatformResult(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    platform: str
    status: Literal["success", "failed"]
    posted_url: str | None
    public_access: bool | None
    date: date | None
    time: time | None
    error: str | None


class PostingResponse(BaseModel):
    success: bool
    results: list[PlatformResult]
