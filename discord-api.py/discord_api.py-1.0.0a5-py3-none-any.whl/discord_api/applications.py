from .command import Command, ApiCommand

class Application:
    def __init__(self, client):
        self.client = client
        self.http = client.http
        self.__commands = []
        
    async def fetch_commands(self) -> List[ApiCommand]:
        """
        This can fetch discord application commands from discord api.
        
        Returns
        -------
        List[Command] : list of command.
        """
        datas = await self.http.fetch_commands()
        return [ApiCommand.from_dict(self, data) for data in datas]
    
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
