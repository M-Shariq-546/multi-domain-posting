from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    mastodon_api_url: str | None = None
    mastodon_access_token: str | None = None

    bluesky_xrpc_url: str | None = None
    bluesky_post_url_template: str | None = None
    bluesky_identifier: str | None = None
    bluesky_app_password: str | None = None

    x_api_url: str | None = None
    x_post_url_template: str | None = None
    x_access_token: str | None = None
    x_username: str | None = None

    reddit_submit_url: str | None = None
    reddit_access_token: str | None = None
    reddit_subreddit: str | None = None
    reddit_title: str = "Update"

    tumblr_post_url_template: str | None = None
    tumblr_consumer_key: str | None = None
    tumblr_consumer_secret: str | None = None
    tumblr_token: str | None = None
    tumblr_token_secret: str | None = None
    tumblr_blog_identifier: str | None = None

    request_timeout_seconds: float = 20.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
