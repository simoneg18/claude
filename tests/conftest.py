"""Pytest configuration and shared fixtures."""

import pytest
import sys
from pathlib import Path

# Add project root to path for all tests
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def sample_html_gamestop():
    """Sample HTML resembling GameStop product listing."""
    return """
    <html>
    <body>
        <div class="product-tile">
            <h3 class="product-name">
                <a href="/products/one-piece-op15-booster-box">
                    One Piece OP15 Booster Box
                </a>
            </h3>
            <span class="sales">
                <span class="value">€89,99</span>
            </span>
            <button class="add-to-cart">Add to Cart</button>
        </div>
        <div class="product-tile">
            <h3 class="product-name">
                <a href="/products/one-piece-op15-sleeves">
                    One Piece OP15 Sleeves
                </a>
            </h3>
            <span class="sales">
                <span class="value">€12,99</span>
            </span>
            <button class="add-to-cart" disabled>Out of Stock</button>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def sample_html_amazon():
    """Sample HTML resembling Amazon product listing."""
    return """
    <html>
    <body>
        <div data-component-type="s-search-result">
            <h2>
                <a href="/dp/B123456">
                    <span>One Piece Card Game OP-16 Booster Display</span>
                </a>
            </h2>
            <span class="a-price-whole">99</span>
            <span class="a-color-success">Disponibile</span>
        </div>
        <div data-component-type="s-search-result">
            <h2>
                <a href="/dp/B789012">
                    <span>One Piece OP16 Box Bustina</span>
                </a>
            </h2>
            <span class="a-price-whole">85</span>
        </div>
    </body>
    </html>
    """


@pytest.fixture
def mock_retailer_config():
    """Create a mock retailer configuration."""
    from models.config import RetailerConfig, RetailerSelectors

    return RetailerConfig(
        name="Test Retailer",
        enabled=True,
        scraper_type="generic",
        urls=["https://example.com/search"],
        selectors=RetailerSelectors(
            product_card="div.product-tile",
            title="h3.product-name a",
            price="span.value",
            availability="button.add-to-cart:not([disabled])",
            link="h3.product-name a"
        ),
        use_playwright=False
    )
