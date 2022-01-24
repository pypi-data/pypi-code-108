import os
import asyncio

from ..utils import FindSnowflake, EmbedFactory, MainMenu, get_bot_message
from ..constants import THUMBS_UP, ERROR

from disnake import Message, MessageInteraction, ButtonStyle
from disnake.ui import View, Button, button
from disnake.ext.commands import Context, Bot

class Github(View):
    def __init__(self, ctx: Context):
        super().__init__()

        self.ctx = ctx
        self.bot: Bot = ctx.bot
        self.path = os.getcwd()
        self.bot_message = get_bot_message(ctx)
        self.add_item(MainMenu(ctx))

    async def interaction_check(self, interaction: MessageInteraction) -> bool:
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )

    def check(self, m: Message) -> bool:
        return m.author == self.ctx.author and m.channel == self.ctx.channel

    @button(label="Push", style=ButtonStyle.green)
    async def push_button(self, button: Button, interaction: MessageInteraction):
        if not '.git' in os.listdir(self.path):
            return await interaction.response.send_message("This command will not working because this is not a github directory (missing .git)")
        
        embed = EmbedFactory.static_embed(
            self.ctx, "Git push", path="github/push", 
            description="Pushing to github...What is the reason for this commit?"
        )
        await interaction.response.send_message("What reason?", ephemeral=True)

        message: Message = await self.bot.wait_for("message", check=self.check)
        git_commands = [
            ["git", "add", "."],
            ["git", "commit", "-m", message.content],
            ["git", "push"],
        ]

        for git_command in git_commands:
            process = await asyncio.create_subprocess_exec(
                git_command[0],
                *git_command[1:],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            output, error = await process.communicate()
            embed.description += f'[{" ".join(git_command)!r} exited with return code ```{process.returncode}```\n'

            if output:
                embed.description += f"**[stdout]**\n```yaml\n{output.decode()}```\n"
            if error:   
                embed.description += f"**[stderr]**\n```yaml\n{error.decode()}```\n"
        await self.bot_message.edit(embed=embed)


    @button(label="Pull", style=ButtonStyle.green)
    async def pull_button(self, button: Button, interaction: MessageInteraction):
        if not '.git' in os.listdir(self.path):
            return await interaction.response.send_message("This command will not working because this is not a github directory (missing .git)")

        await interaction.response.defer()

        embed = EmbedFactory.static_embed(
            self.ctx, "Git pull", path="github/pull", 
            description="Pulling from github"
        )
        git_commands = [
            ["git", "stash"],
            ["git", "pull", "--ff-only"]
        ]

        for git_command in git_commands:
            process = await asyncio.create_subprocess_exec(
                git_command[0],
                *git_command[1:],
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            output, error = await process.communicate()
            embed.description += f'[{" ".join(git_command)!r} exited with return code {process.returncode}\n'

            if output:
                embed.description += f"**[stdout]**\n```yaml\n{output.decode()}```\n"
            if error:   
                embed.description += f"**[stderr]**\n```yaml\n{error.decode()}```\n"
        await self.bot_message.edit(embed=embed)