import asyncio
import logging

from .base import BaseNotifier


__all__ = ["DiscordNotifier"]


class DiscordNotifier(BaseNotifier):
    """A Discord notifier."""

    TYPE = "discord"

    def __init__(self, token: str, channel_id: int):
        self._token = token
        self._channel_id = channel_id

    async def _async_notify(self, text: str) -> None:
        """Sends a message asynchronous."""
        try:
            from hikari import RESTApp
        except ModuleNotFoundError:  # pragma: no cover - no complexity here
            logging.error("Please install the `hikari` package.")
            exit(1)

        rest_app = RESTApp()
        async with rest_app.acquire(self._token, "Bot") as client:
            channel = await client.fetch_channel(self._channel_id)
            await client.create_message(channel, text)  # type: ignore

    def notify(self, text: str) -> None:
        """Sends a message."""
        asyncio.run(self._async_notify(text))
