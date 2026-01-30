"""Product detection and matching logic for TCG Monitor."""

import re
import logging
from typing import List

from models.config import KeywordsConfig

logger = logging.getLogger(__name__)


def matches_keywords(title: str, keywords: KeywordsConfig) -> bool:
    """
    Check if product title matches target keywords.

    Product must match:
    - At least one keyword from 'sets' (e.g., "OP15", "OP-15")
    - At least one keyword from 'product_types' (e.g., "Booster Box", "Display")

    Args:
        title: Product title to check
        keywords: Keywords configuration

    Returns:
        True if product matches both a set and a product type
    """
    if not title:
        return False

    title_lower = title.lower()

    # Check for set match (with word boundary for precise matching)
    set_match = False
    for kw in keywords.sets:
        # Use word boundary to match whole keywords
        # This prevents "OP15" from matching "OP150"
        pattern = r'\b' + re.escape(kw.lower()) + r'\b'
        if re.search(pattern, title_lower):
            set_match = True
            logger.debug(f"Set keyword match: '{kw}' in '{title}'")
            break

    if not set_match:
        return False

    # Check for product type match (substring match is fine here)
    type_match = False
    for kw in keywords.product_types:
        if kw.lower() in title_lower:
            type_match = True
            logger.debug(f"Product type match: '{kw}' in '{title}'")
            break

    return set_match and type_match


def filter_matching_products(products: list, keywords: KeywordsConfig) -> list:
    """
    Filter list of products to only those matching keywords.

    Args:
        products: List of Product objects
        keywords: Keywords configuration

    Returns:
        Filtered list of matching products
    """
    matching = [p for p in products if matches_keywords(p.title, keywords)]
    logger.debug(f"Filtered {len(products)} products to {len(matching)} matching")
    return matching


def extract_set_code(title: str) -> str | None:
    """
    Extract One Piece set code from title.

    Examples:
    - "One Piece OP15 Booster Box" -> "OP15"
    - "One Piece OP-15 Display" -> "OP-15"
    - "Random Product" -> None

    Args:
        title: Product title

    Returns:
        Set code if found, None otherwise
    """
    # Match OP followed by optional dash and 1-3 digits
    pattern = r'\b(OP-?\d{1,3})\b'
    match = re.search(pattern, title, re.IGNORECASE)

    if match:
        return match.group(1).upper()
    return None


def normalize_set_code(code: str) -> str:
    """
    Normalize set code format.

    Args:
        code: Raw set code (e.g., "op-15", "OP15")

    Returns:
        Normalized code (e.g., "OP15")
    """
    # Remove dash and uppercase
    return code.upper().replace('-', '')


def is_booster_product(title: str) -> bool:
    """
    Check if product is a booster/display product.

    Args:
        title: Product title

    Returns:
        True if product appears to be a booster box or display
    """
    booster_keywords = [
        'booster box',
        'booster display',
        'display box',
        'box bustina',
        'box buste',
        'sealed box',
    ]

    title_lower = title.lower()
    return any(kw in title_lower for kw in booster_keywords)


def calculate_price_change(old_price: float | None, new_price: float | None) -> tuple:
    """
    Calculate price change between two values.

    Args:
        old_price: Previous price
        new_price: Current price

    Returns:
        Tuple of (absolute_change, percentage_change)
    """
    if old_price is None or new_price is None:
        return (None, None)

    if old_price == 0:
        return (None, None)

    absolute = new_price - old_price
    percentage = (absolute / old_price) * 100

    return (round(absolute, 2), round(percentage, 1))
