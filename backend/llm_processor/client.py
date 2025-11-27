import httpx
import asyncio
from typing import Callable

class RateLimitError(Exception):
    pass

class OpenRouterClient:
    def __init__(self, api_key: str, model: str, timeout: float = 30.0,
                 max_retries: int = 3, temperature: float = 0.3, log_fn: Callable[[str], None] | None = None):
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries
        self.temperature = temperature
        self.log = log_fn or (lambda x: None)
        self.base_url = "https://openrouter.ai/api/v1"
        self._rate_limit_semaphore = asyncio.Semaphore(20)
        self._last_request_times: list[float] = []

    async def _wait_for_rate_limit(self):
        import time
        now = time.time()
        self._last_request_times = [t for t in self._last_request_times if now - t < 60]

        if len(self._last_request_times) >= 20:
            oldest = self._last_request_times[0]
            wait_time = 60 - (now - oldest) + 1
            if wait_time > 0:
                self.log(f"Rate limit: waiting {wait_time:.1f}s")
                await asyncio.sleep(wait_time)

        self._last_request_times.append(now)

    async def complete(self, messages: list[dict]) -> str:
        async with self._rate_limit_semaphore:
            await self._wait_for_rate_limit()

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://llmstxt.org",
                "X-Title": "llmstxt Generator"
            }

            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": self.temperature
            }

            last_exception = None
            for attempt in range(self.max_retries):
                try:
                    async with httpx.AsyncClient(timeout=self.timeout) as client:
                        response = await client.post(
                            f"{self.base_url}/chat/completions",
                            json=payload,
                            headers=headers
                        )

                        if response.status_code == 429:
                            retry_after = int(response.headers.get('retry-after', 60))
                            if attempt < self.max_retries - 1:
                                self.log(f"Rate limited, retrying after {retry_after}s")
                                await asyncio.sleep(retry_after)
                                continue
                            else:
                                raise RateLimitError("Rate limit exceeded")

                        response.raise_for_status()
                        data = response.json()
                        completion = data['choices'][0]['message']['content'].strip()

                        if completion.startswith('```markdown'):
                            completion = completion[len('```markdown'):].strip()
                        if completion.startswith('```'):
                            completion = completion[3:].strip()
                        if completion.endswith('```'):
                            completion = completion[:-3].strip()

                        return completion

                except httpx.TimeoutException as e:
                    last_exception = e
                    if attempt < self.max_retries - 1:
                        wait_time = 2 ** attempt
                        self.log(f"Timeout, retrying in {wait_time}s (attempt {attempt + 1}/{self.max_retries})")
                        await asyncio.sleep(wait_time)
                    continue

                except httpx.HTTPError as e:
                    last_exception = e
                    if hasattr(e, 'response') and e.response and 400 <= e.response.status_code < 500:
                        if e.response.status_code != 429:
                            raise
                    if attempt < self.max_retries - 1:
                        wait_time = 2 ** attempt
                        self.log(f"API error, retrying in {wait_time}s: {str(e)}")
                        await asyncio.sleep(wait_time)
                    continue

            raise last_exception or Exception("Unknown error in OpenRouter client")
