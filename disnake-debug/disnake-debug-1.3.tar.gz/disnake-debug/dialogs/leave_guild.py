from ..utils import EmbedFactory, MainMenu, get_bot_message
from fuzzywuzzy import fuzz
from typing import List

from disnake import MessageInteraction, SelectOption, Guild, Forbidden, ButtonStyle
from disnake.ui import Select, View, Button, button
from disnake.ext.commands import Bot, Context


class Utilities:
    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx
        self.bot = ctx.bot
        self.bot_message = get_bot_message(ctx)

    async def other_guilds(self, interaction: MessageInteraction, clicked: str) -> None:
        guilds: List[Guild] = [
            k for k in self.bot.guilds if ord(k.name.lower()) not in range(96, 123)
        ]
        if not guilds:
            embed = EmbedFactory.static_embed(
                self.ctx,
                f"Leave guild",
                path="leave_guild/notfound",
                description="I could not find any guilds that have special characters at the start!",
            )
            await interaction.response.defer()
            return await self.bot_message.edit(embed=embed)

        embed = EmbedFactory.static_embed(
            self.ctx,
            f"Leave guild",
            path="leave_guild/choose",
            description="I am in these servers:\n"
            + "\n".join([f"-> guild.name" for guild in guilds]),
        )
        await self.bot_message.edit(embed=embed)
        await interaction.response.send_message(
            "Which guild would you like me to leave?"
        )
        for item in self.bot_message.components:
            if isinstance(item, Select):
                item.disabled = True
        await self.bot_message.edit(embed=embed, view=self)

        message = await self.bot.wait_for(
            "message",
            check=lambda m: m.author == self.ctx.author
            and m.channel == self.ctx.channel,
        )
        selected_guild = max(
            [[guild, fuzz.ratio(message.content, guild.name)]
             for guild in guilds],
            key=lambda m: m[1],
        )

        embed = EmbedFactory.static_embed(
            self.ctx,
            f"Leave guild",
            path="leave_guild/choose/confirm",
            description=f"Are you sure you want me to leave {selected_guild.name}?",
        )
        await self.bot_message.edit(
            embed=embed, view=LeaveGuildConfirm(self.ctx, selected_guild)
        )

    async def find_guilds(self, interaction: MessageInteraction, clicked: str) -> None:
        guilds: List[Guild] = [
            k for k in self.bot.guilds if k.name.lower().startswith(clicked)
        ]
        if not guilds:
            embed = EmbedFactory.static_embed(
                self.ctx,
                f"Leave guild",
                path="leave_guild/notfound",
                description=f"I could not find any guilds starting with {clicked}",
            )
            await interaction.response.defer()
            return await self.bot_message.edit(embed=embed)

        embed = EmbedFactory.static_embed(
            self.ctx,
            f"Leave guild",
            path="leave_guild/choose",
            description=", ".join([guild.name for guild in guilds]),
        )
        await self.bot_message.edit(embed=embed)
        await interaction.response.send_message(
            "Which guild would you like me to leave?"
        )
        view = View()
        view.add_item(MainMenu(self.ctx))
        await self.bot_message.edit(embed=embed, view=view)

        message = await self.bot.wait_for(
            "message",
            check=lambda m: m.author == self.ctx.author
            and m.channel == self.ctx.channel,
        )
        selected_guild = max(
            [[guild, fuzz.ratio(message.content, guild.name)]
             for guild in guilds],
            key=lambda m: m[1],
        )[0]

        embed = EmbedFactory.static_embed(
            self.ctx,
            f"Leave guild",
            path="leave_guild/choose/confirm",
            description=f"Are you sure you want me to leave {selected_guild.name}?",
        )
        await self.bot_message.edit(
            embed=embed, view=LeaveGuildConfirm(self.ctx, selected_guild)
        )


class LeaveGuildConfirm(View):
    def __init__(self, ctx: Context, guild: Guild):
        super().__init__()

        self.ctx = ctx
        self.bot_message = get_bot_message(ctx)
        self.guild = guild
        self.add_item(MainMenu(ctx))

    async def interaction_check(self, interaction: MessageInteraction) -> bool:
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )

    @button(label="Yes", style=ButtonStyle.green)
    async def confirm_button(self, button: Button, interaction: MessageInteraction):
        embed = EmbedFactory.static_embed(
            self.ctx,
            f"Leave guild",
            path="leave_guild/leave",
            description=f"Left {self.guild.name}",
        )

        await self.bot_message.edit(embed=embed)
        await self.guild.leave()

        try:
            await self.bot_message.edit(view=Guild(self.ctx))
        except Forbidden:
            pass

    @button(label="No", style=ButtonStyle.danger)
    async def cancel_button(self, button: Button, interaction: MessageInteraction):
        embed = EmbedFactory.static_embed(
            self.ctx,
            f"Leave guild",
            path="leave_guild/cancel",
            description=f"Didn't leave {self.guild.name}",
        )
        await self.bot_message.edit(embed=embed, view=Guild(self.ctx))


class SelectPZ(Select):
    def __init__(self, ctx: Context):
        super().__init__()

        self.bot = ctx.bot
        self.utils = Utilities(ctx)
        self.options = [
            SelectOption(label=str(k), value=str(k))
            for k in [chr(a) for a in range(112, 123)]
        ]
        self.options.append(SelectOption(label="Other", value="other"))

    async def callback(self, interaction: MessageInteraction) -> None:
        clicked = self.values[0]
        if clicked == "other":
            return await self.utils.find_other_guilds(interaction)
        await self.utils.find_guilds(interaction)


class SelectAO(Select):
    def __init__(self, ctx: Context):
        super().__init__()

        self.bot = ctx.bot
        self.utils = Utilities(ctx)
        self.options = [
            SelectOption(label=str(k), value=str(k))
            for k in [chr(a) for a in range(97, 112)]
        ]
        self.options.append(SelectOption(label="Other", value="other"))

    async def callback(self, interaction: MessageInteraction) -> None:
        clicked = self.values[0]
        if clicked == "other":
            return await self.utils.find_other_guilds(interaction, clicked)
        await self.utils.find_guilds(interaction, clicked)


class Guild(View):
    def __init__(self, ctx: Context):
        super().__init__()

        self.ctx = ctx
        self.add_item(SelectAO(ctx))
        self.add_item(SelectPZ(ctx))
        self.add_item(MainMenu(ctx))

    async def interaction_check(self, interaction: MessageInteraction) -> bool:
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )
