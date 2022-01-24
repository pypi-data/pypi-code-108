import disnake
import io
import contextlib
import textwrap

from traceback import format_exception
from disnake_paginator import ButtonPaginator
from ..utils import EMBED_COLOR, EmbedFactory, MainMenu, clean_code, get_bot_message

from disnake import MessageInteraction, ButtonStyle, Message
from disnake.ui import View, Button, button
from disnake.ext import commands
from disnake.ext.commands import Context


async def eval_code(
    message: Message, local_variables: dict, method: str = "None"
) -> str:
    code = clean_code(message.content)
    message = clean_code(message.content)

    stdout = io.StringIO()
    if method == "dir":
        code = f"print(dir({code}))"

    elif method == "return":
        code = f"return {code}"

    try:
        with contextlib.redirect_stdout(stdout):
            exec(
                f"async def func():\n{textwrap.indent(code, '    ')}",
                local_variables,
            )
            obj = await local_variables["func"]()
            result = f"{stdout.getvalue()}{obj}\n"

    except Exception as e:
        result = "".join(format_exception(e, e, e.__traceback__))
        pass

    result = result.replace("`", "")
    message = message.replace("`", "")

    if result.replace("\n", "").endswith("None") and result != "None":
        result = result[:-5]
    if len(result) < 2000:
        return f"In: {message}\nOut: {result}"

    return [result[i: i + 2000] for i in range(0, len(result), 2000)]


class Eval(View):
    def __init__(self, ctx: Context):
        super().__init__()

        self.ctx = ctx
        self.bot = ctx.bot
        self.bot_message = get_bot_message(ctx)
        self.vars = {
            "disnake": disnake,
            "commands": commands,
            "bot": ctx.bot,
            "client": ctx.bot,
            "ctx": ctx,
            "channel": ctx.channel,
            "author": ctx.author,
            "guild": ctx.guild,
            "message": ctx.message,
        }

        self.add_item(MainMenu(ctx))

    async def interaction_check(self, interaction: MessageInteraction) -> bool:
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )

    @button(label="Eval", style=ButtonStyle.green)
    async def eval_button(self, button: Button, interaction: MessageInteraction):
        """
        evals content
        """

        embed = EmbedFactory.static_embed(
            self.ctx, "Evaluate code", path="eval/code")

        await self.bot_message.edit(embed=embed)
        await interaction.response.send_message(
            "What code would you like to evaluate?", ephemeral=True
        )

        message = await self.bot.wait_for(
            "message",
            check=lambda m: m.author == self.ctx.author
            and m.channel == self.ctx.channel,
        )
        output = await eval_code(message, self.vars)

        if not isinstance(output, list):
            embed = EmbedFactory.static_embed(
                self.ctx,
                "Evaluate code",
                path="eval/code/run",
                description=output,
                markdown="py",
            )
            return await self.bot_message.edit(embed=embed)
        paginator = ButtonPaginator(
            title="All invokes",
            segments=output,
            color=EMBED_COLOR,
            prefix="```yaml\n",
            suffix="```",
            button_style=ButtonStyle.green,
        )
        await paginator.start(interaction, deferred=True)

    @button(label="Return Eval", style=ButtonStyle.green)
    async def return_eval_button(self, button: Button, interaction: MessageInteraction):
        """
        returns content
        """

        embed = EmbedFactory.static_embed(
            self.ctx, "Evaluate code", path="eval/code")

        await self.bot_message.edit(embed=embed)
        await interaction.response.send_message(
            "What code would you like to evaluate?", ephemeral=True
        )

        message = await self.bot.wait_for(
            "message",
            check=lambda m: m.author == self.ctx.author
            and m.channel == self.ctx.channel,
        )
        output = await eval_code(message, self.vars, "return")

        if not isinstance(output, list):
            embed = EmbedFactory.static_embed(
                self.ctx,
                "Evaluate code",
                path="eval/code/run",
                description=output,
                markdown="py",
            )
            return await self.bot_message.edit(embed=embed)
        paginator = ButtonPaginator(
            title="All invokes",
            segments=output,
            color=EMBED_COLOR,
            prefix="```yaml\n",
            suffix="```",
            button_style=ButtonStyle.green,
        )
        await paginator.start(interaction, deferred=True)

    @button(label="Dir Eval", style=ButtonStyle.green)
    async def dir_eval_button(self, button: Button, interaction: MessageInteraction):
        """
        prints the dir of content
        """

        embed = EmbedFactory.static_embed(
            self.ctx, "Evaluate code", path="eval/code")

        await self.bot_message.edit(embed=embed)
        await interaction.response.send_message(
            "What code would you like to evaluate?", ephemeral=True
        )

        message = await self.bot.wait_for(
            "message",
            check=lambda m: m.author == self.ctx.author
            and m.channel == self.ctx.channel,
        )
        output = await eval_code(message, self.vars, "dir")

        if not isinstance(output, list):
            embed = EmbedFactory.static_embed(
                self.ctx,
                "Evaluate code",
                path="eval/code/run",
                description=output,
                markdown="py",
            )
            return await self.bot_message.edit(embed=embed)
        paginator = ButtonPaginator(
            title="All invokes",
            segments=output,
            color=EMBED_COLOR,
            prefix="```yaml\n",
            suffix="```",
            button_style=ButtonStyle.green,
        )
        await paginator.start(interaction, deferred=True)
