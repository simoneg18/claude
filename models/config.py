"""Configuration models for TCG Monitor using Pydantic."""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional


class RetailerSelectors(BaseModel):
    """CSS selectors for extracting product data from retailer pages."""
    product_card: str
    title: str
    price: str
    availability: str
    link: str


class RetailerConfig(BaseModel):
    """Configuration for a single retailer."""
    name: str
    enabled: bool = True
    scraper_type: str
    urls: List[str]  # Using str instead of HttpUrl for flexibility
    selectors: RetailerSelectors
    use_playwright: bool = False
    polling_interval: Optional[int] = None  # Override global polling interval


class DiscordConfig(BaseModel):
    """Discord notification configuration."""
    webhook_url: str
    mention_role_id: Optional[str] = None


class KeywordsConfig(BaseModel):
    """Keywords for product matching."""
    sets: List[str]
    product_types: List[str]


class AppConfig(BaseModel):
    """Main application configuration."""
    polling_interval: int = Field(default=30, ge=10, le=300)
    max_concurrent_scrapers: int = Field(default=5, ge=1, le=20)
    log_level: str = "INFO"
    keywords: KeywordsConfig
    discord: DiscordConfig
    retailers: List[RetailerConfig]

    def get_enabled_retailers(self) -> List[RetailerConfig]:
        """Return only enabled retailers."""
        return [r for r in self.retailers if r.enabled]
