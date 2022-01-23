import imp
from json import load
import os

from dotenv import load_dotenv
from typing import Type, Union, Optional
from disnake import (
    ButtonStyle,
    Embed,
    Message,
    MessageInteraction,
    Guild,
    TextChannel,
    User,
    utils,
)
from disnake.ui import Button
from disnake.ext.commands import Context, Bot

newline = "\n"


class InvalidEnv(Exception):
    """ """


try:
    load_dotenv()
    os.environ["EMBED_COLOR"]
except KeyError:
    with open("./.env", "a") as env:
        env.write("\n#disnake-debug\nEMBED_COLOR = 0x0000ff")
try:
    EMBED_COLOR = int(os.environ["EMBED_COLOR"], 16)
except (TypeError, ValueError):
    raise InvalidEnv("EMBED_COLOR must be hex")


def get_bot_message(ctx: Context) -> Message:
    return ctx.bot._bot_messages[ctx.message.id]


def clean_code(content: str):
    if content.startswith("```py"):
        content = content[5:-3]
    content = content.strip("`")
    content = (
        content.replace("‘", "'").replace(
            "“", '"').replace("”", '"').replace("’", "'")
    )
    return content


class FindSnowflake:
    @staticmethod
    async def find_any(bot: Bot, query: str) -> Union[User, Guild, TextChannel, None]:
        if not query.isalpha():  # id
            _id = int(query)

            user = bot.get_user(_id)
            if user:
                return user
            user = await bot.fetch_user(_id)
            if user:
                return user

            guild = bot.get_guild(_id)
            if guild:
                return guild
            guild = await bot.fetch_guild(_id)
            if guild:
                return guild

            channel = bot.get_channel(_id)
            if isinstance(channel, TextChannel):
                return channel
            channel = await bot.fetch_channel(_id)
            if isinstance(channel, TextChannel):
                return channel

        # name
        user = utils.get(bot.users, name=query)
        if user:
            return user

        guild = utils.get(bot.guilds, name=query)
        if guild:
            return guild

        channel = utils.get(bot.get_all_channels(), name=query)
        if channel:
            return channel

    @staticmethod
    async def find_user(bot: Bot, query: str) -> Optional[User]:
        if not query.isalpha():  # id
            _id = int(query)

            user = bot.get_user(_id)
            if user:
                return user
            user = await bot.fetch_user(_id)
            if user:
                return user
        user = utils.get(bot.users, name=query)
        if user:
            return user

    @staticmethod
    async def find_guild(bot: Bot, query: str) -> Optional[Guild]:
        if not query.isalpha():  # id
            _id = int(query)

            guild = bot.get_guild(_id)
            if guild:
                return guild
            guild = await bot.fetch_guild(_id)
            if guild:
                return guild

        guild = utils.get(bot.guilds, name=query)
        if guild:
            return guild

    @staticmethod
    async def find_channel(bot: Bot, query: str) -> Optional[TextChannel]:
        if not query.isalpha():  # id
            _id = int(query)

            channel = bot.get_channel(_id)
            if isinstance(channel, TextChannel):
                return channel
            channel = await bot.fetch_channel(_id)
            if isinstance(channel, TextChannel):
                return channel

        channel = utils.get(bot.get_all_channels(), name=query)
        if channel:
            return channel


class EmbedFactory:
    """Embed factory"""

    @staticmethod
    def static_embed(
        ctx: Context,
        title: str,
        *,
        path: str = None,
        description: str = None,
        markdown: str = "yaml",
    ) -> Embed:
        return (
            Embed(
                title=title,
                colour=EMBED_COLOR,
                description=f"```yaml\nCurrent path: /{path or ''}```{'```' + markdown + newline + description + '```' if description else ''}",
                timestamp=ctx.message.created_at,
            )
            .set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)
            .set_footer(
                text=f"Bot ping: {ctx.bot.latency * 1000:.0f} || Uptime: {ctx.bot._get_uptime()}"
            )
        )

    @staticmethod
    def check_fail(
        ctx: Context,
        description: str,
    ) -> Embed:
        return Embed(
            title="Uh oh",
            description=f"One of my owners has `blacklisted` {description} from using this command.",
            colour=EMBED_COLOR,
        ).set_author(name=ctx.author.name, icon_url=ctx.author.avatar.url)


class MainMenu(Button):
    def __init__(self, ctx: Context):
        super().__init__(style=ButtonStyle.danger, label="Back")
        self.ctx = ctx
        self.bot_message = get_bot_message(ctx)

    async def callback(self, interaction: MessageInteraction):
        from . import DebugView

        embed = EmbedFactory.static_embed(self.ctx, "Debug Controls")

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed, view=DebugView(self.ctx))
