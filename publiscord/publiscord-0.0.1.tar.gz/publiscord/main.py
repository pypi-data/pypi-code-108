import discord
from discord.ext import commands


class AppCmdPublish(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.channel.type == discord.ChannelType.news:
            await message.publish()
            return


def setup(bot):
    return bot.add_cog(AppCmdPublish(bot))
