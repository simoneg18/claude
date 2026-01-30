#!/usr/bin/env python3
"""
TCG Monitor - One Piece Card Game Restock Tracker

Main entry point for the monitoring application.
Continuously monitors configured retailers for product restocks
and sends notifications via Discord webhook.

Usage:
    python main.py              # Run the monitor
    python main.py --test       # Test Discord webhook
    python main.py --check      # Check configuration and exit
"""

import asyncio
import argparse
import sys
import logging
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

from core.monitor import TCGMonitor
from utils.config_loader import load_config
from utils.logger import setup_logging, get_logger
from utils.notifier import test_discord_notification


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='TCG Monitor - One Piece Card Game Restock Tracker',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py              Run the monitor
    python main.py --test       Test Discord webhook
    python main.py --check      Validate configuration
    python main.py --debug      Run with debug logging
        """
    )

    parser.add_argument(
        '--test',
        action='store_true',
        help='Test Discord webhook and exit'
    )

    parser.add_argument(
        '--check',
        action='store_true',
        help='Validate configuration and exit'
    )

    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )

    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )

    return parser.parse_args()


def check_configuration(config_path: str) -> bool:
    """
    Validate configuration and print summary.

    Args:
        config_path: Path to configuration file

    Returns:
        True if configuration is valid
    """
    print("=" * 50)
    print("TCG Monitor - Configuration Check")
    print("=" * 50)

    try:
        config = load_config(config_path)
        print(f"[OK] Configuration loaded from: {config_path}")

        # Check Discord webhook
        if config.discord.webhook_url:
            print(f"[OK] Discord webhook URL configured")
        else:
            print("[ERROR] Discord webhook URL not set!")
            print("       Set DISCORD_WEBHOOK_URL in .env file")
            return False

        # Check retailers
        enabled_retailers = config.get_enabled_retailers()
        print(f"[OK] Retailers configured: {len(config.retailers)}")
        print(f"[OK] Retailers enabled: {len(enabled_retailers)}")

        for retailer in enabled_retailers:
            print(f"     - {retailer.name} ({len(retailer.urls)} URL(s))")

        if not enabled_retailers:
            print("[WARNING] No retailers enabled!")
            print("          Enable at least one retailer in config.yaml")

        # Check keywords
        print(f"[OK] Set keywords: {len(config.keywords.sets)}")
        print(f"     {config.keywords.sets}")
        print(f"[OK] Product type keywords: {len(config.keywords.product_types)}")
        print(f"     {config.keywords.product_types}")

        # Settings
        print(f"[OK] Polling interval: {config.polling_interval} seconds")
        print(f"[OK] Log level: {config.log_level}")

        print("=" * 50)
        print("Configuration is valid!")
        print("=" * 50)
        return True

    except FileNotFoundError:
        print(f"[ERROR] Configuration file not found: {config_path}")
        print("        Create config.yaml from config.yaml.example")
        return False

    except Exception as e:
        print(f"[ERROR] Configuration error: {e}")
        return False


def test_webhook(config_path: str) -> bool:
    """
    Test Discord webhook.

    Args:
        config_path: Path to configuration file

    Returns:
        True if test was successful
    """
    print("=" * 50)
    print("TCG Monitor - Discord Webhook Test")
    print("=" * 50)

    try:
        config = load_config(config_path)

        if not config.discord.webhook_url:
            print("[ERROR] Discord webhook URL not configured!")
            print("        Set DISCORD_WEBHOOK_URL in .env file")
            return False

        print("Sending test notification...")
        success = test_discord_notification(config.discord.webhook_url)

        if success:
            print("[OK] Test notification sent successfully!")
            print("     Check your Discord channel for the message.")
        else:
            print("[ERROR] Failed to send test notification")
            print("        Check your webhook URL")

        return success

    except Exception as e:
        print(f"[ERROR] {e}")
        return False


async def main_async(config_path: str, debug: bool):
    """
    Main async entry point.

    Args:
        config_path: Path to configuration file
        debug: Enable debug logging
    """
    # Load configuration
    try:
        config = load_config(config_path)
    except FileNotFoundError:
        print(f"ERROR: Configuration file not found: {config_path}")
        print("Create config.yaml from .env.example and config.yaml template")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to load configuration: {e}")
        sys.exit(1)

    # Setup logging
    log_level = "DEBUG" if debug else config.log_level
    setup_logging(log_level)
    logger = get_logger(__name__)

    # Validate Discord webhook
    if not config.discord.webhook_url:
        logger.error("Discord webhook URL not configured!")
        logger.error("Set DISCORD_WEBHOOK_URL in .env file")
        sys.exit(1)

    # Check for enabled retailers
    if not config.get_enabled_retailers():
        logger.error("No retailers enabled!")
        logger.error("Enable at least one retailer in config.yaml")
        sys.exit(1)

    # Create and run monitor
    try:
        monitor = TCGMonitor(config)
        await monitor.run()
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


def main():
    """Main entry point."""
    args = parse_args()

    # Handle --check flag
    if args.check:
        success = check_configuration(args.config)
        sys.exit(0 if success else 1)

    # Handle --test flag
    if args.test:
        success = test_webhook(args.config)
        sys.exit(0 if success else 1)

    # Run the monitor
    print("""
╔════════════════════════════════════════════════════╗
║          TCG Monitor - Restock Tracker             ║
║      One Piece Card Game Edition                   ║
╚════════════════════════════════════════════════════╝
    """)

    asyncio.run(main_async(args.config, args.debug))


if __name__ == "__main__":
    main()
