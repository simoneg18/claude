"""Tests for the detector module."""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.detector import (
    matches_keywords,
    extract_set_code,
    normalize_set_code,
    is_booster_product,
    calculate_price_change
)
from models.config import KeywordsConfig


@pytest.fixture
def keywords():
    """Create test keywords configuration."""
    return KeywordsConfig(
        sets=["OP15", "OP-15", "OP16", "OP-16"],
        product_types=["Booster Box", "Display", "Box Bustina"]
    )


class TestMatchesKeywords:
    """Tests for matches_keywords function."""

    def test_matches_valid_product(self, keywords):
        """Test matching a valid product with set and type."""
        title = "One Piece Card Game OP15 Booster Box"
        assert matches_keywords(title, keywords) is True

    def test_matches_with_dash(self, keywords):
        """Test matching set code with dash."""
        title = "One Piece OP-15 Display Box"
        assert matches_keywords(title, keywords) is True

    def test_matches_case_insensitive(self, keywords):
        """Test case insensitive matching."""
        title = "ONE PIECE op15 BOOSTER BOX"
        assert matches_keywords(title, keywords) is True

    def test_no_match_wrong_set(self, keywords):
        """Test non-matching set code."""
        title = "One Piece OP10 Booster Box"
        assert matches_keywords(title, keywords) is False

    def test_no_match_wrong_type(self, keywords):
        """Test non-matching product type."""
        title = "One Piece OP15 Single Card"
        assert matches_keywords(title, keywords) is False

    def test_no_match_set_only(self, keywords):
        """Test that set alone doesn't match."""
        title = "One Piece OP15 Sleeves"
        assert matches_keywords(title, keywords) is False

    def test_no_match_type_only(self, keywords):
        """Test that type alone doesn't match."""
        title = "Pokemon Booster Box"
        assert matches_keywords(title, keywords) is False

    def test_empty_title(self, keywords):
        """Test empty title."""
        assert matches_keywords("", keywords) is False
        assert matches_keywords(None, keywords) is False

    def test_partial_set_code_no_match(self, keywords):
        """Test that partial set codes don't match (OP150 shouldn't match OP15)."""
        title = "One Piece OP150 Booster Box"
        assert matches_keywords(title, keywords) is False


class TestExtractSetCode:
    """Tests for extract_set_code function."""

    def test_extract_simple(self):
        """Test extracting simple set code."""
        assert extract_set_code("One Piece OP15 Booster Box") == "OP15"

    def test_extract_with_dash(self):
        """Test extracting set code with dash."""
        assert extract_set_code("One Piece OP-15 Display") == "OP-15"

    def test_extract_lowercase(self):
        """Test extracting lowercase set code."""
        assert extract_set_code("one piece op16 box") == "OP16"

    def test_extract_no_match(self):
        """Test no set code found."""
        assert extract_set_code("Pokemon Booster Box") is None

    def test_extract_from_complex_title(self):
        """Test extracting from complex title."""
        title = "Bandai One Piece Card Game OP-17 Booster Display (24 Packs) - ITA"
        assert extract_set_code(title) == "OP-17"


class TestNormalizeSetCode:
    """Tests for normalize_set_code function."""

    def test_normalize_with_dash(self):
        """Test normalizing set code with dash."""
        assert normalize_set_code("OP-15") == "OP15"

    def test_normalize_lowercase(self):
        """Test normalizing lowercase."""
        assert normalize_set_code("op15") == "OP15"

    def test_normalize_already_normalized(self):
        """Test already normalized code."""
        assert normalize_set_code("OP15") == "OP15"


class TestIsBoosterProduct:
    """Tests for is_booster_product function."""

    def test_booster_box(self):
        """Test booster box detection."""
        assert is_booster_product("One Piece OP15 Booster Box") is True

    def test_display_box(self):
        """Test display box detection."""
        assert is_booster_product("One Piece OP15 Display Box") is True

    def test_box_bustina(self):
        """Test Italian format."""
        assert is_booster_product("One Piece OP15 Box Bustina") is True

    def test_single_card_no_match(self):
        """Test single card doesn't match."""
        assert is_booster_product("One Piece OP15 Single Card Luffy") is False

    def test_sleeves_no_match(self):
        """Test sleeves don't match."""
        assert is_booster_product("One Piece Card Sleeves") is False


class TestCalculatePriceChange:
    """Tests for calculate_price_change function."""

    def test_price_drop(self):
        """Test price drop calculation."""
        absolute, percentage = calculate_price_change(100.0, 80.0)
        assert absolute == -20.0
        assert percentage == -20.0

    def test_price_increase(self):
        """Test price increase calculation."""
        absolute, percentage = calculate_price_change(80.0, 100.0)
        assert absolute == 20.0
        assert percentage == 25.0

    def test_no_change(self):
        """Test no price change."""
        absolute, percentage = calculate_price_change(50.0, 50.0)
        assert absolute == 0.0
        assert percentage == 0.0

    def test_none_old_price(self):
        """Test with None old price."""
        result = calculate_price_change(None, 50.0)
        assert result == (None, None)

    def test_none_new_price(self):
        """Test with None new price."""
        result = calculate_price_change(50.0, None)
        assert result == (None, None)

    def test_zero_old_price(self):
        """Test with zero old price (avoid division by zero)."""
        result = calculate_price_change(0, 50.0)
        assert result == (None, None)
