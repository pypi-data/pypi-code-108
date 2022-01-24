from typing import List
from ..utils import EMBED_COLOR, MainMenu, get_bot_message
from ..constants import THUMBS_UP

from disnake import HTTPException, TextChannel, Message, MessageInteraction, ButtonStyle, Embed
from disnake.ui import View, Button, button
from disnake.ext.commands import Context, Bot


class Channel(View):
    def __init__(self, ctx: Context, channel: TextChannel):
        super().__init__()

        self.ctx = ctx
        self.bot: Bot = ctx.bot
        self.channel = channel
        self.bot_message = get_bot_message(ctx)
        self.embed = Embed(
            title="Viewing: " + channel.name,
            timestamp=self.ctx.message.created_at,
            colour=EMBED_COLOR,
        )
        self.messages: List[Message] = []
        self.bot.add_listener(self.specific_channel_message, "on_message")
        self.bot.add_listener(self.specific_channel_message_delete, "on_message_delete")
        self.bot.add_listener(self.specific_channel_message_edited, "on_message_edit")
        self.add_item(MainMenu(ctx))

    def check(self, m: Message) -> bool:
        return m.author == self.ctx.author and m.channel == self.ctx.channel

    async def interaction_check(self, interaction: MessageInteraction) -> bool:
        return (
            interaction.author == self.ctx.author
            and interaction.channel == self.ctx.channel
        )

    @classmethod
    async def create(cls, ctx: Context, channel: TextChannel):
        self = Channel(ctx, channel)
        await self.load_messages()
        return self

    async def load_messages(self) -> None:
        self.messages = [
            f"[{message.id}] {message.author.name}: {message.content}"
            for message in await self.channel.history(limit=30).flatten()
        ][::-1]
        self.embed.description = "```yaml\n" + "\n".join(self.messages) + "```"
        i = 29
        while True:
            try:
                await self.bot_message.edit(
                    embed=self.embed
                )
                return
            except HTTPException:
                i -= 2
                self.messages = [
                    f"[{message.id}] {message.author.name}: {message.content}"
                    for message in await self.channel.history(limit=i).flatten()
                ][::-1]
                self.embed.description = "```yaml\n" + "\n".join(self.messages) + "```"

    async def update_embed(self, message: Message) -> None:
        self.messages.pop(0)
        self.messages.append(f"[{message.id}] {message.author.name}: {message.content}")
        self.embed.description = "```yaml\n" + "\n".join(self.messages) + "```"
        
        while True:
            try:
                await self.bot_message.edit(
                    embed=self.embed
                )
                return
            except HTTPException:
                self.messages.pop(0)
                self.embed.description = "```yaml\n" + "\n".join(self.messages) + "```"
            
    async def message_deleted(self, message: Message) -> None:
        if not any(
            str(message.id) in msg for msg in self.messages
        ):
            return
        self.messages.remove(f"[{message.id}] {message.author.name}: {message.content}")
        self.embed.description = "```yaml\n" + "\n".join(self.messages) + "```"
        await self.bot_message.edit(
            embed=self.embed
        )

    async def message_edited(self, before: Message, after: Message) -> None:
        if not any(
            str(before.id) in msg for msg in self.messages
        ):
            return
        self.messages[self.messages.index(f"[{before.id}] {before.author.name}: {before.content}")] = f"[{after.id}] {after.author.name}: {after.content}"
        self.embed.description = "```yaml\n" + "\n".join(self.messages) + "```"
        await self.bot_message.edit(
            embed=self.embed
        )

    async def specific_channel_message(self, message: Message) -> None:
        if message.channel.id != self.channel.id:
            return
        if message.author.bot and message.author != self.bot.user:
            return
        await self.update_embed(message)   

    async def specific_channel_message_delete(self, message: Message) -> None:
        if message.channel.id != self.channel.id:
            return
        if message.author.bot and message.author != self.bot.user:
            return
        await self.message_deleted(message)

    async def specific_channel_message_edited(self, before: Message, after: Message) -> None:
        if before.channel.id != self.channel.id:
            return
        if before.author.bot and before.author != self.bot.user:
            return
        await self.message_edited(before, after)

    @button(label="Send message", style=ButtonStyle.green)
    async def send_message_button(
        self, button: Button, interaction: MessageInteraction
    ):
        if not self.channel.permissions_for(self.ctx.me).send_messages:
            return await interaction.response.send_message("I do not have permissions to send messages", ephemeral=True)

        await interaction.response.send_message("What would you like to say?", ephemeral=True)
        message: Message = await self.bot.wait_for("message", check=self.check)

        await self.channel.send(message.content)

    @button(label="Delete message", style=ButtonStyle.green)
    async def delete_message_button(
        self, button: Button, interaction: MessageInteraction
    ):
        if not self.channel.permissions_for(self.ctx.me).manage_messages:
            return await interaction.response.send_message("I do not have permissions to delete messages", ephemeral=True)

        await interaction.response.send_message("What message id?", ephemeral=True)
        message: Message = await self.bot.wait_for("message", check=self.check)

        try:
            deleteable = await self.channel.fetch_message(int(message.content))
        except HTTPException:
            return await interaction.send(f"Could not find message with id {message.content}")
            
        await deleteable.delete()
        await message.add_reaction(THUMBS_UP)