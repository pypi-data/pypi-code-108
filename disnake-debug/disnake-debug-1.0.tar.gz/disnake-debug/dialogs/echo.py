import os

from ..utils import FindSnowflake, EmbedFactory, MainMenu, get_bot_message
from disnake import (
    User, 
    TextChannel, 
    Message, 
    MessageInteraction, 
    ButtonStyle, 
    Embed
)
from disnake.abc import Messageable
from disnake.ui import View, Button, button
from disnake.ext.commands import Context

class ViewMessageable(View):
    def __init__(self, ctx: Context, messageable: Messageable):
        super().__init__()

        self.ctx = ctx
        self.bot = ctx.bot
        self.messageable = messageable
        self.bot_message = get_bot_message(ctx)
        self.embed = Embed(
            title=messageable.name,
            timestamp=self.ctx.message.created_at,
            colour=EMBED_COLOR
        ) 

        self.bot.add_listener(self.specific_channel_message, 'on_message')
        self.add_item(MainMenu(ctx))

    async def interaction_check(self, interaction: MessageInteraction) -> bool:
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )

    async def specific_channel_message(self, message: Message) -> None:
        print(message)
        if message.channel.id != self.messageable.id:
            return
        try:
            self.messages.append(f"{message.author.name}: {message.content}")
        except NameError:
            self.messages = [f"{message.author.name}: {message.content}" for message in await self.messageable.history(limit=10).flatten()]
        self.embed.description = '\n'.join(self.messages)

    @button(label="Send message", style=ButtonStyle.green)
    async def send_message_button(
        self, button: Button, interaction: MessageInteraction
    ): 
        ...

class EchoView(View):
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

    @button(label="Channel", style=ButtonStyle.green)
    async def channel_button(
        self, button: Button, interaction: MessageInteraction
    ): 
        name = "channel"

        embed = EmbedFactory.static_embed(
            self.ctx, 
            "Speak as the bot", 
            path=f"echo/{name}",
            description=f"Send an id/name of the {name} you want to view and send messages in"
        )
        await self.bot_message.edit(embed=embed)
        await interaction.response.send_message("What id/name?", ephemeral=True)
        
        message: Message = await self.bot.wait_for("message", check=self.check)
        response = await FindSnowflake.find_channel(self.bot, message.content)
        if not response:
            other_response = await FindSnowflake.find_any(self.bot, message.content)
            if not other_response:
                embed = EmbedFactory.static_embed(
                    self.ctx, 
                    "Speak as the bot", 
                    path=f"echo/{name}/notfound",
                    description=f"I could not find **{name}** with id/name {message.content}"
                )
                return await self.bot_message.edit(embed=embed)
            if not isinstance(other_response, TextChannel):
                embed = EmbedFactory.static_embed(
                    self.ctx, 
                    "Speak as the bot", 
                    path=f"echo/{name}/other",
                    description=f"I could not find a {name} with id/name {message.content}, but i found a {type(other_response)} {other_response}"
                )
                return await self.bot_message.edit(embed=embed)

        if isinstance(response, list):
            embed = EmbedFactory.static_embed(
                self.ctx, 
                "Speak as the bot", 
                path=f"echo/{name}/overload",
                description=f"You were too broad! I found multiple **{name}s** with name {message.content}"
            )
            return await self.bot_message.edit(embed=embed)

        embed = EmbedFactory.static_embed(
            self.ctx, 
            "Speak as the bot", 
            path=f"echo/{name}/view",
            description=f"I found {response}"
        )
        await self.bot_message.edit(embed=embed, view=ViewMessageable(self.ctx, response))

    @button(label="User", style=ButtonStyle.green)
    async def user_button(
        self, button: Button, interaction: MessageInteraction
    ):  
        name = "user"

        embed = EmbedFactory.static_embed(
            self.ctx, 
            "Speak as the bot", 
            path=f"echo/{name}",
            description=f"Send an id/name of the {name} you want to view and send messages in"
        )
        await self.bot_message.edit(embed=embed)
        await interaction.response.send_message("What id/name?", ephemeral=True)
        
        message: Message = await self.bot.wait_for("message", check=self.check)
        response = await FindSnowflake.find_user(self.bot, message.content)
        if not response:
            other_response = await FindSnowflake.find_any(self.bot, message.content)
            if not other_response:
                embed = EmbedFactory.static_embed(
                    self.ctx, 
                    "Speak as the bot", 
                    path=f"echo/{name}/notfound",
                    description=f"I could not find **{name}** with id/name {message.content}"
                )
                return await self.bot_message.edit(embed=embed)
            if not isinstance(other_response, User):
                embed = EmbedFactory.static_embed(
                    self.ctx, 
                    "Speak as the bot", 
                    path=f"echo/{name}/other",
                    description=f"I could not find a {name} user with id/name {message.content}, but i found a {type(other_response)} {other_response}"
                )
                return await self.bot_message.edit(embed=embed)

        if isinstance(response, list):
            embed = EmbedFactory.static_embed(
                self.ctx, 
                "Speak as the bot", 
                path=f"echo/{name}/overload",
                description=f"You were too broad! I found multiple **{name}s** with name {message.content}"
            )
            return await self.bot_message.edit(embed=embed)

        embed = EmbedFactory.static_embed(
            self.ctx, 
            "Speak as the bot", 
            path=f"echo/{name}/view",
            description=f"I found {response}"
        )
        await self.bot_message.edit(embed=embed, view=ViewMessageable(self.ctx, response))