import random

from ..utils import FindSnowflake, EmbedFactory, MainMenu, get_bot_message
from ..constants import THUMBS_UP, ERROR
from typing import Union

from disnake import Message, MessageInteraction, ButtonStyle, TextChannel, Guild
from disnake.ui import View, Button, button
from disnake.ext.commands import Context, Bot

user_info = """
Name: {0.name}
Discriminator: {0.discriminator}
Id: {0.id}
Joined discord: {joined_at}
Flags: {flags}
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
Owner: {0.owner.name}#{0.owner.descriminator}
Members: {members}
Bots: {bots}
Roles: {roles}
Channels: {channels}
Created at: {created_at}
Invite: {invite}
"""

emoji_info = """
Name: {0.name}
Id: {0.id}
Guild id: {0.guild.id}
Created at: {created_at}
"""

class ViewInfo(View):
    def __init__(self, ctx: Context):
        super().__init__()

        self.ctx = ctx
        self.bot: Bot = ctx.bot
        self.bot_message = get_bot_message(ctx)
        self.add_item(MainMenu(ctx))

    def check(self, m: Message) -> bool:
        return m.author == self.ctx.author and m.channel == self.ctx.channel

    async def interaction_check(self, interaction: MessageInteraction) -> bool:
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )

    async def get_invite(self, channel: Union[TextChannel, Guild]) -> str:
        if isinstance(channel, Guild):
            channel = random.choice(channel.text_channels)
        return await channel.create_invite()

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
                joined_at=response.created_at.strftime("%m/%d/%Y"),
                flags=', '.join([f"{k.name}" for k in response.public_flags.all()]),
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
                created_at=response.created_at.strftime("%m/%d/%Y"),
                invite=await self.get_invite(response)    
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
                created_at=response.created_at.strftime("%m/%d/%Y"),
                invite=await self.get_invite(response),
                bots=len([k for k in response.members if k.bot]),
                channels=len(response.text_channels),
                roles=len(response.roles),
                members=len([k for k in response.members if not k.bot]),
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
            f"View Emoji: {response}",
            path=f"view/emoji/info",
            description=emoji_info.format(
                response,
                created_at=response.created_at.strftime("%m/%d/%Y"),
            )
        )
        embed.description += f"**Emoji:** {response}"
        await message.add_reaction(THUMBS_UP)
        await self.bot_message.edit(embed=embed)