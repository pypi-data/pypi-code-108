from impressive_strawberry.database import tables

from . import discord
from . import strawberry

__all__ = (
    "notify_unlock",
)

module_map = {
    tables.WebhookKind.STRAWBERRY: strawberry,
    tables.WebhookKind.DISCORD: discord,
}


async def notify_unlock(group: tables.Group, unlock: tables.Unlock) -> None:
    for webhook in group.webhooks:
        await module_map[webhook.kind].notify_unlock(url=webhook.url, unlock=unlock)
