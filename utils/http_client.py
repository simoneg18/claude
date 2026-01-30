"""HTTP client with anti-detection measures for TCG Monitor."""

import asyncio
import random
import httpx
from fake_useragent import UserAgent
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class HTTPClient:
    """Async HTTP client with anti-detection features."""

    def __init__(self, timeout: float = 15.0):
        """
        Initialize HTTP client.

        Args:
            timeout: Request timeout in seconds
        """
        self.ua = UserAgent()
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                limits=httpx.Limits(
                    max_keepalive_connections=5,
                    max_connections=10
                ),
                timeout=httpx.Timeout(self.timeout),
                follow_redirects=True
            )
        return self._client

    def _get_headers(self) -> dict:
        """Generate random browser-like headers."""
        return {
            'User-Agent': self.ua.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }

    async def _random_delay(self, min_delay: float = 1.0, max_delay: float = 3.0):
        """Add random delay between requests."""
        delay = random.uniform(min_delay, max_delay)
        await asyncio.sleep(delay)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.HTTPStatusError, httpx.TimeoutException)),
        reraise=True
    )
    async def fetch(self, url: str, add_delay: bool = True) -> str:
        """
        Fetch URL content with retry logic and anti-detection.

        Args:
            url: URL to fetch
            add_delay: Whether to add random delay before request

        Returns:
            HTML content as string

        Raises:
            httpx.HTTPStatusError: If request fails after retries
        """
        if add_delay:
            await self._random_delay()

        client = await self._get_client()
        headers = self._get_headers()

        try:
            response = await client.get(url, headers=headers)

            if response.status_code == 403:
                logger.warning(f"403 Forbidden for {url}. Rotating User-Agent and retrying...")
                raise httpx.HTTPStatusError(
                    "Forbidden - rotating User-Agent",
                    request=response.request,
                    response=response
                )

            if response.status_code == 429:
                logger.warning(f"Rate limited on {url}. Backing off...")
                await asyncio.sleep(30)  # Wait 30 seconds before retry
                raise httpx.HTTPStatusError(
                    "Rate limited",
                    request=response.request,
                    response=response
                )

            response.raise_for_status()
            return response.text

        except httpx.TimeoutException:
            logger.error(f"Timeout fetching {url}")
            raise

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
