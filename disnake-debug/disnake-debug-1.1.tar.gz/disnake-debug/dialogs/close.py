from ..utils import EmbedFactory, MainMenu, get_bot_message

from disnake import MessageInteraction, ButtonStyle
from disnake.ui import View, Button, button
from disnake.ext.commands import Context


class ConfirmExit(View):
    def __init__(self, ctx: Context):
        super().__init__()

        self.ctx = ctx
        self.bot_message = get_bot_message(ctx)

        self.add_item(MainMenu(ctx))

    @button(label="Yes", style=ButtonStyle.green)
    async def confirm_button(self, button: Button, interaction: MessageInteraction):
        """
        close bot
        """

        embed = EmbedFactory.static_embed(
            self.ctx, "Goodbye!", path="exit/off")

        await self.bot_message.edit(embed=embed)
        await self.ctx.bot.close()

    @button(label="No", style=ButtonStyle.danger)
    async def cancel_button(self, button: Button, interaction: MessageInteraction):
        from . import DebugView

        embed = EmbedFactory.static_embed(self.ctx, "Debug Controls")
        await self.bot_message.edit(embed=embed, view=DebugView(self.ctx))


class CloseView(View):
    def __init__(self, ctx: Context):
        super().__init__()

        self.ctx = ctx
        self.bot_message = get_bot_message(ctx)

    async def interaction_check(self, interaction: MessageInteraction) -> bool:
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )

    @button(label="Pause", style=ButtonStyle.green)
    async def pause_button(self, button: Button, interaction: MessageInteraction):
        """
        pause the bot so it does not respond to commands
        """

        embed = EmbedFactory.static_embed(
            self.ctx,
            "Paused bot",
            path="pause",
            description="Bot paused; commands locked",
        )
        bot = self.ctx.bot
        bot._paused = True

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed)

    @button(label="Resume", style=ButtonStyle.green)
    async def resume_button(self, button: Button, interaction: MessageInteraction):
        """
        unpause the bot
        """

        embed = EmbedFactory.static_embed(
            self.ctx,
            "Resumed bot",
            path="resume",
            description="Resumed bot; commands unlocked",
        )
        bot = self.ctx.bot
        bot._paused = False

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed)

    @button(label="Exit", style=ButtonStyle.danger)
    async def exit_button(self, button: Button, interaction: MessageInteraction):
        embed = EmbedFactory.static_embed(
            self.ctx, "Are you sure you want to exit?", path="exit"
        )

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed, view=ConfirmExit(self.ctx))
