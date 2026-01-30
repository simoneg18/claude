"""Generic scraper for TCG Monitor - works with most e-commerce sites."""

import logging
from typing import List
from datetime import datetime

from scrapers.base import BaseScraper
from models.product import Product
from utils.parsers import clean_text, extract_price, make_absolute_url

logger = logging.getLogger(__name__)


class GenericScraper(BaseScraper):
    """
    Generic scraper that uses configurable selectors.

    Use this for new retailers before creating a specialized scraper.
    Works well when CSS selectors are straightforward.
    """

    async def parse_products(self, html: str, source_url: str) -> List[Product]:
        """
        Parse products using configured selectors.

        Args:
            html: Raw HTML content
            source_url: URL the HTML was fetched from

        Returns:
            List of Product objects
        """
        soup = self.create_soup(html)
        products = []
        selectors = self.config.selectors

        # Determine base URL from source
        from urllib.parse import urlparse
        parsed = urlparse(source_url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"

        # Find all product cards
        product_cards = soup.select(selectors.product_card)
        logger.debug(f"[{self.config.name}] Found {len(product_cards)} product cards")

        for card in product_cards:
            try:
                product = self._parse_product_card(card, source_url, base_url)
                if product:
                    products.append(product)
            except Exception as e:
                logger.error(f"[{self.config.name}] Error parsing product card: {e}")
                continue

        return products

    def _parse_product_card(self, card, source_url: str, base_url: str) -> Product | None:
        """Parse a single product card element."""
        selectors = self.config.selectors

        # Extract title
        title_elem = card.select_one(selectors.title)
        if not title_elem:
            return None

        title = clean_text(title_elem.get_text())
        if not title:
            return None

        # Extract URL
        link_elem = card.select_one(selectors.link)
        url = source_url
        if link_elem:
            href = link_elem.get('href', '')
            url = make_absolute_url(href, base_url)

        # Extract price
        price = None
        price_elem = card.select_one(selectors.price)
        if price_elem:
            price_text = clean_text(price_elem.get_text())
            price = extract_price(price_text)

        # Check availability
        in_stock = False
        availability_elem = card.select_one(selectors.availability)
        if availability_elem:
            in_stock = True

        # Also check card text for common availability phrases
        card_text = card.get_text().lower()

        # Positive indicators
        in_stock_phrases = ['disponibile', 'in stock', 'add to cart', 'aggiungi al carrello', 'buy now']
        if any(phrase in card_text for phrase in in_stock_phrases):
            in_stock = True

        # Negative indicators (override positive)
        out_of_stock_phrases = ['non disponibile', 'out of stock', 'esaurito', 'sold out', 'unavailable']
        if any(phrase in card_text for phrase in out_of_stock_phrases):
            in_stock = False

        # Create product
        product = Product(
            product_id=self.generate_product_id(self.config.name, title, url),
            retailer=self.config.name,
            title=title,
            url=url,
            in_stock=in_stock,
            price=price,
            first_seen=datetime.now(),
            last_checked=datetime.now()
        )

        logger.debug(f"[{self.config.name}] Parsed: {product}")
        return product
