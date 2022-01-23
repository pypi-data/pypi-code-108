from .utils import FindSnowflake, EmbedFactory, get_bot_message
from .constants import DESCRIPTION

from disnake import ButtonStyle, Message, MessageInteraction, TextChannel
from disnake.ui import View, Button, button
from disnake.ext.commands import Context

newline = "\n"
bot_statistics = """
-> Bot ping: {0}    
-> Bot name: {1.user.name}
-> Bot owners: {1.owner_ids}
-> Bot uptime: {2}
-> Total invokes: {3}
-> Servers in: {4}
-> Users: {5}
-> Channels: {6}
-> Prefix: {7}
-> Number of extensions loaded: {8}
"""


class DebugView(View):
    def __init__(self, ctx: Context):
        super().__init__()

        self.ctx = ctx
        self.bot = ctx.bot

    async def interaction_check(self, interaction: MessageInteraction) -> bool:
        self.bot_message = get_bot_message(self.ctx)

        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )

    def check(self, m: Message):
        return m.author == self.ctx.author and m.channel == self.ctx.channel

    @button(label="Blacklist", style=ButtonStyle.green)
    async def blacklist_button(self, button: Button, interaction: MessageInteraction):
        """
        buttons:
            -> user
            -> channel
                => blacklist user/channel
        """

        from . import BlacklistView

        embed = EmbedFactory.static_embed(
            self.ctx, "Blacklist/Unblacklist", path="blacklist"
        )

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed, view=BlacklistView(self.ctx))

    @button(label="Change", style=ButtonStyle.green)
    async def change_button(self, button: Button, interaction: MessageInteraction):
        """
        buttons:
            -> avatar
                => change avatar
            -> name
                => change name
        """

        from . import ChangeView

        embed = EmbedFactory.static_embed(
            self.ctx, "Change bot information", path="change"
        )

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed, view=ChangeView(self.ctx))

    @button(label="Echo", style=ButtonStyle.green)
    async def echo_button(self, button: Button, interaction: MessageInteraction):
        """
        buttons:
            ->
        """

        from . import ChannelView

        embed = EmbedFactory.static_embed(
            self.ctx,
            "Speak as the bot",
            path=f"echo/channel",
            description=f"Send an id/name of the channel you want to view and send messages in",
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
                    path=f"echo/channel/notfound",
                    description=f"I could not find channel with id/name {message.content}",
                )
                return await self.bot_message.edit(embed=embed)
            if not isinstance(other_response, TextChannel):
                embed = EmbedFactory.static_embed(
                    self.ctx,
                    "Speak as the bot",
                    path=f"echo/channel/other",
                    description=f"I could not find a channel with id/name {message.content}, but i found a {type(other_response)} {other_response}",
                )
                return await self.bot_message.edit(embed=embed)

        if isinstance(response, list):
            embed = EmbedFactory.static_embed(
                self.ctx,
                "Speak as the bot",
                path=f"echo/channel/overload",
                description=f"You were too broad! I found multiple **channels** with name {message.content}",
            )
            return await self.bot_message.edit(embed=embed)

        await interaction.send("Loading messages...this might take a while if the channel contains long messages")
        view = await ChannelView.create(self.ctx, response)
        await self.bot_message.edit(view=view)

    @button(label="Eval", style=ButtonStyle.green)
    async def eval_button(self, button: Button, interaction: MessageInteraction):
        """
        buttons:
            -> eval
            -> return eval
            -> dir eval
                => output
        """

        from . import EvalView

        embed = EmbedFactory.static_embed(
            self.ctx, "Evaluate code", path="eval")

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed, view=EvalView(self.ctx))

    @button(label="Invokes", style=ButtonStyle.green)
    async def invoke_button(self, button: Button, interaction: MessageInteraction):
        """
        buttons:

        """

        from . import InvokeView

        embed = EmbedFactory.static_embed(self.ctx, "Invokes", path="invokes")

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed, view=InvokeView(self.ctx))

    @button(label="Leave guild", style=ButtonStyle.green)
    async def leave_guild_button(self, button: Button, interaction: MessageInteraction):
        """
        buttons:
            -> find
                => leave guild [confirm]
        """

        from . import GuildView

        embed = EmbedFactory.static_embed(
            self.ctx, "Leave guild", path="leave_guild")

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed, view=GuildView(self.ctx))

    @button(label="Go to path", style=ButtonStyle.blurple)
    async def go_to_button(self, button: Button, interaction: MessageInteraction):
        """
        buttons:
            none
        """

        from .dialogs import (
            BlacklistView,
            ChangeView,
            CloseView,
            EchoView,
            EvalView,
            GuildView,
            InvokeView,
        )

        paths = {
            "blacklist": BlacklistView,
            "change": ChangeView,
            "close": CloseView,
            "echo": EchoView,
            "eval": EvalView,
            "invokes": InvokeView,
            "leave_guild": GuildView,
        }

        embed = EmbedFactory.static_embed(
            self.ctx,
            "Go to path",
            path="go_to",
            description="Type the path you want to go to (eg /blacklist/user)\nNot all paths are available because some require additional info (eg which guild to leave in leave_guild/leave)",
        )
        await self.bot_message.edit(embed=embed)
        await interaction.response.send_message("What path?", ephemeral=True)

        message: Message
        while (
            (message := await self.bot.wait_for("message", check=self.check))
        ).content.lower() != "q":
            content = message.content.lower()

            if content in paths:
                embed = EmbedFactory.static_embed(
                    self.ctx,
                    content.capitalize(),
                    path=f"{content}",
                    description=f"Moved to path {content}",
                )
                return await self.bot_message.edit(
                    embed=embed, view=paths[content](self.ctx)
                )

            embed = EmbedFactory.static_embed(
                self.ctx,
                "Go to path",
                path="go_to",
                description=f"That is not a valid path\nPaths are:\n{newline.join(['     -> ' + k for k in list(paths.keys())])}",
            )
            await self.bot_message.edit(embed=embed)
            await interaction.message.reply("Invalid path, try again")

    @button(label="Stats", style=ButtonStyle.blurple)
    async def stats_button(self, button: Button, interaction: MessageInteraction):

        """
        buttons:
            none
        """

        embed = EmbedFactory.static_embed(
            self.ctx,
            "Stats",
            path="stats",
            description=bot_statistics.format(
                round(self.bot.latency * 1000),
                self.bot,
                self.bot._get_uptime(),
                len(self.bot._commands_ran),
                len(self.bot.guilds),
                len(self.bot.users),
                len([e for e in self.bot.get_all_channels()]),
                self.bot.command_prefix,
                len(self.bot.extensions),
            ),
        )

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed)

    @button(label="Help", style=ButtonStyle.blurple)
    async def help_button(self, button: Button, interaction: MessageInteraction):
        """
        buttons:
            none
        """

        embed = EmbedFactory.static_embed(
            self.ctx,
            "Information about disnake-debug",
            path="help",
            description=DESCRIPTION,
        )

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed)

    @button(label="Close", style=ButtonStyle.danger)
    async def close_button(self, button: Button, interaction: MessageInteraction):
        """
        buttons:
            => close [confirm]
        """

        from . import CloseView

        embed = EmbedFactory.static_embed(self.ctx, "Close", path="exit")

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed, view=CloseView(self.ctx))
