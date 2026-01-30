"""Tests for the parsers module."""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.parsers import (
    clean_text,
    extract_price,
    make_absolute_url,
    normalize_url,
    extract_domain,
    is_valid_product_url
)


class TestCleanText:
    """Tests for clean_text function."""

    def test_clean_normal_text(self):
        """Test cleaning normal text."""
        assert clean_text("Hello World") == "Hello World"

    def test_clean_extra_whitespace(self):
        """Test removing extra whitespace."""
        assert clean_text("  Hello   World  ") == "Hello World"

    def test_clean_newlines(self):
        """Test removing newlines."""
        assert clean_text("Hello\n\nWorld") == "Hello World"

    def test_clean_tabs(self):
        """Test removing tabs."""
        assert clean_text("Hello\t\tWorld") == "Hello World"

    def test_clean_empty(self):
        """Test empty string."""
        assert clean_text("") == ""

    def test_clean_none(self):
        """Test None input."""
        assert clean_text(None) == ""


class TestExtractPrice:
    """Tests for extract_price function."""

    def test_euro_symbol_prefix(self):
        """Test euro symbol prefix."""
        assert extract_price("€49,99") == 49.99

    def test_euro_symbol_suffix(self):
        """Test euro symbol suffix."""
        assert extract_price("49,99€") == 49.99

    def test_eur_text(self):
        """Test EUR text."""
        assert extract_price("EUR 49.99") == 49.99
        assert extract_price("49.99 EUR") == 49.99

    def test_european_format(self):
        """Test European number format (comma as decimal)."""
        assert extract_price("49,99") == 49.99

    def test_us_format(self):
        """Test US number format (dot as decimal)."""
        assert extract_price("49.99") == 49.99

    def test_thousands_separator_european(self):
        """Test European thousands separator."""
        assert extract_price("€1.234,56") == 1234.56

    def test_thousands_separator_us(self):
        """Test US thousands separator."""
        assert extract_price("$1,234.56") == 1234.56

    def test_with_extra_text(self):
        """Test price with extra text."""
        assert extract_price("Price: €49,99 incl. VAT") == 49.99

    def test_empty(self):
        """Test empty string."""
        assert extract_price("") is None

    def test_none(self):
        """Test None input."""
        assert extract_price(None) is None

    def test_no_price(self):
        """Test string without price."""
        assert extract_price("Out of stock") is None


class TestMakeAbsoluteUrl:
    """Tests for make_absolute_url function."""

    def test_already_absolute(self):
        """Test already absolute URL."""
        url = "https://example.com/product"
        assert make_absolute_url(url, "https://base.com") == url

    def test_relative_path(self):
        """Test relative path."""
        assert make_absolute_url("/product", "https://example.com") == "https://example.com/product"

    def test_relative_no_slash(self):
        """Test relative without leading slash."""
        assert make_absolute_url("product", "https://example.com/") == "https://example.com/product"

    def test_empty_url(self):
        """Test empty URL returns base."""
        assert make_absolute_url("", "https://example.com") == "https://example.com"

    def test_none_url(self):
        """Test None URL returns base."""
        assert make_absolute_url(None, "https://example.com") == "https://example.com"


class TestNormalizeUrl:
    """Tests for normalize_url function."""

    def test_normalize_trailing_slash(self):
        """Test removing trailing slash."""
        assert normalize_url("https://example.com/product/") == "https://example.com/product"

    def test_normalize_uppercase(self):
        """Test lowercasing."""
        assert normalize_url("HTTPS://EXAMPLE.COM/Product") == "https://example.com/product"

    def test_normalize_removes_query(self):
        """Test URL without query params for comparison."""
        result = normalize_url("https://example.com/product?ref=123")
        assert "?" not in result


class TestExtractDomain:
    """Tests for extract_domain function."""

    def test_simple_domain(self):
        """Test simple domain extraction."""
        assert extract_domain("https://example.com/path") == "example.com"

    def test_www_prefix(self):
        """Test removing www prefix."""
        assert extract_domain("https://www.example.com/path") == "example.com"

    def test_subdomain(self):
        """Test subdomain handling."""
        assert extract_domain("https://shop.example.com/path") == "shop.example.com"

    def test_with_port(self):
        """Test domain with port."""
        assert extract_domain("https://example.com:8080/path") == "example.com:8080"


class TestIsValidProductUrl:
    """Tests for is_valid_product_url function."""

    def test_valid_https(self):
        """Test valid HTTPS URL."""
        assert is_valid_product_url("https://example.com/product") is True

    def test_valid_http(self):
        """Test valid HTTP URL."""
        assert is_valid_product_url("http://example.com/product") is True

    def test_invalid_no_scheme(self):
        """Test invalid URL without scheme."""
        assert is_valid_product_url("example.com/product") is False

    def test_invalid_empty(self):
        """Test empty URL."""
        assert is_valid_product_url("") is False

    def test_invalid_none(self):
        """Test None URL."""
        assert is_valid_product_url(None) is False
