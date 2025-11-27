from playwright.async_api import async_playwright
from bs4 import BeautifulSoup

def has_meaningful_content(html: str) -> bool:
    if not html or len(html.strip()) < 100:
        return False

    try:
        soup = BeautifulSoup(html, 'html.parser')
        text = soup.get_text(separator=' ', strip=True)

        blocking_indicators = [
            'access denied', 'blocked', 'captcha', 'cloudflare',
            'please verify you are human', 'robot or human', 'security check'
        ]
        text_lower = text.lower()
        if any(indicator in text_lower for indicator in blocking_indicators):
            return False

        if '{{' in text or '{%' in text:
            return False

        return len(text) > 200

    except Exception:
        return False

class ScrapingBrowserClient:
    def __init__(self, api_key: str, enabled: bool = True, zone: str = "scraping_browser1", password: str | None = None):
        self.api_key = api_key
        self.enabled = enabled
        self.zone = zone
        self.password = password
        self.request_count = 0
        self.success_count = 0
        self.total_cost_estimate = 0.0

        auth_string = f"brd-customer-{api_key}-zone-{zone}"
        if password:
            auth_string += f":{password}"
        self.ws_endpoint = f"wss://{auth_string}@brd.superproxy.io:9222"

    async def fetch(self, url: str, wait_for_network: bool = False, timeout: int = 120000) -> str:
        if not self.enabled or not self.api_key:
            raise ValueError("Scraping Browser not enabled or API key missing")

        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(self.ws_endpoint)

            try:
                page = await browser.new_page()
                await page.goto(url, wait_until='networkidle' if wait_for_network else 'domcontentloaded', timeout=timeout)
                await page.wait_for_timeout(3000)

                html = await page.content()

                self.request_count += 1
                self.total_cost_estimate += 0.02

                if has_meaningful_content(html):
                    self.success_count += 1

                return html

            finally:
                await browser.close()

    def get_usage_stats(self) -> dict:
        return {
            "requests": self.request_count,
            "successful": self.success_count,
            "estimated_cost_usd": round(self.total_cost_estimate, 2)
        }
