"""Common HTML parsing utilities for TCG Monitor."""

import re
from typing import Optional
from urllib.parse import urljoin, urlparse


def clean_text(text: Optional[str]) -> str:
    """
    Clean and normalize text content.

    Args:
        text: Raw text to clean

    Returns:
        Cleaned text with normalized whitespace
    """
    if not text:
        return ""
    # Remove extra whitespace and normalize
    return " ".join(text.split()).strip()


def extract_price(price_text: Optional[str]) -> Optional[float]:
    """
    Extract numeric price from text.

    Handles formats like:
    - "€49,99"
    - "49.99 EUR"
    - "EUR 49,99"
    - "49,99€"

    Args:
        price_text: Raw price text

    Returns:
        Price as float, or None if extraction fails
    """
    if not price_text:
        return None

    try:
        # Remove currency symbols and text
        cleaned = re.sub(r'[€$£]|EUR|USD|GBP', '', price_text, flags=re.IGNORECASE)

        # Remove thousands separators (period in European format)
        # But keep decimal separator
        cleaned = cleaned.strip()

        # Handle European format (1.234,56) vs US format (1,234.56)
        if ',' in cleaned and '.' in cleaned:
            # Check which comes last to determine format
            if cleaned.rfind(',') > cleaned.rfind('.'):
                # European: 1.234,56
                cleaned = cleaned.replace('.', '').replace(',', '.')
            else:
                # US: 1,234.56
                cleaned = cleaned.replace(',', '')
        elif ',' in cleaned:
            # Could be European decimal: 49,99
            cleaned = cleaned.replace(',', '.')

        # Extract first number
        match = re.search(r'[\d]+\.?\d*', cleaned)
        if match:
            return float(match.group())

    except (ValueError, AttributeError):
        pass

    return None


def make_absolute_url(url: str, base_url: str) -> str:
    """
    Convert relative URL to absolute.

    Args:
        url: Relative or absolute URL
        base_url: Base URL for resolving relative paths

    Returns:
        Absolute URL
    """
    if not url:
        return base_url

    # Already absolute
    if url.startswith(('http://', 'https://')):
        return url

    return urljoin(base_url, url)


def normalize_url(url: str) -> str:
    """
    Normalize URL for consistent comparison.

    Args:
        url: URL to normalize

    Returns:
        Normalized URL (lowercase, no trailing slash, no query params for comparison)
    """
    parsed = urlparse(url.lower())
    # Keep scheme, netloc, and path only for comparison
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path.rstrip('/')}"
    return normalized


def extract_domain(url: str) -> str:
    """
    Extract domain from URL.

    Args:
        url: Full URL

    Returns:
        Domain name (e.g., "gamestop.it")
    """
    parsed = urlparse(url)
    domain = parsed.netloc
    # Remove www. prefix if present
    if domain.startswith('www.'):
        domain = domain[4:]
    return domain


def is_valid_product_url(url: str) -> bool:
    """
    Basic validation that URL looks like a product page.

    Args:
        url: URL to validate

    Returns:
        True if URL appears valid
    """
    if not url:
        return False

    try:
        parsed = urlparse(url)
        # Must have scheme and netloc
        return bool(parsed.scheme and parsed.netloc)
    except Exception:
        return False
