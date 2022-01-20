import disnake

from disnake import ButtonStyle, Embed, Message, MessageInteraction
from disnake.ui import Button
from disnake.ext.commands import Context

newline = '\n'

def get_bot_message(ctx: Context) -> Message:
    return ctx.bot._bot_messages[ctx.message.id]

def clean_code(content:str):
    if content.startswith("```py"):
        content = content[5:-3]
    content = content.strip("`")
    content = content.replace("‘", "'").replace('“', '"').replace("”", "\"").replace("’", "'")
    return content


class EmbedFactory:
    """Embed factory"""

    @staticmethod
    def static_embed(
        ctx: Context, 
        title: str, 
        *,
        path: str = None, 
        description: str = None,
        markdown: str = 'yaml',
    ):
        return Embed(
            title=title,
            colour=0x0000ff,
            description=f"```yaml\nCurrent path: /{path or ''}```{'```' + markdown + newline + description + '```' if description else ''}",
            timestamp=ctx.message.created_at
        ).set_author(
            name=ctx.author.name,
            icon_url=ctx.author.avatar.url      
        ).set_footer(
            text=f"Bot ping: {ctx.bot.latency * 1000:.0f} || Uptime: {ctx.bot._get_uptime()}"
        )

class MainMenu(Button):
    def __init__(self, ctx: Context):
        super().__init__(
            style=ButtonStyle.danger,
            label="Back"
        )
        self.ctx = ctx
        self.bot_message = get_bot_message(ctx)

    async def callback(self, interaction: MessageInteraction):
        from .exts import DebugView

        embed = EmbedFactory.static_embed(self.ctx, "Debug Controls")

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed, view=DebugView(self.ctx))