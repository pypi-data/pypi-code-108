from ..utils import FindSnowflake, EmbedFactory, MainMenu, get_bot_message
from ..constants import THUMBS_UP, ERROR

from disnake import Message, MessageInteraction, ButtonStyle
from disnake.ui import View, Button, button
from disnake.ext.commands import Context, Bot

class Github(View):
    def __init__(self, ctx: Context):
        super().__init__()

        self.ctx = ctx
        self.bot: Bot = ctx.bot
        self.bot_message = get_bot_message(ctx)
        self.add_item(MainMenu(ctx))

    async def interaction_check(self, interaction: MessageInteraction) -> bool:
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )

    def check(self, m: Message):
        return m.author == self.ctx.author and m.channel == self.ctx.channel