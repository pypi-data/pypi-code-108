from typing import List
from disnake_paginator import ButtonPaginator
from fuzzywuzzy import fuzz
from ..utils import EmbedFactory, MainMenu, get_bot_message
from ..constants import EMBED_COLOR

from disnake import Message, MessageInteraction, ButtonStyle
from disnake.ui import View, Button, button
from disnake.ext.commands import Context


def pretty(invokes: List[dict]) -> List[str]:
    output = []
    for iteration, invoke_dict in enumerate(invokes):
        output.append(
            "\n".join(
                [
                    f"-> {key}: {invokes[iteration][key]}"
                    for key in list(invoke_dict.keys())
                ]
            )
        )
    return output[::-1]


def find(invokes: List[dict], *, key: str, value: str) -> List[str]:
    output = [
        invoke_dict
        for num, invoke_dict in enumerate(invokes)
        if fuzz.ratio(str(invokes[num][key]), value.lower()) > 70
    ]
    return pretty(output)


class FindInvoke(View):
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

    @button(label="ID", style=ButtonStyle.green)
    async def id_button(self, button: Button, interaction: MessageInteraction):
        name = "id"

        embed = EmbedFactory.static_embed(
            self.ctx, "Find Invoke", path=f"invokes/find/{name}"
        )

        await self.bot_message.edit(embed=embed)
        await interaction.response.send_message(f"What {name}?", ephemeral=True)

        message = await self.bot.wait_for("message", check=self.check)
        output = find(self.bot._commands_ran, key=name, value=message.content)

        if not output:
            embed = EmbedFactory.static_embed(
                self.ctx,
                "Find Invoke",
                path=f"invokes/find/{name}/not_found",
                description=f"Invoke with {name} `{message.content}` not found",
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

    @button(label="USER_NAME", style=ButtonStyle.green)
    async def user_button(self, button: Button, interaction: MessageInteraction):
        name = "user"

        embed = EmbedFactory.static_embed(
            self.ctx, "Find Invoke", path=f"invokes/find/{name}"
        )

        await self.bot_message.edit(embed=embed)
        await interaction.response.send_message(f"What {name}?", ephemeral=True)

        message = await self.bot.wait_for("message", check=self.check)
        output = find(self.bot._commands_ran, key=name, value=message.content)

        if not output:
            embed = EmbedFactory.static_embed(
                self.ctx,
                "Find Invoke",
                path=f"invokes/find/{name}/not_found",
                description=f"Invoke with {name} `{message.content}` not found",
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

    @button(label="GUILD_NAME", style=ButtonStyle.green)
    async def guild_button(self, button: Button, interaction: MessageInteraction):
        name = "guild"

        embed = EmbedFactory.static_embed(
            self.ctx, "Find Invoke", path=f"invokes/find/{name}"
        )

        await self.bot_message.edit(embed=embed)
        await interaction.response.send_message(f"What {name}?", ephemeral=True)

        message = await self.bot.wait_for("message", check=self.check)
        output = find(self.bot._commands_ran, key=name, value=message.content)

        if not output:
            embed = EmbedFactory.static_embed(
                self.ctx,
                "Find Invoke",
                path=f"invokes/find/{name}/not_found",
                description=f"Invoke with {name} `{message.content}` not found",
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

    @button(label="CHANNEL_NAME", style=ButtonStyle.green)
    async def channel_button(self, button: Button, interaction: MessageInteraction):
        name = "channel"

        embed = EmbedFactory.static_embed(
            self.ctx, "Find Invoke", path=f"invokes/find/{name}"
        )

        await self.bot_message.edit(embed=embed)
        await interaction.response.send_message(f"What {name}?", ephemeral=True)

        message = await self.bot.wait_for("message", check=self.check)
        output = find(self.bot._commands_ran, key=name, value=message.content)

        if not output:
            embed = EmbedFactory.static_embed(
                self.ctx,
                "Find Invoke",
                path=f"invokes/find/{name}/not_found",
                description=f"Invoke with {name} `{message.content}` not found",
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

    @button(label="COMMAND_NAME", style=ButtonStyle.green)
    async def command_button(self, button: Button, interaction: MessageInteraction):
        name = "command"

        embed = EmbedFactory.static_embed(
            self.ctx, "Find Invoke", path=f"invokes/find/{name}"
        )

        await self.bot_message.edit(embed=embed)
        await interaction.response.send_message(f"What {name}?", ephemeral=True)

        message = await self.bot.wait_for("message", check=self.check)
        output = find(self.bot._commands_ran, key=name, value=message.content)

        if not output:
            embed = EmbedFactory.static_embed(
                self.ctx,
                "Find Invoke",
                path=f"invokes/find/{name}/not_found",
                description=f"Invoke with {name} `{message.content}` not found",
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

    @button(label="ERRORED", style=ButtonStyle.green)
    async def errored_button(self, button: Button, interaction: MessageInteraction):
        name = "errored"

        embed = EmbedFactory.static_embed(
            self.ctx,
            "Find Invoke",
            path=f"invokes/find/{name}",
            description="True/False",
        )

        await self.bot_message.edit(embed=embed)
        await interaction.response.send_message(f"True/False?", ephemeral=True)

        message = await self.bot.wait_for("message", check=self.check)
        output = find(self.bot._commands_ran, key=name, value=message.content)

        if not output:
            embed = EmbedFactory.static_embed(
                self.ctx,
                "Find Invoke",
                path=f"invokes/find/{name}/not_found",
                description=f"Invoke with {name} `{message.content}` not found",
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

    @button(label="BOT_PAUSED", style=ButtonStyle.green)
    async def bot_paused_button(self, button: Button, interaction: MessageInteraction):
        name = "bot_paused"

        embed = EmbedFactory.static_embed(
            self.ctx,
            "Find Invoke",
            path=f"invokes/find/{name}",
            description="True/False",
        )

        await self.bot_message.edit(embed=embed)
        await interaction.response.send_message(f"True/False?", ephemeral=True)

        message = await self.bot.wait_for("message", check=self.check)
        output = find(self.bot._commands_ran, key=name, value=message.content)

        if not output:
            embed = EmbedFactory.static_embed(
                self.ctx,
                "Find Invoke",
                path=f"invokes/find/{name}/not_found",
                description=f"Invoke with {name} `{message.content}` not found",
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

    @button(label="INVOKED_WITH", style=ButtonStyle.green)
    async def invoked_with_button(
        self, button: Button, interaction: MessageInteraction
    ):
        name = "invoked_with"

        embed = EmbedFactory.static_embed(
            self.ctx, "Find Invoke", path=f"invokes/find/{name}"
        )

        await self.bot_message.edit(embed=embed)
        await interaction.response.send_message(
            f"What was the command {name}?", ephemeral=True
        )

        message = await self.bot.wait_for("message", check=self.check)
        output = find(self.bot._commands_ran, key=name, value=message.content)

        if not output:
            embed = EmbedFactory.static_embed(
                self.ctx,
                "Find Invoke",
                path=f"invokes/find/{name}/not_found",
                description=f"Invoke with {name} `{message.content}` not found",
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

    @button(label="MESSAGE_CONTENT", style=ButtonStyle.green)
    async def message_content_button(
        self, button: Button, interaction: MessageInteraction
    ):
        name = "message_content"

        embed = EmbedFactory.static_embed(
            self.ctx, "Find Invoke", path=f"invokes/find/{name}"
        )

        await self.bot_message.edit(embed=embed)
        await interaction.response.send_message(f"What {name}?", ephemeral=True)

        message = await self.bot.wait_for("message", check=self.check)
        output = find(self.bot._commands_ran, key=name, value=message.content)

        if not output:
            embed = EmbedFactory.static_embed(
                self.ctx,
                "Find Invoke",
                path=f"invokes/find/{name}/not_found",
                description=f"Invoke with {name} `{message.content}` not found",
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

    @button(label="TIMESTAMP", style=ButtonStyle.green)
    async def timestamp_button(self, button: Button, interaction: MessageInteraction):
        name = "timestamp"


class Invokes(View):
    def __init__(self, ctx: Context):
        super().__init__()

        self.ctx = ctx
        self.bot = ctx.bot
        self.bot_message = get_bot_message(ctx)
        self.add_item(MainMenu(ctx))

    async def interaction_check(self, interaction: MessageInteraction) -> bool:
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )

    @button(label="All", style=ButtonStyle.green)
    async def all_invokes_button(self, button: Button, interaction: MessageInteraction):
        paginator = ButtonPaginator(
            title="All invokes",
            segments=pretty(self.bot._commands_ran),
            color=EMBED_COLOR,
            prefix="```yaml\n",
            suffix="```",
            button_style=ButtonStyle.green,
        )
        await paginator.start(interaction)

    @button(label="Find", style=ButtonStyle.green)
    async def find_invoke_button(self, button: Button, interaction: MessageInteraction):
        embed = EmbedFactory.static_embed(
            self.ctx,
            "Find Invoke",
            path=f"invokes/find",
        )

        await interaction.response.defer()
        await self.bot_message.edit(embed=embed, view=FindInvoke(self.ctx))
