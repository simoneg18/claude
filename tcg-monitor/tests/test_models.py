"""Tests for the data models."""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models.product import Product
from models.config import (
    AppConfig,
    RetailerConfig,
    RetailerSelectors,
    DiscordConfig,
    KeywordsConfig
)


class TestProduct:
    """Tests for Product model."""

    @pytest.fixture
    def sample_product(self):
        """Create a sample product."""
        return Product(
            product_id="abc123",
            retailer="Test Retailer",
            title="One Piece OP15 Booster Box",
            url="https://example.com/product",
            in_stock=True,
            price=89.99
        )

    def test_product_creation(self, sample_product):
        """Test basic product creation."""
        assert sample_product.product_id == "abc123"
        assert sample_product.retailer == "Test Retailer"
        assert sample_product.title == "One Piece OP15 Booster Box"
        assert sample_product.in_stock is True
        assert sample_product.price == 89.99

    def test_product_default_values(self, sample_product):
        """Test default values are set."""
        assert sample_product.price_currency == "EUR"
        assert sample_product.restock_count == 0
        assert sample_product.first_seen is not None
        assert sample_product.last_checked is not None

    def test_product_to_dict(self, sample_product):
        """Test conversion to dictionary."""
        data = sample_product.to_dict()
        assert isinstance(data, dict)
        assert data['product_id'] == "abc123"
        assert data['in_stock'] is True
        # Datetime should be ISO format string
        assert isinstance(data['first_seen'], str)

    def test_product_from_dict(self, sample_product):
        """Test reconstruction from dictionary."""
        data = sample_product.to_dict()
        reconstructed = Product.from_dict(data)

        assert reconstructed.product_id == sample_product.product_id
        assert reconstructed.title == sample_product.title
        assert reconstructed.in_stock == sample_product.in_stock

    def test_product_repr(self, sample_product):
        """Test string representation."""
        repr_str = repr(sample_product)
        assert "One Piece OP15" in repr_str
        assert "IN STOCK" in repr_str

    def test_product_out_of_stock_repr(self):
        """Test out of stock representation."""
        product = Product(
            product_id="abc123",
            retailer="Test",
            title="Test Product",
            url="https://example.com",
            in_stock=False,
            price=None
        )
        assert "OUT OF STOCK" in repr(product)


class TestRetailerConfig:
    """Tests for RetailerConfig model."""

    def test_retailer_config_creation(self):
        """Test retailer config creation."""
        selectors = RetailerSelectors(
            product_card="div.product",
            title="h2.title",
            price="span.price",
            availability="button.buy",
            link="a.link"
        )

        config = RetailerConfig(
            name="Test Retailer",
            enabled=True,
            scraper_type="generic",
            urls=["https://example.com/search"],
            selectors=selectors
        )

        assert config.name == "Test Retailer"
        assert config.enabled is True
        assert len(config.urls) == 1
        assert config.use_playwright is False  # Default

    def test_retailer_config_disabled(self):
        """Test disabled retailer."""
        selectors = RetailerSelectors(
            product_card="div",
            title="h2",
            price="span",
            availability="button",
            link="a"
        )

        config = RetailerConfig(
            name="Disabled Retailer",
            enabled=False,
            scraper_type="generic",
            urls=["https://example.com"],
            selectors=selectors
        )

        assert config.enabled is False


class TestAppConfig:
    """Tests for AppConfig model."""

    @pytest.fixture
    def sample_config(self):
        """Create sample app config."""
        selectors = RetailerSelectors(
            product_card="div",
            title="h2",
            price="span",
            availability="button",
            link="a"
        )

        return AppConfig(
            polling_interval=30,
            max_concurrent_scrapers=5,
            log_level="INFO",
            keywords=KeywordsConfig(
                sets=["OP15", "OP16"],
                product_types=["Booster Box"]
            ),
            discord=DiscordConfig(
                webhook_url="https://discord.com/api/webhooks/test"
            ),
            retailers=[
                RetailerConfig(
                    name="Enabled Retailer",
                    enabled=True,
                    scraper_type="generic",
                    urls=["https://example.com"],
                    selectors=selectors
                ),
                RetailerConfig(
                    name="Disabled Retailer",
                    enabled=False,
                    scraper_type="generic",
                    urls=["https://example2.com"],
                    selectors=selectors
                )
            ]
        )

    def test_app_config_creation(self, sample_config):
        """Test app config creation."""
        assert sample_config.polling_interval == 30
        assert len(sample_config.retailers) == 2

    def test_get_enabled_retailers(self, sample_config):
        """Test filtering enabled retailers."""
        enabled = sample_config.get_enabled_retailers()
        assert len(enabled) == 1
        assert enabled[0].name == "Enabled Retailer"

    def test_polling_interval_validation(self):
        """Test polling interval bounds."""
        selectors = RetailerSelectors(
            product_card="div",
            title="h2",
            price="span",
            availability="button",
            link="a"
        )

        # Test minimum bound
        with pytest.raises(ValueError):
            AppConfig(
                polling_interval=5,  # Below minimum of 10
                keywords=KeywordsConfig(sets=["OP15"], product_types=["Box"]),
                discord=DiscordConfig(webhook_url="https://test.com"),
                retailers=[]
            )

        # Test maximum bound
        with pytest.raises(ValueError):
            AppConfig(
                polling_interval=500,  # Above maximum of 300
                keywords=KeywordsConfig(sets=["OP15"], product_types=["Box"]),
                discord=DiscordConfig(webhook_url="https://test.com"),
                retailers=[]
            )
