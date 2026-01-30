"""Configuration loader for TCG Monitor."""

import os
import yaml
import logging
from pathlib import Path
from dotenv import load_dotenv
from pydantic import ValidationError
from models.config import AppConfig

logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.yaml") -> AppConfig:
    """
    Load and validate configuration from YAML file.

    Args:
        config_path: Path to the configuration file

    Returns:
        Validated AppConfig instance

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValidationError: If config is invalid
    """
    # Load environment variables
    load_dotenv()

    # Check if config file exists
    config_file = Path(config_path)
    if not config_file.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    # Load YAML config
    with open(config_file, 'r', encoding='utf-8') as f:
        config_dict = yaml.safe_load(f)

    # Replace environment variable placeholders
    config_dict = _replace_env_vars(config_dict)

    # Validate and return config
    try:
        config = AppConfig(**config_dict)
        logger.info(f"Configuration loaded successfully from {config_path}")
        logger.info(f"Enabled retailers: {[r.name for r in config.get_enabled_retailers()]}")
        return config
    except ValidationError as e:
        logger.error(f"Configuration validation failed: {e}")
        raise


def _replace_env_vars(obj):
    """
    Recursively replace ${ENV_VAR} placeholders with environment variable values.

    Args:
        obj: Dictionary, list, or value to process

    Returns:
        Processed object with env vars replaced
    """
    if isinstance(obj, dict):
        return {k: _replace_env_vars(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_replace_env_vars(item) for item in obj]
    elif isinstance(obj, str) and obj.startswith('${') and obj.endswith('}'):
        env_var = obj[2:-1]
        value = os.getenv(env_var)
        if value is None:
            logger.warning(f"Environment variable {env_var} not set")
        return value
    return obj


def create_default_config(output_path: str = "config.yaml"):
    """
    Create a default configuration file template.

    Args:
        output_path: Path where to save the config file
    """
    default_config = """# TCG Monitor Configuration
# Edit this file to configure your monitoring settings

# Global settings
polling_interval: 30  # seconds between monitoring cycles
max_concurrent_scrapers: 5
log_level: INFO

# Target keywords for product matching
# Products must match at least one keyword from BOTH 'sets' AND 'product_types'
keywords:
  sets:
    - "OP15"
    - "OP-15"
    - "OP16"
    - "OP-16"
    - "OP17"
    - "OP-17"
  product_types:
    - "Booster Box"
    - "Display"
    - "Box Bustina"
    - "Busta"

# Discord notifications
discord:
  webhook_url: "${DISCORD_WEBHOOK_URL}"  # Set in .env file
  mention_role_id: null  # Optional: Discord role ID to mention

# Retailers configuration
# Add or modify retailers here
retailers:
  - name: "GameStop Italy"
    enabled: true
    scraper_type: "gamestop_it"
    urls:
      - "https://www.gamestop.it/SearchResult/QuickSearch?q=one+piece+booster+box"
    selectors:
      product_card: "div.product-tile"
      title: "h3.product-name a"
      price: "span.sales span.value"
      availability: "button.add-to-cart:not([disabled])"
      link: "h3.product-name a"
    use_playwright: false

  - name: "Amazon Italy"
    enabled: false  # Enable when ready
    scraper_type: "amazon_it"
    urls:
      - "https://www.amazon.it/s?k=one+piece+booster+box"
    selectors:
      product_card: "div[data-component-type='s-search-result']"
      title: "h2 a span"
      price: "span.a-price-whole"
      availability: "span.a-color-success"
      link: "h2 a"
    use_playwright: false

  - name: "Cardmarket"
    enabled: false  # Enable when ready
    scraper_type: "cardmarket"
    urls:
      - "https://www.cardmarket.com/it/OnePiece/Products/Booster-Boxes"
    selectors:
      product_card: "div.col-12.col-md-6.col-lg-4"
      title: "div.product-name"
      price: "span.font-weight-bold"
      availability: "button.btn-primary"
      link: "a.card"
    use_playwright: true  # Cardmarket requires JavaScript rendering
"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(default_config)

    logger.info(f"Default configuration created at {output_path}")


if __name__ == "__main__":
    # Create default config if run directly
    create_default_config()
    print("Default config.yaml created!")
