from discord_api_types import Client
import asyncio
from .gateway import DiscordGateway
from .command import Command, ApiCommand
from .clientuser import ClientUser
from .channels import TextChannel
from typing import Optional, List
from .guild import Guild
from .fast import setup_fast

class Client(Client):
    def __init__(self, loop:asyncio.AbstractEventLoop = None, log:bool = True) -> None:
        """
        This can setup a discordbot.

        Parameters
        ----------
        loop : asyncio.AbstractEventLoop
            Put a event loop.
        log : bool default True
            If you don't want show a log, please do False
            
        Attributes
        ----------
        loop : asyncio.AbstractEventLoop
            event loop.
        user : ClientUser
            get a bot information

        Examples
        --------
        ```python
        from discord_api import Client
        client = Client()
        ```
        """
        setup_fast(self)
        super().__init__(loop, log = log)

    def dispatch(self, eventname, *args, **kwargs):
        name = "on_" + eventname
        if hasattr(self, name):
            coro = getattr(self, name)
            try:
                self.loop.create_task(coro(*args, **kwargs))
            except:
                pass

    def print(self, name, content):
        """
        This is print a like sanic log
        
        Examples
        --------
        ```python
        client.print("test", "this is test")
        ```
        """
        super().print(name, content)

    async def connect(self, token) -> None:
        """
        This can connect to discord gateway.
        But if you want to use this, you need to use `await client.login()`
        """
        await super().connect(token)

    async def login(self) -> None:
        """
        This can login to discord api.
        """
        user = await super().login()
        self.user = ClientUser.from_dict(user.user)

    async def start(self, token) -> None:
        """
        This can run a discord client.
        """
        self.print("START", "Now starting...")
        self.http._token(token)
        await self.login()
        await self.setup_command()
        await self.connect(token)
    
    def run(self, token) -> None:
        """
        This can run a discord client.

        Examples
        --------
        ```python
        client = Client()
        client.run("ToKeN")
        ```
        """
        self.loop.run_until_complete(self.start(token))

    def event(self, coro):
        """
        This is send gateway event.

        Examples
        --------
        ```python
        client = Client()
        
        @client.event
        async def on_ready():
            print("ready")

        client.run("ToKeN")
        ```
        """
        setattr(self, coro.__name__, coro)
        return coro

    def get_guild(self, _id:int) -> Optional[Guild]:
        """This can search guild from client.guilds
        
        Returns
        -------
        Optional[Guild] : guild or None
        
        Examples
        --------
        ```python
        guild = client.get_guild(8819371883819)
        ```
        """
        guild = None
        for guild in self.guilds:
            if _id == guild.id:
                break
        return guild

    async def fetch_commands(self) -> List[ApiCommand]:
        """
        This can fetch discord application commands from discord api.
        
        Returns
        -------
        List[Command] : list of command.
        """
        datas = await self.http.fetch_commands()
        return [ApiCommand.from_dict(self, data) for data in datas]

    def get_channel(self, _id:int) -> Optional[TextChannel]:
        """This can search text_channel from guild.text_channels.
        
        Examples
        --------
        ```python
        channel = client.get_channel(0189193918939)
        print(channel.name)
        ```
        """
        channel = None
        for guild in self.guilds:
            for channel in guild.text_channels:
                if _id == channel.id:
                    break
        return channel
    
    def _check_command(self, command, api):
        if command.description != api.description:
            return True
        else:
            return False

    async def setup_command(self) -> None:
        """
        set up a application command.
        """
        apis = await self.fetch_commands()
        cmds = []
        for command in self.__commands:
            cmds.append(command.name)
            update = False
            for api in apis:
                if api.name in cmds:
                    if api.name == command.name:
                        break
                else:
                    await api.delete()
            else:
                update = True
            if update:
                data = await self.http.add_command(command)

    def add_command(self, command:Command) -> None:
        """
        This can add discord application commannd.

        Examples
        --------
        ```python
        from discord_api import Client, Command

        client = Client()
        client.add_command(Command(name = "ping", description = "pong"))
        
        client.run("ToKeN")
        ```
        """
        self.__commands.append(command)
