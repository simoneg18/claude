"""Base scraper class for TCG Monitor."""

import hashlib
import logging
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

from models.product import Product
from models.config import RetailerConfig
from utils.http_client import HTTPClient
from utils.parsers import make_absolute_url

logger = logging.getLogger(__name__)


class BaseScraper(ABC):
    """Abstract base class for all retailer scrapers."""

    def __init__(self, config: RetailerConfig):
        """
        Initialize the scraper.

        Args:
            config: Retailer configuration
        """
        self.config = config
        self.http_client = HTTPClient()

    @abstractmethod
    async def parse_products(self, html: str, source_url: str) -> List[Product]:
        """
        Parse HTML and extract products.

        Must be implemented by child classes.

        Args:
            html: Raw HTML content
            source_url: URL the HTML was fetched from

        Returns:
            List of Product objects
        """
        pass

    async def fetch_html(self, url: str) -> Optional[str]:
        """
        Fetch HTML from URL using appropriate method.

        Args:
            url: URL to fetch

        Returns:
            HTML content or None if fetch failed
        """
        if self.config.use_playwright:
            return await self._fetch_with_playwright(url)
        else:
            return await self._fetch_with_httpx(url)

    async def _fetch_with_httpx(self, url: str) -> Optional[str]:
        """Fetch URL using httpx."""
        try:
            return await self.http_client.fetch(url)
        except Exception as e:
            logger.error(f"[{self.config.name}] Error fetching {url}: {e}")
            return None

    async def _fetch_with_playwright(self, url: str) -> Optional[str]:
        """Fetch URL using Playwright for JavaScript-rendered content."""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)

                context = await browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    locale='it-IT',
                    timezone_id='Europe/Rome'
                )

                page = await context.new_page()

                # Block unnecessary resources to speed up
                await page.route(
                    "**/*.{png,jpg,jpeg,gif,svg,mp4,webm,woff,woff2}",
                    lambda route: route.abort()
                )

                await page.goto(url, wait_until='networkidle', timeout=30000)

                # Wait a bit for dynamic content
                await page.wait_for_timeout(2000)

                content = await page.content()
                await browser.close()

                return content

        except Exception as e:
            logger.error(f"[{self.config.name}] Playwright error for {url}: {e}")
            return None

    async def fetch_products(self) -> List[Product]:
        """
        Fetch and parse all configured URLs.

        Returns:
            List of all products found across all URLs
        """
        all_products = []

        for url in self.config.urls:
            try:
                logger.debug(f"[{self.config.name}] Fetching {url}")
                html = await self.fetch_html(url)

                if not html:
                    logger.warning(f"[{self.config.name}] No HTML content from {url}")
                    continue

                products = await self.parse_products(html, url)
                logger.info(f"[{self.config.name}] Found {len(products)} products from {url}")
                all_products.extend(products)

            except Exception as e:
                logger.error(f"[{self.config.name}] Error processing {url}: {e}")

        return all_products

    def generate_product_id(self, retailer: str, title: str, url: str) -> str:
        """
        Generate unique product ID.

        Args:
            retailer: Retailer name
            title: Product title
            url: Product URL

        Returns:
            MD5 hash as product ID
        """
        # Normalize URL for consistent hashing
        normalized_url = url.rstrip('/').lower().split('?')[0]
        unique_string = f"{retailer}:{title}:{normalized_url}"
        return hashlib.md5(unique_string.encode()).hexdigest()

    def create_soup(self, html: str) -> BeautifulSoup:
        """Create BeautifulSoup object from HTML."""
        return BeautifulSoup(html, 'lxml')

    async def close(self):
        """Clean up resources."""
        await self.http_client.close()
