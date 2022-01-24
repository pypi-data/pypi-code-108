from ..utils import EmbedFactory, MainMenu, get_bot_message

from disnake import HTTPException, Message, MessageInteraction, ButtonStyle
from disnake.ui import View, Button, button
from disnake.ext.commands import Context


class Change(View):
    def __init__(self, ctx: Context):
        super().__init__()

        self.ctx = ctx
        self.bot = ctx.bot
        self.bot_message = get_bot_message(ctx)
        self.add_item(MainMenu(ctx))

    async def interaction_check(self, interaction: MessageInteraction) -> bool:
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )

    def check(self, m: Message) -> bool:
        return m.author == self.ctx.author and m.channel == self.ctx.channel

    @button(label="Name", style=ButtonStyle.green)
    async def name_button(self, button: Button, interaction: MessageInteraction):
        embed = EmbedFactory.static_embed(
            self.ctx, "Change", path="change/name", description="Changing my name"
        )
        await self.bot_message.edit(embed=embed)
        await interaction.response.send_message("What username?", ephemeral=True)

        message: Message
        while len(
            ((message := await self.bot.wait_for("message", check=self.check))).content
        ) not in range(2, 33):
            await interaction.message.reply(
                "My username must be between `2-32` characters in length"
            )

        try:
            await self.bot.user.edit(username=message.content)
        except HTTPException:
            await interaction.message.reply(
                "Something went wrong - Maybe you have been changing my name too often"
            )

        embed = EmbedFactory.static_embed(
            self.ctx,
            "Change",
            path="change/name/success",
            description=f"I changed my name to {message.content}",
        )
        await self.bot_message.edit(embed=embed)

    @button(label="Avatar", style=ButtonStyle.green)
    async def avatar_button(self, button: Button, interaction: MessageInteraction):
        embed = EmbedFactory.static_embed(
            self.ctx,
            "Change",
            path="change/avatar",
            description="Changing my avatar - Send an image",
        )
        await self.bot_message.edit(embed=embed)
        await interaction.response.send_message(
            "What avatar? send an image", ephemeral=True
        )

        message: Message
        while not (
            (message := await self.bot.wait_for("message", check=self.check))
        ).attachments:
            await interaction.message.reply("You must send an image file!")

        try:
            await self.bot.user.edit(avatar=await message.attachments[0].read())
        except HTTPException:
            await interaction.message.reply(
                "Something went wrong - Maybe you have been changing my avatar too often"
            )

        embed = EmbedFactory.static_embed(
            self.ctx,
            "Change",
            path="change/avatar/success",
            description=f"I changed my avatar successfully!",
        )
        await self.bot_message.edit(embed=embed)
