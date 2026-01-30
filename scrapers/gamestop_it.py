"""GameStop Italy scraper for TCG Monitor."""

import logging
from typing import List
from datetime import datetime

from scrapers.base import BaseScraper
from models.product import Product
from utils.parsers import clean_text, extract_price, make_absolute_url

logger = logging.getLogger(__name__)


class GameStopITScraper(BaseScraper):
    """Scraper for GameStop Italy website."""

    BASE_URL = "https://www.gamestop.it"

    async def parse_products(self, html: str, source_url: str) -> List[Product]:
        """
        Parse GameStop Italy search results page.

        Args:
            html: Raw HTML content
            source_url: URL the HTML was fetched from

        Returns:
            List of Product objects
        """
        soup = self.create_soup(html)
        products = []
        selectors = self.config.selectors

        # Find all product cards
        product_cards = soup.select(selectors.product_card)
        logger.debug(f"[GameStop IT] Found {len(product_cards)} product cards")

        for card in product_cards:
            try:
                product = self._parse_product_card(card, source_url)
                if product:
                    products.append(product)
            except Exception as e:
                logger.error(f"[GameStop IT] Error parsing product card: {e}")
                continue

        return products

    def _parse_product_card(self, card, source_url: str) -> Product | None:
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
            url = make_absolute_url(href, self.BASE_URL)

        # Extract price
        price = None
        price_elem = card.select_one(selectors.price)
        if price_elem:
            price_text = clean_text(price_elem.get_text())
            price = extract_price(price_text)

        # Check availability
        # GameStop uses a disabled add-to-cart button for out of stock
        availability_elem = card.select_one(selectors.availability)
        in_stock = availability_elem is not None

        # Also check for explicit out of stock text
        card_text = card.get_text().lower()
        if 'non disponibile' in card_text or 'out of stock' in card_text:
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

        logger.debug(f"[GameStop IT] Parsed: {product}")
        return product
