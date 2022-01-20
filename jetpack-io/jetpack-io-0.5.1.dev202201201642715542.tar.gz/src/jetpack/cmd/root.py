import asyncio
import time
from typing import Final

import click
import grpc

from jetpack import cron
from jetpack._runtime.client import client
from jetpack._task.jetpack_function import JetpackFunction
from jetpack.cmd import util
from jetpack.cmd.cron import cron_group
from jetpack.cmd.params import ENTRYPOINT_PARAMS
from jetpack.config import symbols
from jetpack.config.symbols import Symbol

_using_new_cli = False


def is_using_new_cli() -> bool:
    """
    for legacy uses, we keep old cli. This function disables that logic to ensure
    we don't run the cli command twice.
    """
    return _using_new_cli


@click.group()
def cli() -> None:
    global _using_new_cli
    _using_new_cli = True


@click.command(help="Executes jetpack task")
@click.option("--entrypoint", **ENTRYPOINT_PARAMS)
@click.option("--exec-id", required=True)
@click.option("--qualified-symbol", required=True)
@click.option("--encoded-args", default="")
def exec_task(
    entrypoint: str,
    exec_id: str,
    qualified_symbol: str,
    encoded_args: str,
) -> None:
    util.load_user_entrypoint(entrypoint)
    func = symbols.get_symbol_table()[Symbol(qualified_symbol)]
    asyncio.run(JetpackFunction(func).exec(exec_id, encoded_args))


@click.command(help="Executes cronjob")
@click.option("--entrypoint", **ENTRYPOINT_PARAMS)
@click.option("--qualified-symbol", required=True)
def exec_cronjob(entrypoint: str, qualified_symbol: str) -> None:
    util.load_user_entrypoint(entrypoint)
    func = symbols.get_symbol_table()[Symbol(qualified_symbol)]
    asyncio.run(JetpackFunction(func).exec(post_result=False))


@click.command(help="Registers jetpack functions with runtime")
@click.option("--entrypoint", **ENTRYPOINT_PARAMS)
def register(entrypoint: str) -> None:
    async def _register() -> None:
        util.load_user_entrypoint(entrypoint)
        # For now, we try a few times to register with runtime. Once the runtime
        # becomes a sidecar, we can remove this.
        tries = 3
        for i in range(tries):
            try:
                await client.set_cron_jobs(cron.get_jobs())
            except grpc.RpcError as rpc_error:
                if rpc_error.code() == grpc.StatusCode.UNAVAILABLE:
                    if i == tries - 1:
                        # no more tries, just give up.
                        raise rpc_error
                    print("runtime is not available. Sleep(5) and try again")
                    time.sleep(5)
                else:
                    raise rpc_error

    asyncio.run(_register())


@click.command(help="List jetroutines")
@click.option("--entrypoint", **ENTRYPOINT_PARAMS)
def ls(entrypoint: str) -> None:
    util.load_user_entrypoint(entrypoint)
    print(symbols.get_symbol_table().defined_symbols())


cli.add_command(exec_task)
cli.add_command(exec_cronjob)
cli.add_command(register)
cli.add_command(ls)
cli.add_command(cron_group)
