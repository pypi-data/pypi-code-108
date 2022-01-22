from ..utils import EmbedFactory, get_bot_message

from disnake import ButtonStyle, MessageInteraction
from disnake.ui import View, Button, button
from disnake.ext.commands import Context

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
DESCRIPTION = """
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

    @button(label="Echo", style=ButtonStyle.green)
    async def echo_button(
        self, button: Button, interaction: MessageInteraction
    ):
        """
        buttons:
            -> 
        """

        from . import EchoView

        embed = EmbedFactory.static_embed(
            self.ctx, 
            "View messageable", 
            path="echo"
        )

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed, view=EchoView(self.ctx))

    @button(label="Blacklist", style=ButtonStyle.green)
    async def blacklist_button(
        self, button: Button, interaction: MessageInteraction
    ):
        """
        buttons:
            -> user
            -> channel
                => blacklist user/channel   
        """

        from . import BlacklistView

        embed = EmbedFactory.static_embed(
            self.ctx, 
            "Blacklist/Unblacklist", 
            path="blacklist"
        )

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed, view=BlacklistView(self.ctx))

    @button(label="Leave guild", style=ButtonStyle.green)
    async def leave_guild_button(
        self, button: Button, interaction: MessageInteraction
    ):
        """
        buttons:
            -> find
                => leave guild [confirm]
        """

        from . import GuildView

        embed = EmbedFactory.static_embed(
            self.ctx, 
            "Leave guild", 
            path="leave_guild"
        )

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed, view=GuildView(self.ctx))

    @button(label="Change", style=ButtonStyle.green)
    async def change_button(
        self, button: Button, interaction: MessageInteraction
    ):  
        """
        buttons:
            -> avatar
                => change avatar
            -> name
                => change name
        """

        from . import ChangeView
        
        embed = EmbedFactory.static_embed(
            self.ctx, 
            "Change bot information", 
            path="change"
        )

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed, view=ChangeView(self.ctx))

    @button(label="Invokes", style=ButtonStyle.green)
    async def invoke_button(
        self, button: Button, interaction: MessageInteraction
    ):  
        """
        buttons:
            
        """

        from . import InvokeView

        embed = EmbedFactory.static_embed(
            self.ctx, 
            "Invokes", 
            path="invokes"
        )

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed, view=InvokeView(self.ctx))

    @button(label="Eval", style=ButtonStyle.green)
    async def eval_button(
        self, button: Button, interaction: MessageInteraction
    ):  
        """
        buttons:
            -> eval 
            -> return eval
            -> dir eval
                => output
        """

        from . import EvalView

        embed = EmbedFactory.static_embed(
            self.ctx, 
            "Evaluate code", 
            path="eval"
        )

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed, view=EvalView(self.ctx))

    @button(label="Stats", style=ButtonStyle.blurple)
    async def stats_button(
        self, button: Button, interaction: MessageInteraction
    ):  

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
            )
        )

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed)

    @button(label="Info", style=ButtonStyle.blurple)
    async def info_button(
        self, button: Button, interaction: MessageInteraction
    ):  
        """
        buttons:
            none
        """

        embed = EmbedFactory.static_embed(
            self.ctx, 
            "Information about disnake-debug", 
            path="info",
            description=DESCRIPTION
        )

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed)

    @button(label="Close", style=ButtonStyle.danger)
    async def close_button(
        self, button: Button, interaction: MessageInteraction
    ):  
        """
        buttons:
            => close [confirm]
        """

        from . import CloseView

        embed = EmbedFactory.static_embed(
            self.ctx, 
            "Close", 
            path="exit"
        )

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed, view=CloseView(self.ctx))