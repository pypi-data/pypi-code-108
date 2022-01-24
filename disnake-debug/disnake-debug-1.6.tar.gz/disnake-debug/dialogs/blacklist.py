from typing import Union
from ..utils import FindSnowflake, EmbedFactory, MainMenu, get_bot_message
from ..constants import THUMBS_UP, ERROR, BLACKLIST_HELP

from disnake import (
    MessageInteraction,
    ButtonStyle,
    User,
    Guild,
    TextChannel,
    Message,
)
from disnake.ui import View, Button, button
from disnake.ext.commands import Context


class BlacklistSnowflake(View):
    def __init__(
        self,
        ctx: Context,
        snowflake: Union[User, Guild, TextChannel],
        _type: str = "user",
    ):
        super().__init__()

        self.ctx = ctx
        self.bot = ctx.bot
        self.bot_message = get_bot_message(ctx)
        self.snowflake = snowflake
        self._type = _type
        self.add_item(MainMenu(ctx))

    def check(self, m: Message) -> bool:
        return m.author == self.ctx.author and m.channel == self.ctx.channel

    async def interaction_check(self, interaction: MessageInteraction) -> bool:
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )
        
    @button(label="Blacklist", style=ButtonStyle.green)
    async def blacklist_button(self, button: Button, interaction: MessageInteraction):
        cursor = await self.bot._db.cursor()
        await cursor.execute(
            f"SELECT * FROM blacklist WHERE {self._type}_id = ?", (
                self.snowflake.id,)
        )
        result = await cursor.fetchall()

        if not result:
            embed = EmbedFactory.static_embed(
                self.ctx,
                "Blacklist/Unblacklist",
                path=f"blacklist/{self._type}/choose/commands",
                description=BLACKLIST_HELP,
            )
            await self.bot_message.edit(embed=embed)
            await interaction.response.send_message(
                "What commands do you want to blacklist the user from?", ephemeral=True
            )
            message: Message = await self.bot.wait_for("message", check=self.check)
            await message.add_reaction(THUMBS_UP)

            content = ",".join([e.strip() for e in message.content.split(",")])
            if self._type == "user":
                result = (0, 0, self.snowflake.id, content)
            elif self._type == "channel":
                result = (0, self.snowflake.id, 0, content)
            elif self._type == "guild":
                result = (self.snowflake.id, 0, 0, content)

            await cursor.execute("Insert into blacklist values(?, ?, ?, ?)", result)
            await self.bot._db.commit()

            embed = EmbedFactory.static_embed(
                self.ctx,
                "Blacklist/Unblacklist",
                path=f"blacklist/",
                description=f"Blacklisted {self.snowflake.name} from commands: {content}",
            )
            return await self.bot_message.edit(
                embed=embed, view=Blacklist(self.ctx)
            )

    @button(label="Unblacklist", style=ButtonStyle.green)
    async def unblacklist_button(self, button: Button, interaction: MessageInteraction):
        cursor = await self.bot._db.cursor()
        await cursor.execute(
            f"SELECT * FROM blacklist WHERE {self._type}_id = ?", (
                self.snowflake.id,)
        )
        result = await cursor.fetchall()

        if not result:
            embed = EmbedFactory.static_embed(
                self.ctx,
                "Blacklist/Unblacklist",
                path=f"unblacklist/{self._type}/notfound",
                description=f"{self.snowflake.name} is not blacklisted from any commands!",
            )
            await self.bot_message.edit(embed=embed)
            return await interaction.response.defer()
        embed = EmbedFactory.static_embed(
            self.ctx,
            "Blacklist/Unblacklist",
            path=f"unblacklist/{self._type}/",
            description=f"I unblacklisted {self.snowflake.name} from all commands",
        )
        await self.bot_message.edit(embed=embed)
        await interaction.response.defer()

        cursor = await self.bot._db.cursor()
        await cursor.execute(
            f"DELETE FROM blacklist WHERE {self._type}_id = ?", (
                self.snowflake.id,)
        )
        await self.bot._db.commit()

        embed = EmbedFactory.static_embed(
            self.ctx,
            "Blacklist/Unblacklist",
            path=f"unblacklist/{self._type}/",
            description=f"I unblacklisted {self.snowflake.name} from all commands",
        )
        await self.bot_message.edit(embed=embed)


class Blacklist(View):
    def __init__(self, ctx: Context):
        super().__init__()

        self.ctx = ctx
        self.bot = ctx.bot
        self.bot_message = get_bot_message(ctx)
        self.add_item(MainMenu(ctx))

    def check(self, m: Message) -> bool:
        return m.author == self.ctx.author and m.channel == self.ctx.channel

    async def interaction_check(self, interaction: MessageInteraction) -> bool:
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )

    @button(label="User", style=ButtonStyle.green)
    async def blacklist_user_button(
        self, button: Button, interaction: MessageInteraction
    ):
        name = "user"

        embed = EmbedFactory.static_embed(
            self.ctx,
            "Blacklist/Unblacklist",
            path=f"blacklist/{name}",
            description="Send an id/name of the user you want to blacklist/unblacklist",
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
                    "Blacklist/Unblacklist",
                    path=f"blacklist/{name}/notfound",
                    description=f"I could not find {name} with id/name {message.content}",
                )
                await message.add_reaction(ERROR)
                return await self.bot_message.edit(embed=embed)
            if not isinstance(other_response, User):
                embed = EmbedFactory.static_embed(
                    self.ctx,
                    "Blacklist/Unblacklist",
                    path="blacklist/{name}/other",
                    description=f"I could not find a {name} user with id/name {message.content}, but i found a {type(other_response)} {other_response}",
                )
                await message.add_reaction(ERROR)
                return await self.bot_message.edit(embed=embed)

        if isinstance(response, list):
            embed = EmbedFactory.static_embed(
                self.ctx,
                "Blacklist/Unblacklist",
                path=f"blacklist/{name}/overload",
                description=f"You were too broad! I found multiple **{name}s** with name {message.content}",
            )
            await message.add_reaction(ERROR)
            return await self.bot_message.edit(embed=embed)

        embed = EmbedFactory.static_embed(
            self.ctx,
            "Blacklist/Unblacklist",
            path=f"blacklist/{name}/choose",
            description=f"I found {response}",
        )
        await message.add_reaction(THUMBS_UP)
        await self.bot_message.edit(
            embed=embed, view=BlacklistSnowflake(self.ctx, response)
        )

    @button(label="Channel", style=ButtonStyle.green)
    async def blacklist_channel_button(
        self, button: Button, interaction: MessageInteraction
    ):
        name = "channel"

        embed = EmbedFactory.static_embed(
            self.ctx,
            "Blacklist/Unblacklist",
            path=f"blacklist/{name}",
            description=f"Send an id/name of the {name} you want to blacklist/unblacklist",
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
                    "Blacklist/Unblacklist",
                    path=f"blacklist/{name}/notfound",
                    description=f"I could not find {name} with id/name {message.content}",
                )
                await message.add_reaction(ERROR)
                return await self.bot_message.edit(embed=embed)
            if not isinstance(other_response, TextChannel):
                embed = EmbedFactory.static_embed(
                    self.ctx,
                    "Blacklist/Unblacklist",
                    path="blacklist/{name}/other",
                    description=f"I could not find a {name} with id/name {message.content}, but i found a {type(other_response)} {other_response}",
                )
                await message.add_reaction(ERROR)
                return await self.bot_message.edit(embed=embed)

        if isinstance(response, list):
            embed = EmbedFactory.static_embed(
                self.ctx,
                "Blacklist/Unblacklist",
                path=f"blacklist/{name}/overload",
                description=f"You were too broad! I found multiple **{name}s** with name {message.content}",
            )
            await message.add_reaction(ERROR)
            return await self.bot_message.edit(embed=embed)

        embed = EmbedFactory.static_embed(
            self.ctx,
            "Blacklist/Unblacklist",
            path=f"blacklist/{name}/choose",
            description=f"I found {response}",
        )
        await message.add_reaction(THUMBS_UP)
        await self.bot_message.edit(
            embed=embed, view=BlacklistSnowflake(self.ctx, response)
        )

    @button(label="Guild", style=ButtonStyle.green)
    async def blacklist_guild_button(
        self, button: Button, interaction: MessageInteraction
    ):
        name = "guild"

        embed = EmbedFactory.static_embed(
            self.ctx,
            "Blacklist/Unblacklist",
            path=f"blacklist/{name}",
            description=f"Send an id/name of the {name} you want to blacklist/unblacklist",
        )
        await self.bot_message.edit(embed=embed)
        await interaction.response.send_message("What id/name?", ephemeral=True)

        message: Message = await self.bot.wait_for("message", check=self.check)
        response = await FindSnowflake.find_guild(self.bot, message.content)
        if not response:
            other_response = await FindSnowflake.find_any(self.bot, message.content)
            if not other_response:
                embed = EmbedFactory.static_embed(
                    self.ctx,
                    "Blacklist/Unblacklist",
                    path=f"blacklist/{name}/notfound",
                    description=f"I could not find {name} with id/name {message.content}",
                )
                await message.add_reaction(ERROR)
                return await self.bot_message.edit(embed=embed)
            if not isinstance(other_response, Guild):
                embed = EmbedFactory.static_embed(
                    self.ctx,
                    "Blacklist/Unblacklist",
                    path="blacklist/{name}/other",
                    description=f"I could not find a {name} with id/name {message.content}, but i found a {type(other_response)} {other_response}",
                )
                await message.add_reaction(ERROR)
                return await self.bot_message.edit(embed=embed)

        if isinstance(response, list):
            embed = EmbedFactory.static_embed(
                self.ctx,
                "Blacklist/Unblacklist",
                path=f"blacklist/{name}/overload",
                description=f"You were too broad! I found multiple **{name}s** with name {message.content}",
            )
            await message.add_reaction(ERROR)
            return await self.bot_message.edit(embed=embed)

        embed = EmbedFactory.static_embed(
            self.ctx,
            "Blacklist/Unblacklist",
            path=f"blacklist/{name}/choose",
            description=f"I found {response}",
        )
        await message.add_reaction(THUMBS_UP)
        await self.bot_message.edit(
            embed=embed, view=BlacklistSnowflake(self.ctx, response)
        )
