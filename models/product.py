"""Product data model for TCG Monitor."""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional


@dataclass
class Product:
    """Represents a monitored TCG product."""

    # Identifiers
    product_id: str          # Hash of (retailer + title + url)
    retailer: str            # "GameStop Italy"
    title: str               # "One Piece OP15 Booster Box"
    url: str                 # Direct product link

    # Availability data
    in_stock: bool           # Current availability
    price: Optional[float]   # Current price (EUR)
    price_currency: str = "EUR"

    # Metadata
    first_seen: datetime = None     # When first detected
    last_checked: datetime = None   # Last monitoring timestamp
    last_notified: Optional[datetime] = None  # Prevent notification spam

    # Tracking
    restock_count: int = 0   # How many times restocked

    def __post_init__(self):
        """Initialize timestamps if not provided."""
        if self.first_seen is None:
            self.first_seen = datetime.now()
        if self.last_checked is None:
            self.last_checked = datetime.now()

    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        data = asdict(self)
        # Convert datetime to ISO format
        for key in ['first_seen', 'last_checked', 'last_notified']:
            if data[key]:
                data[key] = data[key].isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'Product':
        """Reconstruct from stored dictionary."""
        # Parse datetime fields
        for key in ['first_seen', 'last_checked', 'last_notified']:
            if data.get(key):
                data[key] = datetime.fromisoformat(data[key])
        return cls(**data)

    def __repr__(self) -> str:
        stock_status = "IN STOCK" if self.in_stock else "OUT OF STOCK"
        return f"Product({self.title[:30]}... | {self.retailer} | {stock_status})"
