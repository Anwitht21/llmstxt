import httpx
from bs4 import BeautifulSoup


def has_meaningful_content(html: str) -> bool:
    if not html or len(html.strip()) < 100:
        return False

    try:
        soup = BeautifulSoup(html, 'html.parser')

        text = soup.get_text(separator=' ', strip=True)

        blocking_indicators = [
            'access denied',
            'blocked',
            'captcha',
            'cloudflare',
            'please verify you are human',
            'robot or human',
            'security check',
        ]
        text_lower = text.lower()
        if any(indicator in text_lower for indicator in blocking_indicators):
            return False

        if '{{' in text or '{%' in text:
            return False

        if len(text) > 200:
            return True

        return False

    except Exception:
        return False


async def fetch_with_brightdata(url: str, api_key: str, zone: str = "web_unlocker1", timeout: int = 60) -> str:
    endpoint = "https://api.brightdata.com/request"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "zone": zone,
        "url": url,
        "format": "json"
    }

    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(endpoint, headers=headers, json=payload)
        response.raise_for_status()

        result = response.json()
        return result.get("body", "") or result.get("html", "") or str(result)


class BrightDataClient:
    def __init__(self, api_key: str, enabled: bool = True, zone: str = "web_unlocker1"):
        self.api_key = api_key
        self.enabled = enabled
        self.zone = zone
        self.request_count = 0
        self.success_count = 0
        self.total_cost_estimate = 0.0

    async def fetch(self, url: str) -> str:
        if not self.enabled or not self.api_key:
            raise ValueError("Bright Data not enabled or API key missing")

        html = await fetch_with_brightdata(url, self.api_key, self.zone)

        self.request_count += 1
        self.total_cost_estimate += 0.015

        if has_meaningful_content(html):
            self.success_count += 1

        return html

    def get_usage_stats(self) -> dict:
        return {
            "requests": self.request_count,
            "successful": self.success_count,
            "estimated_cost_usd": round(self.total_cost_estimate, 2)
        }
