"""Scraper factory for TCG Monitor."""

import logging
from typing import Dict, Type

from scrapers.base import BaseScraper
from scrapers.gamestop_it import GameStopITScraper
from scrapers.amazon_it import AmazonITScraper
from scrapers.cardmarket import CardmarketScraper
from scrapers.generic import GenericScraper
from models.config import RetailerConfig

logger = logging.getLogger(__name__)


class ScraperFactory:
    """Factory for creating retailer-specific scrapers."""

    # Registry of available scrapers
    SCRAPERS: Dict[str, Type[BaseScraper]] = {
        'gamestop_it': GameStopITScraper,
        'amazon_it': AmazonITScraper,
        'cardmarket': CardmarketScraper,
        'generic': GenericScraper,
    }

    @classmethod
    def create(cls, scraper_type: str, config: RetailerConfig) -> BaseScraper:
        """
        Create a scraper instance for the specified type.

        Args:
            scraper_type: Type identifier (e.g., 'gamestop_it')
            config: Retailer configuration

        Returns:
            Configured scraper instance

        Raises:
            ValueError: If scraper type is unknown
        """
        scraper_class = cls.SCRAPERS.get(scraper_type)

        if not scraper_class:
            logger.warning(
                f"Unknown scraper type '{scraper_type}', falling back to generic scraper"
            )
            scraper_class = GenericScraper

        logger.debug(f"Creating {scraper_class.__name__} for {config.name}")
        return scraper_class(config)

    @classmethod
    def register(cls, scraper_type: str, scraper_class: Type[BaseScraper]):
        """
        Register a new scraper type.

        Args:
            scraper_type: Type identifier
            scraper_class: Scraper class to register
        """
        cls.SCRAPERS[scraper_type] = scraper_class
        logger.info(f"Registered scraper type: {scraper_type}")

    @classmethod
    def available_scrapers(cls) -> list:
        """Return list of available scraper types."""
        return list(cls.SCRAPERS.keys())
