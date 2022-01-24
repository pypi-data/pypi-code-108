import json
from functools import partial

import requests
from aiohttp import web

from umm.server.command import Command
from umm.server.command_set import CommandSet


async def available_commands(request: requests.request, commands: CommandSet):
    """
    Args:
        request: http request
    Returns:
        response json of all commands
    """
    resp_json = commands.command_dict
    return web.json_response(
        resp_json, dumps=partial(json.dumps, default=vars, indent=2)
    )


async def request_command(request: requests.request, commands: CommandSet):
    """
    Args:
        request: http request
    Returns:
        response json of queried commands
    """
    tags = list(request.query.keys())
    resp_json = {"commands": commands.get_candidates(tags)}
    return web.json_response(
        resp_json, dumps=partial(json.dumps, default=vars, indent=2)
    )


async def add_command(request: requests.request, commands: CommandSet):
    """
    Args:
        request: http request with data for command to add
    Returns:
        response json to confirm added command
    """
    command = Command(
        command=request.query.getone("command"), tags=request.query.getall("tags")
    )
    commands.add(command)
    commands.write_down()
    resp_json = {"recieved": True}
    return web.json_response(resp_json, dumps=partial(json.dumps, indent=2))


async def confirm_command(request: requests.request, commands: CommandSet):
    """
    Args:
        request: http request with confirmed id
    Returns:
        response json to confirm added command
    """
    id = request.query.get("id", None)
    if id:
        commands.increment_freq(id)
        commands.write_down()
    resp_json = {"recieved": True}
    return web.json_response(resp_json, dumps=partial(json.dumps, indent=2))
