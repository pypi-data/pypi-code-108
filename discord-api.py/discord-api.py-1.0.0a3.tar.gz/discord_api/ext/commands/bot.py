from ...client import Client
from ...command import CommandOption, Command, CommandTypeChat_Input
from .option import Option
from ...interaction import InteractionTypeCommand
from .errors import Application_Command_NotFound, ExtensionError
from .cogs import Cog
from inspect import signature, getmembers, isclass
import importlib
from typing import Dict

class Bot(Client):
    def __init__(self):
        super().__init__()
        self._commands = {}
        self.__cogs = {}
        self._events = {}

    def add_listener(self, coro, name):
        """This can add listener
        
        Examples
        --------
        ```python
        async def coro():
            print("ready")
        bot.add_listener(coro, "on_ready")
        ```
        """
        if name in self._events:
            self._events[name].append(coro)
        else:
            self._events[name] = [coro]

    def dispatch(self, name, *args, **kwargs):
        super().dispatch(name, *args, **kwargs)
        name = "on_" + name
        if name in self._events:
            for coro in self._events[name]:
                self.loop.create_task(coro())

    async def on_interaction(self, interaction):
        try:
            await self.process_command(interaction)
        except Exception as error:
            self.dispatch("application_command_error", interaction, error)

    async def process_command(self, interaction):
        """Use interaction to execute application commands.
        
        Examples
        --------
        ```python
        @bot.event
        async def on_interaction(interaction):
            await bot.process_command(interaction)
        ```
        """
        data = interaction.data
        if isinstance(interaction.type, InteractionTypeCommand):
            if data["name"] in self._commands:
                kwargs = {}
                if data.get("options") is not None:
                    for option in data.get("options"):
                        kwargs[option["name"]] = option["value"]
                await self._commands[data["name"]](interaction, **kwargs)
            else:
                raise Application_Command_NotFound("The application command is not registered.")

    def load_extension(self, name):
        """This is for reading cogs.
        
        Paramaters
        ----------
        name : str
          cog file name
        """
        lib = importlib.import_module(name)
        for name, cls in getmembers(lib):
            if isclass(cls):
                if issubclass(cls, Cog):
                    self.add_cog(cls(self))

    def add_cog(self, _class):
        cls = _class.setup(self)
        self.__cogs[cls.__class__.__name__] = cls

    def add_command(self, name, coro):
        """This can setup application.
        
        Paramater
        ---------
        name : str
          application command name
        coro : corotine
          function
        """
        options = []
        values = signature(coro).parameters.values()
        self._commands[name] = coro
        for p in values:
            option_name = p.name
            if option_name in ["self", "ctx"]:
                continue
            option = p.annotation
            if p.default is None:
                option_required = False
            elif p.default is p.empty:
                option_required = True
            if not isinstance(option, Option):
                options.append(CommandOption(name = option_name, required = option_required))
            else:
                options.append(CommandOption(name = option_name, description = option.description, type = option.type, required = option_required))
        super().add_command(Command(name = name, description = coro.kwargs.pop("description", "..."), type = coro.kwargs.pop("type", CommandTypeChat_Input), options = options))
    
    def application_command(self, name, **kwargs):
        """This can setup application command easy.
        If you want add option.
        please use `discord_api.ext.command.Option`.
     
        Examples
        --------
        ```python
        @bot.application_command("ping")
        async def ping(ctx):
            await ctx.send("Pong")
        ```
        """
        def deco(coro):
            coro.kwargs = kwargs
            self.add_command(name, coro)
            return coro
        return deco

    def slash(self, name, **kwargs):
        """Consult unread newest application
        
        ```python
        @bot.slash("ping")
        async def ping(ctx):
            await ctx.send("ping")
        ```
        """
        return self.application_command(name, type = CommandTypeChat_Input, **kwargs)

    def run(self, token):
        super().run(token)
