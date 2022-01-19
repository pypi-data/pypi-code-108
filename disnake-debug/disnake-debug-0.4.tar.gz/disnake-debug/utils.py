from disnake import Embed, Message
from disnake.ext.commands import Context

def get_bot_message(ctx: Context) -> Message:
    return ctx.bot.bot_messages[ctx.message.id]

class EmbedFactory:
    """Embed factory"""

    @staticmethod
    def static_embed(ctx, title: str, path: str = None):
        return Embed(
            title=title,
            colour=0xb82785,
            description=f"```yaml\nChoose an option - Current path: /{path or ''}```",
            timestamp=ctx.message.created_at
        ).set_author(
            name=ctx.author.name,
            icon_url=ctx.author.avatar.url
        )
