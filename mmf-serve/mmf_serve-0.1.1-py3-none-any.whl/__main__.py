import asyncio
import importlib
import os
import sys
import click
from mmf_meta.core import scan
from .config import config
from .rabbit_wrapper import serve_rabbitmq


@click.group()
def cli():
    sys.path.append(os.getcwd())
    return


@cli.command(name="serve-rabbit")
@click.argument("module")
@click.option("--n_proc", default=1)
@click.option("--queue_name")
@click.option("--results_exchange")
def serve_rabbit(module: str, queue_name: str, results_exchange: str, n_proc):
    """
    Прослушивание задач из очереди
    """
    module = importlib.import_module(module.replace(".py", ""))
    targets, _ = scan()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(
        serve_rabbitmq(
            n_proc=n_proc,
            queue_name=queue_name,
            results_exchange=results_exchange,
            rabbit_params=config.rabbit.dict(),
            targets=targets,
        )
    )
