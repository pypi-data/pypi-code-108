import random
import aiosqlite
import os

from importlib_metadata import re

from .utils import EmbedFactory
from datetime import datetime
from dotenv import load_dotenv
from disnake import Embed
from disnake.ext.commands import Cog, Context, Bot, CheckFailure, command

def get_database() -> str:
    try:
        load_dotenv()
        database_path = os.environ["DATABASE_PATH"]
    except KeyError:
        try:
            os.mkdir("./db")
        except FileExistsError:
            pass
        database_path = "./db/database.db"
    return database_path


class MissingDatabase(Exception):
    """
    aiosqlite missingdatabase exception
    """


class Debug(Cog, name="debug"):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

        self.setup()
        self.bot.loop.create_task(self.connect_database())

    def get_uptime(self, _type: str = "strict") -> str:
        delta_uptime = datetime.utcnow() - self.bot._launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        if _type == "strict":
            return f"{days} days; {hours} hours; {minutes} minutes"
        elif _type == "lazy":
            return f"I've been up for **{days}** Days, **{hours}** Hours, **{minutes}** Minutes, and **{seconds}** Seconds!"

    def setup(self) -> None:
        bot = self.bot

        if not hasattr(bot, "_bot_messages"):
            self.bot._bot_messages = {}
        if not hasattr(bot, "_commands_ran"):
            self.bot._commands_ran = []
        if not hasattr(bot, "_paused"):
            self.bot._paused = False
        if not hasattr(bot, "_launch_time"):
            self.bot._launch_time = datetime.utcnow()
        if not hasattr(bot, "_get_uptime"):
            self.bot._get_uptime = self.get_uptime
        if not hasattr(bot, "_close"):
            self.bot._close = self._close

    async def connect_database(self):
        database_path = get_database()
        try:
            self.bot._db = await aiosqlite.connect(database_path)
        except aiosqlite.OperationalError:
            raise MissingDatabase(f"{database_path} isn't a valid path!")
        except Exception as e:
            print(e)

        cursor = await self.bot._db.cursor()
        await cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS "blacklist" (
                "guild_id"	INTEGER,
                "channel_id" INTEGER,
                "user_id"  INTEGER,
                "commands"	TEXT
            );
            """ 
        )
        await self.bot._db.commit()

    async def _close(self) -> None:
        await self.bot._db.close()
        await self.bot.close()

    async def bot_check(self, ctx: Context) -> bool:
        if ctx.command.hidden:
            if await self.bot.is_owner(ctx.author):
                return True

        for key, value in {
            "user_id": [ctx.author.id, "you"],
            "channel_id": [ctx.channel.id, "your channel"],
            "guild_id": [ctx.guild.id, "your guild"],
        }.items():
            cursor = await self.bot._db.cursor()
            await cursor.execute(
                f"Select commands from blacklist where {key}=?", (value[0],)
            )
            result = await cursor.fetchone()
            if result:
                result = result[0].split(",")
                if "all" in result:
                    await ctx.send(embed=EmbedFactory.check_fail(ctx, value[1]))
                    return False
                if ctx.command.name in result:
                    await ctx.send(embed=EmbedFactory.check_fail(ctx, value[1]))
                    return False
        return not self.bot._paused

    @command()
    async def t(self, ctx):
        print(".")

    @command()
    async def e(self, ctx):
        print(".")

    @command(hidden=True)
    async def debug(self, ctx):
        """
        echo:
            -> user/channel
                => send message

        blacklist:
            -> user/guild
                => blacklist

        leave_guild:
            -> guild
                => leave guild [confirm]

        change:
            -> avatar/name
                => change avatar/name [confirm]

        invokes:
            -> view all
            -> filter

        eval:
            -> code
                => eval code

        stats:
            => view bot stats (ping, uptime, etc)

        info:
            => view debugger info

        close:
            -> pause
                => pause bot
            -> unpause
                => unpause bot
            -> close
                => close bot [confirm]


        """

        from . import DebugView

        embed = EmbedFactory.static_embed(ctx, "Debug Controls")
        self.bot._bot_messages[ctx.message.id] = await ctx.send(
            embed=embed, view=DebugView(ctx)
        )

    @Cog.listener("on_slash_command")
    async def cache_slash_command(self, interaction):
        _id = random.randint(10000000, 100000000)
        self.bot._commands_ran.append(
            {
                "id": _id,
                "user": interaction.author.name,
                "guild": interaction.guild.name,
                "channel": interaction.channel.name,
                "command": interaction.command.name,
                "errored": interaction.command_failed,
                "bot_paused": self.bot._paused,
                "invoked_with": interaction.invoked_with,
                "message_content": interaction.message.content,
                "user-id": interaction.author.id,
                "guild-id": interaction.guild.id,
                "channel-id": interaction.channel.id,
                "timestamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                "raw timestamp": datetime.now(),
            }
        )

    @Cog.listener("on_command")
    async def cache_command(self, ctx):
        _id = random.randint(10000000, 100000000)
        self.bot._commands_ran.append(
            {
                "id": _id,
                "user": ctx.author.name,
                "guild": ctx.guild.name,
                "channel": ctx.channel.name,
                "command": ctx.command.name,
                "errored": ctx.command_failed,
                "bot_paused": self.bot._paused,
                "invoked_with": ctx.invoked_with,
                "message_content": ctx.message.content,
                "user-id": ctx.author.id,
                "guild-id": ctx.guild.id,
                "channel-id": ctx.channel.id,
                "timestamp": datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                "raw timestamp": datetime.now(),
            }
        )

    @Cog.listener("on_command_error")
    async def check_failure(self, ctx: Context, error: Exception):
        if isinstance(error, CheckFailure):
            return

        print(error)

    @Cog.listener("on_slash_command_error")
    async def slash_check_failure(self, ctx: Context, error: Exception):
        if isinstance(error, CheckFailure):
            return

        print(error)


def setup(bot: Bot) -> None:
    """Load the Debug extension"""

    bot.add_cog(Debug(bot))
