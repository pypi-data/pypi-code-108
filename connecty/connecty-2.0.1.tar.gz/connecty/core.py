import discord, types
from .gbl import GB


class MessageLike:
    """
    Children of this class may be passed to Link.send for complete control over the message sent by the webhook
    """
    content: str
    tts: bool
    id: int
    author: types.SimpleNamespace

    # https://i.imgur.com/DTJuzsi.png
    def __init__(self, content, author_name="unset", author_avatar_url="unset", tts: bool = False, id: int = None, channel: discord.TextChannel = None, attachments=None, reference=None):
        """
        Customize your own message. Use this when you aren't simply echoing a message.
        """
        if attachments is None: attachments = []
        self.attachments = attachments
        self.content = content
        self.tts = tts
        self.id = id
        self.channel = channel
        self.reference = reference
        self.author = types.SimpleNamespace(name=author_name, avatar_url=author_avatar_url)

    @classmethod
    def from_message(cls, msg: discord.Message):
        """
        Create a MessageLike from a discord.Message.
        """
        if isinstance(msg, cls): return msg
        else: return cls(
            content=msg.content,
            author_name=msg.author.name,
            author_avatar_url=msg.author.avatar_url,
            tts=msg.tts,
            id=msg.id,
            channel=msg.channel,
            attachments=msg.attachments,
            reference=msg.reference
        )


async def connect(channel, name):
    """
    Returns a webhook object for the given channel and name.
    If the webhook does not exist, it will be created.
    """
    hooks = await channel.webhooks()
    for hook in hooks:
        if hook.name == name:
            return hook
    else:
        return await channel.create_webhook(name=name)

class Link:
    """
    A class that bundles a webhook and a channel. Multiple "links" combine to form a "chain".
    """
    hook: discord.Webhook
    channel: discord.TextChannel

    @classmethod
    async def new(cls, channel: discord.TextChannel):
        """
        Create a new Link object.
        """
        self = cls()
        self.channel = channel
        self.hook = await connect(channel, GB.bot.user.name)
        return self

    async def send(self, msg: discord.Message):
        """
        Send a message to the channel.
        If a discord message is passed, the bot will try to imitate the message and author using a webhook.
        A MessageLike can be passed for finer control.
        """
        if msg.channel == self.channel: return
        files = [await attc.to_file() for attc in msg.attachments]
        await self.hook.send(content=msg.content, avatar_url=str(msg.author.avatar_url), username=msg.author.name, tts=msg.tts, files=files)


class Chain:
    """
    A class that wraps a list of Links. Represent a single connected network of channels, which echo back to each other.
    """

    @classmethod
    async def new(cls, channels):
        """
        Create a new Chain object.
        """
        self = cls()
        self.links = [await Link.new(ch) for ch in channels]
        return self

    async def send(self, message: discord.Message):
        """
        If the message is sent to a link/channel in the chain, it will be sent to all the links in the chain.
        """
        if message.channel in (link.channel for link in self.links):
            for link in self.links:
                await link.send(message)

class Bot(discord.Client):
    """
    Discord bot with extra features.
    """
    startup: callable  # function to run on startup. initial async functions should be put here.

    def __init__(self):
        """
        Initialize the bot.
        """
        super().__init__()
        self.chains = []
        self.init = None
        self.startup = None

    async def on_ready(self):
        """
        Called when the bot is ready.
        """
        print('Logged on as {0}!'.format(GB.bot.user))
        if self.startup: await self.startup()

    async def on_message(self, message: discord.Message):
        """
        Called when a message is received.
        """
        if message.author == self.user or (int(message.author.discriminator) == 0):
            return
        for chain in self.chains:
            msg = MessageLike.from_message(message)
            msg.author.name = message.author.display_name
            await chain.send(msg)

    async def register(self, channels):
        """
        Pass a list of channel IDs.
        A newly created chain (connection) will be added to the bot.
        """
        channels = [GB.bot.get_channel(id) for id in channels]
        chain = await Chain.new(channels)
        self.chains.append(chain)
        return chain
