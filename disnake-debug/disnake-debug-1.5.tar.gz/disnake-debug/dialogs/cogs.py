from ..utils import EmbedFactory, MainMenu, get_bot_message
from ..constants import ERROR, THUMBS_UP

from disnake import Message, MessageInteraction, ButtonStyle
from disnake.ui import View, Button, button
from disnake.ext.commands import Context, Bot, ExtensionNotFound, ExtensionAlreadyLoaded, ExtensionNotLoaded



class Cogs(View):
    def __init__(self, ctx: Context):
        super().__init__()

        self.ctx = ctx
        self.bot: Bot = ctx.bot
        self.bot_message = get_bot_message(ctx)
        self.add_item(MainMenu(ctx))
        cog_not_found = EmbedFactory.error_embed(self.ctx, "Extension not found")
        cog_not_loaded = EmbedFactory.error_embed(self.ctx, "Extension not loaded")
        cog_already_loaded = EmbedFactory.error_embed(self.ctx, "Extension already")

    async def interaction_check(self, interaction: MessageInteraction) -> bool:
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )

    def check(self, m: Message) -> bool:
        return m.author == self.ctx.author and m.channel == self.ctx.channel

    @button(label="Load", style=ButtonStyle.green)
    async def load_button(self, button: Button, interaction: MessageInteraction):
        embed = EmbedFactory.static_embed(
            self.ctx, "Manage cogs", path="cog/load", description="What is the file path of the cog you want to load?"
        )
        await self.bot_message.edit(embed=embed)
        await interaction.response.send_message("What cog do you want to load?", ephemeral=True)

        message: Message = await self.bot.wait_for("message", check=self.check)
        fp = message.content.replace("/", ".")

        try:
            self.bot.load_extension(fp)
        except ExtensionNotFound:
            await message.add_reaction(ERROR)
            return await self.bot_message.edit(embed=self.cog_not_found)
        except ExtensionAlreadyLoaded:
            await message.add_reaction(ERROR)
            return await self.bot_message.edit(embed=self.cog_already_loaded)

        embed = EmbedFactory.static_embed(
            self.ctx, "Manage cogs", path="cog/load/success", description=f"Successfully loaded {fp}"
        )
        await message.add_reaction(THUMBS_UP)
        await self.bot_message.edit(embed=embed)

    @button(label="Unload", style=ButtonStyle.green)
    async def unload_button(self, button: Button, interaction: MessageInteraction):
        embed = EmbedFactory.static_embed(
            self.ctx, "Manage cogs", path="cog/unload", description="What is the file path of the cog you want to unload?"
        )
        await self.bot_message.edit(embed=embed)
        await interaction.response.send_message("What cog do you want to unload?", ephemeral=True)

        message: Message = await self.bot.wait_for("message", check=self.check)
        fp = message.content.replace("/", ".")

        try:
            self.bot.load_extension(fp)
        except ExtensionNotFound:
            await message.add_reaction(ERROR)
            return await self.bot_message.edit(embed=self.cog_not_found)
        except ExtensionNotLoaded:
            await message.add_reaction(ERROR)
            return await self.bot_message.edit(embed=self.cog_not_loaded)

        embed = EmbedFactory.static_embed(
            self.ctx, "Manage cogs", path="cog/unload/success", description=f"Successfully unloaded {fp}"
        )
        await message.add_reaction(THUMBS_UP)
        await self.bot_message.edit(embed=embed)


    @button(label="Reload", style=ButtonStyle.green)
    async def reload_button(self, button: Button, interaction: MessageInteraction):
        embed = EmbedFactory.static_embed(
            self.ctx, "Manage cogs", path="cog/reload", description="What is the file path of the cog you want to reload?"
        )
        await self.bot_message.edit(embed=embed)
        await interaction.response.send_message("What cog do you want to reload?", ephemeral=True)

        message: Message = await self.bot.wait_for("message", check=self.check)
        fp = message.content.replace("/", ".")

        try:
            self.bot.load_extension(fp)
        except ExtensionNotFound:
            await message.add_reaction(ERROR)
            return await self.bot_message.edit(embed=self.cog_not_found)
        except ExtensionNotLoaded:
            await message.add_reaction(ERROR)
            return await self.bot_message.edit(embed=self.cog_not_loaded)

        embed = EmbedFactory.static_embed(
            self.ctx, "Manage cogs", path="cog/reload/success", description=f"Successfully reloaded {fp}"
        )
        await message.add_reaction(THUMBS_UP)
        await self.bot_message.edit(embed=embed)