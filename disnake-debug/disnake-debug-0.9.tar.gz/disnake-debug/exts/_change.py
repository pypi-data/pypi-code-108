from ..utils import EmbedFactory, MainMenu, get_bot_message

from disnake import MessageInteraction, ButtonStyle
from disnake.ui import View, Button, button
from disnake.ext.commands import Context

class ChangeView(View):
    def __init__(self, ctx: Context):
        super().__init__()

        self.ctx = ctx
        self.bot_message = get_bot_message(ctx)

        self.add_item(MainMenu(ctx))

    async def interaction_check(self, interaction: MessageInteraction) -> bool:
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )

    @button(label="Name", style=ButtonStyle.green)
    async def name_button(
        self, button: Button, interaction: MessageInteraction
    ): 
        ...

    @button(label="Avatar", style=ButtonStyle.green)
    async def avatar_button(
        self, button: Button, interaction: MessageInteraction
    ):  
        ...