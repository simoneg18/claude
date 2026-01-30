"""Amazon Italy scraper for TCG Monitor."""

import logging
from typing import List
from datetime import datetime

from scrapers.base import BaseScraper
from models.product import Product
from utils.parsers import clean_text, extract_price, make_absolute_url

logger = logging.getLogger(__name__)


class AmazonITScraper(BaseScraper):
    """Scraper for Amazon Italy website."""

    BASE_URL = "https://www.amazon.it"

    async def parse_products(self, html: str, source_url: str) -> List[Product]:
        """
        Parse Amazon Italy search results page.

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
        logger.debug(f"[Amazon IT] Found {len(product_cards)} product cards")

        for card in product_cards:
            try:
                # Skip sponsored products and ads
                if self._is_sponsored(card):
                    continue

                product = self._parse_product_card(card, source_url)
                if product:
                    products.append(product)
            except Exception as e:
                logger.error(f"[Amazon IT] Error parsing product card: {e}")
                continue

        return products

    def _is_sponsored(self, card) -> bool:
        """Check if product card is a sponsored listing."""
        card_text = card.get_text().lower()
        sponsored_indicators = ['sponsorizzato', 'sponsored', 'annuncio']
        return any(indicator in card_text for indicator in sponsored_indicators)

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
        # Amazon shows availability in various ways
        in_stock = True  # Default to true, then check for out of stock indicators

        # Check for availability indicator
        availability_elem = card.select_one(selectors.availability)
        if availability_elem:
            avail_text = clean_text(availability_elem.get_text()).lower()
            if 'disponibil' in avail_text or 'in stock' in avail_text:
                in_stock = True
            elif 'non disponibile' in avail_text or 'currently unavailable' in avail_text:
                in_stock = False

        # Also check card text for out of stock indicators
        card_text = card.get_text().lower()
        out_of_stock_phrases = [
            'non disponibile',
            'currently unavailable',
            'out of stock',
            'temporaneamente esaurito'
        ]
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

        logger.debug(f"[Amazon IT] Parsed: {product}")
        return product
