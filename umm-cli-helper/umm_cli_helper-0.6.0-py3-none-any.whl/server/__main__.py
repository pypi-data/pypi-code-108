from functools import partial

from aiohttp import web

from umm.server.command_set import CommandSet
from umm.server.routes import (
    add_command,
    available_commands,
    confirm_command,
    request_command,
)
from umm.server.utils import setup_folder
from umm.utils.config import parse_config


def setup_routes(app: web.Application, commands: CommandSet):
    app.router.add_get("/commands", partial(available_commands, commands=commands))
    app.router.add_get("/add", partial(add_command, commands=commands))
    app.router.add_get("/umm", partial(request_command, commands=commands))
    app.router.add_get("/confirm", partial(confirm_command, commands=commands))


def main():
    commands = setup_folder()
    config = parse_config()
    app = web.Application()
    setup_routes(app, commands)
    web.run_app(app, port=config.port)


if __name__ == "__main__":
    main()
