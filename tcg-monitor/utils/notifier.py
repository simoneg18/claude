"""Discord notification system for TCG Monitor."""

import logging
from discord_webhook import DiscordWebhook, DiscordEmbed
from models.product import Product
from typing import Optional

logger = logging.getLogger(__name__)


class DiscordNotifier:
    """Send notifications to Discord via webhooks."""

    # Color codes for different notification types
    COLORS = {
        'RESTOCK': 0x00ff00,      # Green
        'NEW_STOCK': 0x3498db,    # Blue
        'PRICE_DROP': 0xf1c40f,   # Yellow
        'ERROR': 0xe74c3c,        # Red
        'INFO': 0x95a5a6,         # Gray
    }

    def __init__(self, webhook_url: str, mention_role_id: Optional[str] = None):
        """
        Initialize Discord notifier.

        Args:
            webhook_url: Discord webhook URL
            mention_role_id: Optional role ID to mention on alerts
        """
        self.webhook_url = webhook_url
        self.mention_role_id = mention_role_id

    def _create_mention(self) -> str:
        """Create mention string if role ID is configured."""
        if self.mention_role_id:
            return f"<@&{self.mention_role_id}>"
        return ""

    async def send_restock_alert(self, product: Product, event_type: str = "RESTOCK") -> bool:
        """
        Send formatted restock notification to Discord.

        Args:
            product: Product that was restocked
            event_type: Type of event (RESTOCK, NEW_STOCK)

        Returns:
            True if notification was sent successfully
        """
        try:
            webhook = DiscordWebhook(
                url=self.webhook_url,
                content=self._create_mention()
            )

            # Select emoji and color based on event type
            emoji = "🔥" if event_type == "RESTOCK" else "🆕"
            color = self.COLORS.get(event_type, self.COLORS['INFO'])

            embed = DiscordEmbed(
                title=f"{emoji} {event_type}: {product.title[:100]}",
                description=f"**Retailer**: {product.retailer}",
                color=color,
                url=product.url
            )

            # Price field
            if product.price:
                embed.add_embed_field(
                    name="Price",
                    value=f"€{product.price:.2f}",
                    inline=True
                )

            # Status field
            embed.add_embed_field(
                name="Status",
                value="✅ IN STOCK",
                inline=True
            )

            # Quick buy link
            embed.add_embed_field(
                name="Quick Buy",
                value=f"[Click Here]({product.url})",
                inline=True
            )

            # Restock count (if applicable)
            if product.restock_count > 0:
                embed.add_embed_field(
                    name="Restock #",
                    value=str(product.restock_count),
                    inline=True
                )

            # Timestamp footer
            embed.set_footer(text=f"Detected at {product.last_checked.strftime('%Y-%m-%d %H:%M:%S')}")

            webhook.add_embed(embed)
            response = webhook.execute()

            success = response.status_code in [200, 204]
            if success:
                logger.info(f"Discord notification sent for: {product.title[:50]}")
            else:
                logger.error(f"Discord notification failed: {response.status_code}")

            return success

        except Exception as e:
            logger.error(f"Error sending Discord notification: {e}")
            return False

    async def send_error_alert(self, message: str) -> bool:
        """
        Send error notification to Discord.

        Args:
            message: Error message to send

        Returns:
            True if notification was sent successfully
        """
        try:
            webhook = DiscordWebhook(url=self.webhook_url)

            embed = DiscordEmbed(
                title="⚠️ TCG Monitor Alert",
                description=message,
                color=self.COLORS['ERROR']
            )

            webhook.add_embed(embed)
            response = webhook.execute()

            return response.status_code in [200, 204]

        except Exception as e:
            logger.error(f"Error sending error alert: {e}")
            return False

    async def send_startup_message(self) -> bool:
        """Send a startup notification to confirm bot is running."""
        try:
            webhook = DiscordWebhook(url=self.webhook_url)

            embed = DiscordEmbed(
                title="🚀 TCG Monitor Started",
                description="The monitoring bot is now online and watching for restocks!",
                color=self.COLORS['INFO']
            )

            webhook.add_embed(embed)
            response = webhook.execute()

            return response.status_code in [200, 204]

        except Exception as e:
            logger.error(f"Error sending startup message: {e}")
            return False


def test_discord_notification(webhook_url: str) -> bool:
    """
    Test Discord webhook with a simple message.

    Args:
        webhook_url: Discord webhook URL to test

    Returns:
        True if test was successful
    """
    try:
        webhook = DiscordWebhook(url=webhook_url)

        embed = DiscordEmbed(
            title="🎉 Test Notification",
            description="TCG Monitor webhook test successful!",
            color=0x00ff00
        )
        embed.set_footer(text="Test Mode")

        webhook.add_embed(embed)
        response = webhook.execute()

        success = response.status_code in [200, 204]
        print(f"Webhook test: {'SUCCESS' if success else 'FAILED'} (Status: {response.status_code})")
        return success

    except Exception as e:
        print(f"Webhook test failed: {e}")
        return False


if __name__ == "__main__":
    # Quick test
    import os
    from dotenv import load_dotenv

    load_dotenv()
    webhook_url = os.getenv("DISCORD_WEBHOOK_URL")

    if webhook_url:
        test_discord_notification(webhook_url)
    else:
        print("DISCORD_WEBHOOK_URL not set in .env file")
