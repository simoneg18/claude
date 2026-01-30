"""Main monitoring orchestrator for TCG Monitor."""

import asyncio
import logging
from datetime import datetime
from typing import Dict

from scrapers.factory import ScraperFactory
from scrapers.base import BaseScraper
from core.state_manager import StateManager
from core.detector import matches_keywords
from utils.notifier import DiscordNotifier
from models.config import AppConfig
from models.product import Product

logger = logging.getLogger(__name__)


class TCGMonitor:
    """Main monitoring orchestrator."""

    def __init__(self, config: AppConfig):
        """
        Initialize the monitor.

        Args:
            config: Application configuration
        """
        self.config = config
        self.state_manager = StateManager()
        self.notifier = DiscordNotifier(
            config.discord.webhook_url,
            config.discord.mention_role_id
        )

        # Track errors per scraper for automatic disabling
        self.error_counts: Dict[str, int] = {}
        self.max_consecutive_errors = 5

        # Stats for current session
        self.stats = {
            'cycles': 0,
            'products_scanned': 0,
            'restocks_detected': 0,
            'new_stock_detected': 0,
            'errors': 0
        }

    async def create_scrapers(self) -> list[BaseScraper]:
        """Create scraper instances for enabled retailers."""
        scrapers = []

        for retailer in self.config.get_enabled_retailers():
            try:
                scraper = ScraperFactory.create(retailer.scraper_type, retailer)
                scrapers.append(scraper)
                logger.debug(f"Created scraper for {retailer.name}")
            except Exception as e:
                logger.error(f"Failed to create scraper for {retailer.name}: {e}")

        return scrapers

    async def monitoring_cycle(self):
        """Execute one complete monitoring cycle across all retailers."""
        cycle_start = datetime.now()
        logger.info("=" * 50)
        logger.info("Starting monitoring cycle...")

        # Create scrapers for enabled retailers
        scrapers = await self.create_scrapers()

        if not scrapers:
            logger.warning("No scrapers available!")
            return

        # Fetch products from all retailers concurrently
        scraper_results = await asyncio.gather(
            *[scraper.fetch_products() for scraper in scrapers],
            return_exceptions=True
        )

        # Process results
        cycle_products = 0
        cycle_restocks = 0
        cycle_new_stock = 0

        for idx, result in enumerate(scraper_results):
            scraper = scrapers[idx]
            retailer_name = scraper.config.name

            if isinstance(result, Exception):
                logger.error(f"Scraper {retailer_name} failed: {result}")
                self._handle_scraper_error(retailer_name)
                self.stats['errors'] += 1
                continue

            # Reset error count on success
            self.error_counts[retailer_name] = 0

            products = result
            cycle_products += len(products)

            for product in products:
                # Check if product matches target keywords
                if not matches_keywords(product.title, self.config.keywords):
                    logger.debug(f"Skipping non-matching product: {product.title[:50]}")
                    continue

                # Process matching product
                event = await self._process_product(product)

                if event == "RESTOCK":
                    cycle_restocks += 1
                elif event == "NEW_STOCK":
                    cycle_new_stock += 1

        # Update stats
        self.stats['cycles'] += 1
        self.stats['products_scanned'] += cycle_products
        self.stats['restocks_detected'] += cycle_restocks
        self.stats['new_stock_detected'] += cycle_new_stock

        # Log cycle summary
        cycle_duration = (datetime.now() - cycle_start).total_seconds()
        logger.info(
            f"Cycle #{self.stats['cycles']} complete in {cycle_duration:.1f}s | "
            f"Products: {cycle_products} | "
            f"Restocks: {cycle_restocks} | "
            f"New: {cycle_new_stock}"
        )

        # Clean up scrapers
        for scraper in scrapers:
            await scraper.close()

    async def _process_product(self, product: Product) -> str | None:
        """
        Process a single product and detect state changes.

        Args:
            product: Product to process

        Returns:
            Event type if notification sent, None otherwise
        """
        # Get previous state from database
        previous_state = self.state_manager.get_product(product.product_id)

        if previous_state is None:
            # New product discovered
            logger.info(f"[NEW] {product.retailer}: {product.title[:60]}")
            self.state_manager.save_product(product)

            if product.in_stock:
                success = await self.notifier.send_restock_alert(product, "NEW_STOCK")
                if success:
                    self.state_manager.mark_notified(product.product_id)
                return "NEW_STOCK"

        elif not previous_state.in_stock and product.in_stock:
            # RESTOCK DETECTED!
            logger.warning(f"[RESTOCK] {product.retailer}: {product.title[:60]}")

            # Update product with restock info
            product.restock_count = previous_state.restock_count + 1
            product.first_seen = previous_state.first_seen
            self.state_manager.update_product(product)

            # Send notification
            success = await self.notifier.send_restock_alert(product, "RESTOCK")
            if success:
                self.state_manager.mark_notified(product.product_id)
            return "RESTOCK"

        elif previous_state.in_stock and not product.in_stock:
            # Out of stock now
            logger.info(f"[OUT OF STOCK] {product.retailer}: {product.title[:60]}")
            product.first_seen = previous_state.first_seen
            product.restock_count = previous_state.restock_count
            self.state_manager.update_product(product)

        else:
            # No change - just update timestamp
            self.state_manager.update_timestamp(product.product_id)

        return None

    def _handle_scraper_error(self, retailer_name: str):
        """
        Handle scraper errors and disable if too many consecutive failures.

        Args:
            retailer_name: Name of the failing retailer
        """
        self.error_counts[retailer_name] = self.error_counts.get(retailer_name, 0) + 1
        count = self.error_counts[retailer_name]

        if count >= self.max_consecutive_errors:
            logger.error(
                f"Scraper {retailer_name} has failed {count} times consecutively. "
                f"Consider checking the configuration."
            )
            # Note: We don't actually disable here to allow recovery
            # In production, you might want to temporarily disable

    async def run(self):
        """Main loop - run monitoring cycles continuously."""
        logger.info("=" * 50)
        logger.info("TCG Monitor Starting")
        logger.info(f"Polling interval: {self.config.polling_interval} seconds")
        logger.info(f"Enabled retailers: {[r.name for r in self.config.get_enabled_retailers()]}")
        logger.info(f"Keywords (sets): {self.config.keywords.sets}")
        logger.info(f"Keywords (types): {self.config.keywords.product_types}")
        logger.info("=" * 50)

        # Send startup notification
        await self.notifier.send_startup_message()

        while True:
            try:
                await self.monitoring_cycle()
            except Exception as e:
                logger.error(f"Error in monitoring cycle: {e}", exc_info=True)
                self.stats['errors'] += 1

            # Wait before next cycle
            logger.info(f"Next check in {self.config.polling_interval} seconds...")
            await asyncio.sleep(self.config.polling_interval)

    def get_stats(self) -> dict:
        """Get current session statistics."""
        return {
            **self.stats,
            'database': self.state_manager.get_stats()
        }
