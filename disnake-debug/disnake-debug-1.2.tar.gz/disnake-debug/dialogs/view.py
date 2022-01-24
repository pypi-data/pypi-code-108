from ..utils import FindSnowflake, EmbedFactory, MainMenu, get_bot_message
from ..constants import THUMBS_UP, ERROR

from disnake import Message, MessageInteraction, ButtonStyle
from disnake.ui import View, Button, button
from disnake.ext.commands import Context, Bot

user_info = """
Name: {0.name}
Discriminator: {0.discriminator}
Id: {0.id}
Joined discord: {joined_at}
Flags: {flags}
Mobile: {mobile}
"""

channel_info = """
Name: {0.name}
Id: {0.id}
Created at: {created_at}
Invite: {invite}
"""

guild_info = """
Name: {0.name}
Id: {0.id}
Created at: {created_at}
Invite: {invite}
"""

class ViewInfo(View):
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

    @button(label="User", style=ButtonStyle.green)
    async def user_button(self, button: Button, interaction: MessageInteraction):
        embed = EmbedFactory.static_embed(
            self.ctx,
            "View",
            path=f"view/user",
            description=f"Send an id/name of the user you want to view",
        )
        await self.bot_message.edit(embed=embed)
        await interaction.response.send_message("What id/name?", ephemeral=True)

        message: Message = await self.bot.wait_for("message", check=self.check)
        response = await FindSnowflake.find_user(self.bot, message.content)
        if not response:
            embed = EmbedFactory.static_embed(
                self.ctx,
                "View",
                path=f"view/user/notfound",
                description=f"I could not find a user with id/name {message.content}",
            )
            await message.add_reaction(ERROR)
            return await self.bot_message.edit(embed=embed)
        embed = EmbedFactory.static_embed(
            self.ctx,
            "View",
            path=f"view/user/info",
            description=user_info.format(
                response,
                joined_at=response.created_at.strftime("%m/%d/%Y")
            )
        )
        await message.add_reaction(THUMBS_UP)
        await self.bot_message.edit(embed=embed)


    @button(label="Channel", style=ButtonStyle.green)
    async def channel_button(self, button: Button, interaction: MessageInteraction):
        embed = EmbedFactory.static_embed(
            self.ctx,
            "View",
            path=f"view/channel",
            description=f"Send an id/name of the channel you want to view",
        )
        await self.bot_message.edit(embed=embed)
        await interaction.response.send_message("What id/name?", ephemeral=True)

        message: Message = await self.bot.wait_for("message", check=self.check)
        response = await FindSnowflake.find_channel(self.bot, message.content)
        if not response:
            embed = EmbedFactory.static_embed(
                self.ctx,
                "View",
                path=f"view/channel/notfound",
                description=f"I could not find a channel with id/name {message.content}",
            )
            await message.add_reaction(ERROR)
            return await self.bot_message.edit(embed=embed)
        embed = EmbedFactory.static_embed(
            self.ctx,
            "View",
            path=f"view/channel/info",
            description=channel_info.format(
                response,
                joined_at=response.created_at.strftime("%m/%d/%Y")
            )
        )
        await message.add_reaction(THUMBS_UP)
        await self.bot_message.edit(embed=embed)

    @button(label="Guild", style=ButtonStyle.green)
    async def guild_button(self, button: Button, interaction: MessageInteraction):
        embed = EmbedFactory.static_embed(
            self.ctx,
            "View",
            path=f"view/guild",
            description=f"Send an id/name of the guild you want to view",
        )
        await self.bot_message.edit(embed=embed)
        await interaction.response.send_message("What id/name?", ephemeral=True)

        message: Message = await self.bot.wait_for("message", check=self.check)
        response = await FindSnowflake.find_guild(self.bot, message.content)
        if not response:
            embed = EmbedFactory.static_embed(
                self.ctx,
                "View",
                path=f"view/guild/notfound",
                description=f"I could not find a guild with id/name {message.content}",
            )
            await message.add_reaction(ERROR)
            return await self.bot_message.edit(embed=embed)
        embed = EmbedFactory.static_embed(
            self.ctx,
            "View",
            path=f"view/guild/info",
            description=guild_info.format(
                response,
                joined_at=response.created_at.strftime("%m/%d/%Y")
            )
        )
        await message.add_reaction(THUMBS_UP)
        await self.bot_message.edit(embed=embed)

    @button(label="Emoji", style=ButtonStyle.green)
    async def emoji_button(self, button: Button, interaction: MessageInteraction):
        embed = EmbedFactory.static_embed(
            self.ctx,
            "View",
            path=f"view/emoji",
            description=f"Send an id/name of the emoji you want to view",
        )
        await self.bot_message.edit(embed=embed)
        await interaction.response.send_message("What id/name?", ephemeral=True)

        message: Message = await self.bot.wait_for("message", check=self.check)
        response = await FindSnowflake.find_emoji(self.bot, message.content)
        if not response:
            embed = EmbedFactory.static_embed(
                self.ctx,
                "View",
                path=f"view/emoji/notfound",
                description=f"I could not find an emoji with id/name {message.content}",
            )
            await message.add_reaction(ERROR)
            return await self.bot_message.edit(embed=embed)
        embed = EmbedFactory.static_embed(
            self.ctx,
            "View",
            path=f"view/emoji/info",
            description=user_info.format(
                response,
                joined_at=response.created_at.strftime("")
            )
        )
        await message.add_reaction(THUMBS_UP)
        await self.bot_message.edit(embed=embed)

    @button(label="Any", style=ButtonStyle.green)
    async def any_button(self, button: Button, interaction: MessageInteraction):
        ...