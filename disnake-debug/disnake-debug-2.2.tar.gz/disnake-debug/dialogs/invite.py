from ..utils import EmbedFactory, MainMenu, get_bot_message
from ..constants import PERMISSION_LIST

from disnake import MessageInteraction, ButtonStyle, Message
from disnake.ui import View, Button, button
from disnake.ext.commands import Context, Bot


class Invite(View):
    def __init__(self, ctx: Context, *, restart: bool = False):
        super().__init__()

        self.ctx = ctx
        self.bot: Bot = ctx.bot
        self.restart = restart
        self.bot_message = get_bot_message(ctx)
        self.base_url = "https://discord.com/oauth2/authorize?client_id={bot_id}&scope=bot{application}&permissions={permissions}"
        self.add_item(MainMenu(ctx))

    async def interaction_check(self, interaction: MessageInteraction) -> bool:
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )

    def check(self, m: Message) -> bool:
        return m.author == self.ctx.author and m.channel == self.ctx.channel

    @button(label="No slash commands", style=ButtonStyle.green)
    async def bot_button(self, button: Button, interaction: MessageInteraction):
        embed = EmbedFactory.static_embed(
            self.ctx,
            "Generate invite",
            path="invite/bot",
            description=f"What permissions?{PERMISSION_LIST}",
        )
        await self.bot_message.edit(embed=embed, view=Invite(self.ctx))
        await interaction.response.send_message("What permission value?")

        message: Message = await self.bot.wait_for("message", check=self.check)
        if message.content == "q":
            return await interaction.message.reply("Cancelled the current `wait_for`")

        invite = self.base_url.format(
            bot_id=self.bot.user.id, application="", permissions=message.content
        )
        embed = EmbedFactory.static_embed(
            self.ctx,
            "Generate invite",
            path="invite/bot/create",
            description="Generated invite: " + invite,
        )
        await interaction.message.reply(f"Invite: {invite}")
        await self.bot_message.edit(embed=embed)

    @button(label="Slash commands", style=ButtonStyle.green)
    async def slash_command_button(
        self, button: Button, interaction: MessageInteraction
    ):
        embed = EmbedFactory.static_embed(
            self.ctx,
            "Generate invite",
            path="invite/application",
            description=f"What permissions?{PERMISSION_LIST}",
        )

        await self.bot_message.edit(embed=embed, view=Invite(self.ctx))
        await interaction.response.send_message("What permission value?")

        message: Message = await self.bot.wait_for("message", check=self.check)
        if message.content == "q":
            return await interaction.message.reply("Cancelled the current `wait_for`")

        invite = self.base_url.format(
            bot_id=self.bot.user.id,
            application="%20applications.commands",
            permissions=message.content,
        )
        embed = EmbedFactory.static_embed(
            self.ctx,
            "Generate invite",
            path="invite/application/create",
            description="Generated invite: " + invite,
        )
        await interaction.message.reply(f"Invite: {invite}")
        await self.bot_message.edit(embed=embed)
