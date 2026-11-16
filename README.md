# Automated Multi-Platform Posting API

A FastAPI service that accepts one short message and attempts to publish it to Mastodon, Bluesky, X, Reddit, and Tumblr. Each platform runs independently, so one failure does not stop the others.

## Setup

Requires Python 3.10 or newer.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Fill in the platform URLs, URL templates, and credentials in `.env`. `.env.example` contains the default API endpoints and public post URL templates; each can be overridden without changing code. Credentials and endpoints are optional per platform; a platform missing required settings returns a failed result while the others are still attempted. Use platform-issued tokens/app passwords and never commit `.env`.

## Run

```bash
uvicorn app.main:app --host 0.0.0.0 --port 4000
```

Interactive API documentation: <http://localhost:4000/docs>

## Request

```bash
curl -X POST http://localhost:4000/posting \
  -H 'Content-Type: application/json' \
  -d '{"message":"Check out our latest update https://example.com"}'
```

Messages must be at most 200 characters and contain exactly one valid HTTP(S) URL. Platform selection is configured inside the application.

## Response

The API returns one result per platform with its status, returned post URL (if supplied by that API), public-access certainty, UTC posting date/time, and any error. `public_access` is `null` when the platform API does not let the application verify public visibility. Overall `success` is true if at least one platform accepted the post.

## Platform setup notes

- **Mastodon:** set the instance URL and an access token with `write:statuses`.
- **Bluesky:** use an app password, not your account password.
- **X:** set a user access token with posting permissions. `X_USERNAME` is needed to construct a post URL.
- **Reddit:** provide an OAuth access token and the destination subreddit. Reddit may reject posts due to subreddit rules, account restrictions, or API limits.
- **Tumblr:** provide OAuth 1.0a consumer key/secret, token/secret, and blog hostname. Its endpoint template uses `{blog_identifier}`.

Bluesky's public post URL template uses `{handle}` and `{rkey}`. X's template uses `{username}` and `{post_id}`. These template values are filled from platform API responses and environment configuration at runtime.

API availability, scopes, account permissions, and provider policies can change; confirm access for your account before relying on live posting.

## Tests

```bash
pytest
```
