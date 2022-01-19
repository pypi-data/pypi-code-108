import random

from ..utils import EmbedFactory
from datetime import datetime
from disnake.ext.commands import (
    Cog, 
    Context, 
    Bot, 
    command
)

class Debug(Cog, name='debug'):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

        if not hasattr(bot, 'bot_messages'):
            self.bot.bot_messages = {}
        if not hasattr(bot, 'commands_ran'):
            self.bot.commands_ran = []

    async def cog_check(self, ctx: Context) -> bool:
        return await self.bot.is_owner(ctx.author)

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

        close:
            => close bot [confirm]
        """ 

        from . import DebugView

        embed = EmbedFactory.static_embed(ctx, "Debug Controls")
        self.bot.bot_messages[ctx.message.id] = await ctx.send(embed=embed, view=DebugView(ctx))

    @Cog.listener('on_slash_command')
    async def cache_slash_command(self, interaction): 
        self.bot.commands_ran.append(
            {
                'id': random.randint(100000, 1000000),
                'user': interaction.author,
                'guild': interaction.guild.name,
                'channel': interaction.channel.name,
                'invoked_with': interaction.invoked_with,
                'message_content': interaction.message.content,
                'command': interaction.command,
                'errored': interaction.command_failed,
                'timestamp': datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                'raw timestamp': datetime.now(),
                'user-id': interaction.author.id,
                'guild-id': interaction.guild.id,
                'channel-id': interaction.channel.id,
            }   
        )

    @Cog.listener('on_command')
    async def cache_command(self, ctx):
        self.bot.commands_ran.append(
            {
                'id': random.randint(100000, 1000000),
                'user': ctx.author,
                'guild': ctx.guild.name,
                'channel': ctx.channel.name,
                'invoked_with': ctx.invoked_with,
                'message_content': ctx.message.content,
                'command': ctx.command,
                'errored': ctx.command_failed,
                'timestamp': datetime.now().strftime("%m/%d/%Y, %H:%M:%S"),
                'raw timestamp': datetime.now(),
                'user-id': ctx.author.id,
                'guild-id': ctx.guild.id,
                'channel-id': ctx.channel.id,
            }
        )


def setup(bot: Bot) -> None:
    """ Load the Debug extension """

    bot.add_cog(Debug(bot))