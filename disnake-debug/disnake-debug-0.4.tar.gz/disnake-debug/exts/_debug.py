from ..utils import EmbedFactory

from disnake import ButtonStyle, MessageInteraction
from disnake.ui import View, Button, button
from disnake.ext.commands import Context


class DebugView(View):
    def __init__(self, ctx: Context):
        super().__init__()

        self.ctx = ctx

    @button(label="Echo", style=ButtonStyle.green)
    async def echo_button(
        self, button: Button, interaction: MessageInteraction
    ):
        """
        args:
            -> user/channel
            -> message
        """

    @button(label="Blacklist", style=ButtonStyle.green)
    async def blacklist_button(
        self, button: Button, interaction: MessageInteraction
    ):
        """
        args:
            -> user/guild/channel
            -> duration
        """
        ...

        #TODO: append to db

    @button(label="Leave guild", style=ButtonStyle.green)
    async def leave_guild_button(
        self, button: Button, interaction: MessageInteraction
    ):
        """
        args:
            -> guild
        """

        from . import GuildView

        embed = EmbedFactory.static_embed(self.ctx, "What guild would you like to edit?", "leave_guild")

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed, view=GuildView(self.ctx))

    @button(label="Change", style=ButtonStyle.green)
    async def change_button(
        self, button: Button, interaction: MessageInteraction
    ):  
        """
        args:
            -> name/avatar
        """

        from . import ChangeView
        
        embed = EmbedFactory.static_embed(self.ctx, "What would you like to change?", "change")

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed, view=ChangeView(self.ctx, self.bot_message))