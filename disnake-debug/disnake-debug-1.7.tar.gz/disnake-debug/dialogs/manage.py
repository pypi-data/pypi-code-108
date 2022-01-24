import asyncio
import os
import __main__
from ..utils import EmbedFactory, MainMenu, get_bot_message

from disnake import MessageInteraction, ButtonStyle
from disnake.ui import View, Button, button
from disnake.ext.commands import Context

newline = '\n'
class ConfirmShutdown(View):
    def __init__(self, ctx: Context, *, restart: bool = False):
        super().__init__()

        self.ctx = ctx
        self.restart = restart
        self.bot_message = get_bot_message(ctx)
        self.add_item(MainMenu(ctx))

    async def interaction_check(self, interaction: MessageInteraction) -> bool:
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )
        
    async def restart_bot(self) -> None:
        """
        restart bot, if stuck in event loop stderr will never be created, hence triggering bot shut down
        """

        path = os.getcwd()
        main = str(__main__.__file__).split('/')[-1]

        proc = await asyncio.create_subprocess_shell(
            f"cd {path} && python {main}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        self.stdout, self.stderr = await proc.communicate()
        embed = EmbedFactory.static_embed(
            self.ctx, "Uh oh!", path=f"manage/restart/error",
            description=f"stderr: {self.stderr.decode()}\nstdout: {self.stdout.decode() if self.stdout else 'no stdout'}{newline + 'I am not shutting of the bot because I would error on startup' if self.stderr else ''}"
        )
        await self.bot_message.edit(embed=embed)
        
    @button(label="Yes", style=ButtonStyle.green)
    async def confirm_button(self, button: Button, interaction: MessageInteraction):
        """
        close/restart bot
        """

        await interaction.response.defer()
        if not self.restart:
            embed = EmbedFactory.static_embed(
                self.ctx, "Turned off bot", path=f"manage/shut_down",
                description=f"The bot is now offline"
            )   
            await self.bot_message.edit(embed=embed)
            return await self.ctx.bot.close()
            
        asyncio.create_task(self.restart_bot())
        await asyncio.sleep(3)
        try:
            self.stderr
        except AttributeError:
            embed = EmbedFactory.static_embed(
                self.ctx, "Turned off bot", path=f"manage/restart",
                description=f"The bot is now offline"
            )  
            await self.bot_message.edit(embed=embed) 
            return await self.ctx.bot.close()
        

    @button(label="No", style=ButtonStyle.danger)
    async def cancel_button(self, button: Button, interaction: MessageInteraction):
        from . import DebugView

        embed = EmbedFactory.static_embed(self.ctx, "Debug Controls")
        await self.bot_message.edit(embed=embed, view=DebugView(self.ctx))


class Manage(View):
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

    @button(label="Pause", style=ButtonStyle.green)
    async def pause_button(self, button: Button, interaction: MessageInteraction):
        """
        pause the bot so it does not respond to commands
        """

        embed = EmbedFactory.static_embed(
            self.ctx,
            "Paused bot",
            path="manage/pause",
            description="Bot paused; commands locked",
        )
        bot = self.ctx.bot
        bot._paused = True

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed)

    @button(label="Resume", style=ButtonStyle.green)
    async def resume_button(self, button: Button, interaction: MessageInteraction):
        """
        unpause the bot
        """

        embed = EmbedFactory.static_embed(
            self.ctx,
            "Resumed bot",
            path="manage/resume",
            description="Resumed bot; commands unlocked",
        )
        bot = self.ctx.bot
        bot._paused = False

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed)

    @button(label="Restart", style=ButtonStyle.danger)
    async def restart_button(self, button: Button, interaction: MessageInteraction):
        """
        restart the bot
        """

        embed = EmbedFactory.static_embed(
            self.ctx, "Are you sure you want to restart?", path="manage/restart",
            description="WARNING: If there is an error on startup, the bot will not be able to start back up"
        )

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed, view=ConfirmShutdown(self.ctx, restart=True))

    @button(label="Shut down", style=ButtonStyle.danger)
    async def shutdown_button(self, button: Button, interaction: MessageInteraction):
        embed = EmbedFactory.static_embed(
            self.ctx, "Are you sure you want to shut the bot down?", path="manage/shut_down"
        )

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed, view=ConfirmShutdown(self.ctx))
