import logging
import os
import sys

from unipipeline.args import CMD_INIT, CMD_CHECK, CMD_CRON, CMD_PRODUCE, CMD_CONSUME, parse_args, CMD_SCAFFOLD
from unipipeline.modules.uni import Uni


def run_check(u: Uni, args) -> None:  # type: ignore
    u.check()


def run_scaffold(u: Uni, args) -> None:  # type: ignore
    u.scaffold()


def run_cron(u: Uni, args) -> None:  # type: ignore
    u.init_cron()
    u.initialize()
    u.start_cron()


def run_init(u: Uni, args) -> None:  # type: ignore
    for wn in args.init_workers:
        u.init_producer_worker(wn)
    u.initialize(everything=len(args.init_workers) == 0)


def run_consume(u: Uni, args) -> None:  # type: ignore
    for wn in args.consume_workers:
        u.init_consumer_worker(wn)
    u.initialize()
    u.start_consuming()


def run_produce(u: Uni, args) -> None:  # type: ignore
    u.init_producer_worker(args.produce_worker)
    u.initialize()
    u.send_to(args.produce_worker, args.produce_data, alone=args.produce_alone)


args_cmd_map = {
    CMD_INIT: run_init,
    CMD_CHECK: run_check,
    CMD_SCAFFOLD: run_scaffold,
    CMD_CRON: run_cron,
    CMD_PRODUCE: run_produce,
    CMD_CONSUME: run_consume,
}


def main() -> None:
    sys.path.insert(0, os.getcwdb().decode('utf-8'))
    args = parse_args()
    u = Uni(args.config_file, echo_level=logging.DEBUG if args.verbose else None)
    args_cmd_map[args.cmd](u, args)
    u.echo.success('done')
