from disnake import MessageInteraction, SelectOption
from disnake.ui import Select, View
from disnake.ext.commands import Bot, Context

class Utilities:
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    async def other_guilds(self, interaction: MessageInteraction, clicked: str) -> None:
        ...

    async def find_guilds(self, interaction: MessageInteraction, clicked: str) -> None:
        guilds = [k for k in list(map(lambda m: m.name.lower(), self.bot.guilds)) if k.startswith(clicked)]
        print(guilds)

class SelectPZ(Select):
    def __init__(self, ctx: Context):
        super().__init__()

        self.bot = ctx.bot
        self.utils = Utilities(ctx.bot)
        self.options = [
            SelectOption(label=str(k), value=str(k)) for k in [chr(a) for a in range(112, 123)]
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
        self.utils = Utilities(ctx.bot)
        self.options = [
            SelectOption(label=str(k), value=str(k)) for k in [chr(a) for a in range(97, 112)]
        ]
        self.options.append(SelectOption(label="Other", value="other"))

    async def callback(self, interaction: MessageInteraction) -> None:
        clicked = self.values[0]
        if clicked == "other":
            return await self.utils.find_other_guilds(interaction, clicked)
        await self.utils.find_guilds(interaction, clicked)

class GuildView(View):
    async def interaction_check(self, interaction: MessageInteraction) -> bool:
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )

    def __init__(self, ctx: Context):
        super().__init__()

        self.ctx = ctx
        self.add_item(SelectAO(ctx))
        self.add_item(SelectPZ(ctx))