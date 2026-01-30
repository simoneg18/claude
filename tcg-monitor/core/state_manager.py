"""State management using TinyDB for TCG Monitor."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List

from tinydb import TinyDB, Query

from models.product import Product

logger = logging.getLogger(__name__)


class StateManager:
    """Manages product state persistence using TinyDB."""

    def __init__(self, db_path: str = "data/products.db"):
        """
        Initialize state manager.

        Args:
            db_path: Path to the TinyDB database file
        """
        # Ensure data directory exists
        db_file = Path(db_path)
        db_file.parent.mkdir(parents=True, exist_ok=True)

        self.db = TinyDB(db_path)
        self.products_table = self.db.table('products')
        self.query = Query()

        logger.info(f"StateManager initialized with database: {db_path}")

    def get_product(self, product_id: str) -> Optional[Product]:
        """
        Retrieve product by ID.

        Args:
            product_id: Unique product identifier

        Returns:
            Product if found, None otherwise
        """
        result = self.products_table.get(self.query.product_id == product_id)

        if result:
            return Product.from_dict(result)
        return None

    def save_product(self, product: Product) -> int:
        """
        Insert new product.

        Args:
            product: Product to save

        Returns:
            Document ID of inserted product
        """
        doc_id = self.products_table.insert(product.to_dict())
        logger.info(f"New product saved: {product.title[:50]}... (ID: {product.product_id[:8]})")
        return doc_id

    def update_product(self, product: Product) -> bool:
        """
        Update existing product.

        Args:
            product: Product with updated data

        Returns:
            True if update was successful
        """
        product.last_checked = datetime.now()
        updated = self.products_table.update(
            product.to_dict(),
            self.query.product_id == product.product_id
        )
        if updated:
            logger.debug(f"Product updated: {product.title[:50]}...")
        return bool(updated)

    def update_timestamp(self, product_id: str) -> bool:
        """
        Update only the last_checked timestamp.

        Args:
            product_id: Product ID to update

        Returns:
            True if update was successful
        """
        updated = self.products_table.update(
            {'last_checked': datetime.now().isoformat()},
            self.query.product_id == product_id
        )
        return bool(updated)

    def mark_notified(self, product_id: str) -> bool:
        """
        Mark product as notified.

        Args:
            product_id: Product ID to mark

        Returns:
            True if update was successful
        """
        updated = self.products_table.update(
            {'last_notified': datetime.now().isoformat()},
            self.query.product_id == product_id
        )
        return bool(updated)

    def get_all_products(self) -> List[Product]:
        """
        Retrieve all products.

        Returns:
            List of all products in database
        """
        results = self.products_table.all()
        return [Product.from_dict(r) for r in results]

    def get_products_by_retailer(self, retailer: str) -> List[Product]:
        """
        Retrieve products for a specific retailer.

        Args:
            retailer: Retailer name

        Returns:
            List of products from that retailer
        """
        results = self.products_table.search(self.query.retailer == retailer)
        return [Product.from_dict(r) for r in results]

    def get_in_stock_products(self) -> List[Product]:
        """
        Retrieve all currently in-stock products.

        Returns:
            List of in-stock products
        """
        results = self.products_table.search(self.query.in_stock == True)
        return [Product.from_dict(r) for r in results]

    def delete_product(self, product_id: str) -> bool:
        """
        Delete a product by ID.

        Args:
            product_id: Product ID to delete

        Returns:
            True if deletion was successful
        """
        removed = self.products_table.remove(self.query.product_id == product_id)
        return bool(removed)

    def clear_all(self) -> int:
        """
        Clear all products from database.

        Returns:
            Number of products removed
        """
        count = len(self.products_table)
        self.products_table.truncate()
        logger.warning(f"Cleared all {count} products from database")
        return count

    def get_stats(self) -> dict:
        """
        Get database statistics.

        Returns:
            Dictionary with stats
        """
        all_products = self.products_table.all()
        in_stock = sum(1 for p in all_products if p.get('in_stock', False))

        retailers = {}
        for p in all_products:
            retailer = p.get('retailer', 'Unknown')
            retailers[retailer] = retailers.get(retailer, 0) + 1

        return {
            'total_products': len(all_products),
            'in_stock': in_stock,
            'out_of_stock': len(all_products) - in_stock,
            'by_retailer': retailers
        }

    def close(self):
        """Close database connection."""
        self.db.close()
