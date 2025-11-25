# Backend - llms.txt Generator

FastAPI backend with WebSocket-based crawler.

## Setup

```bash
cd backend
cp .env.example .env
pip install -r requirements.txt
```

## Run

```bash
uvicorn main:app --reload
```

## Test

```bash
pytest
```

## WebSocket Endpoint

Connect to `ws://localhost:8000/ws/crawl`

Send:
```json
{
  "url": "https://example.com",
  "maxPages": 50,
  "descLength": 500
}
```

Receive messages:
- `{"type": "log", "content": "..."}`
- `{"type": "result", "content": "llms.txt content"}`
- `{"type": "url", "content": "hosted url"}`
- `{"type": "error", "content": "error message"}`
