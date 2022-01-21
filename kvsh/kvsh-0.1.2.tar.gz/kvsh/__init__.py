from __future__ import annotations

import argparse
import logging
from collections import UserDict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import re
import shlex
from typing import Dict, Optional, Sequence

import argcomplete
import xdg
from dataclasses_json import DataClassJsonMixin, config
from logging_actions import log_level_action

logger = logging.getLogger(__name__)


@dataclass
class Value:
    value: str
    created: datetime = field(
        default_factory=datetime.now,
        metadata=config(encoder=datetime.isoformat, decoder=datetime.fromisoformat),
    )
    comment: Optional[str] = None


@dataclass
class Database(DataClassJsonMixin):
    mapping: Dict[str, Value]

    @classmethod
    def load_or_default(cls, file_path: Path) -> Database:
        try:
            db = cls.from_json(file_path.read_text())
        except Exception as e:
            logger.error(
                f"Unable to load from {file_path} ({e}), ignoring and using a new kv store",
            )
            db = Database(mapping={})
        return db


class LenientChoices(UserDict):
    def __contains__(self, key: object) -> bool:
        """Return True so that argparse will validate any key as a choice"""
        return True


def kv(
    kv_file: Path = xdg.xdg_data_home().joinpath("kv.json"),
    args: Optional[Sequence[str]] = None,
):
    logger.addHandler(logging.StreamHandler())
    logger.debug(f"{kv_file=}")

    db = Database.load_or_default(kv_file)

    parser = argparse.ArgumentParser(
        description="A persistent key-value store for the shell"
    )
    parser.add_argument("--log-level", action=log_level_action(logger), default="info")

    parser.add_argument("key", choices=LenientChoices(db.mapping), metavar="key")
    parser.add_argument("value", nargs="?")

    argcomplete.autocomplete(parser)
    args = parser.parse_args(args=args)

    logger.debug(f"{args=}")

    if args.value is None:
        print(db.mapping[args.key].value)
    else:
        db.mapping[args.key] = Value(value=args.value)
        kv_file.parent.mkdir(parents=True, exist_ok=True)
        kv_file.write_text(db.to_json())


def is_valid_env_var_name(s: str) -> bool:
    return re.match(pattern=r"^[a-zA-Z_]+[a-zA-Z0-9_]*$", string=s) is not None


def kvv(
    kv_file: Path = xdg.xdg_data_home().joinpath("kv.json"),
    args: Optional[Sequence[str]] = None,
):
    logger.addHandler(logging.StreamHandler())
    logger.debug(f"{kv_file=}")

    db = Database.load_or_default(kv_file)

    parser = argparse.ArgumentParser(
        description="A persistent key-value store for the shell - verbose functionality"
    )
    parser.add_argument("--log-level", action=log_level_action(logger), default="info")
    subparsers = parser.add_subparsers(required=True, dest="subcommand")

    get = subparsers.add_parser("get")
    get.add_argument("key", choices=db.mapping)

    set = subparsers.add_parser("set")
    set.add_argument("key", choices=LenientChoices(db.mapping), metavar="key")
    set.add_argument("value")
    set.add_argument("comment", nargs="?")

    remove = subparsers.add_parser("remove", aliases=["rm"])
    remove.add_argument("key", choices=db.mapping, nargs="+")

    clear = subparsers.add_parser("clear")

    env = subparsers.add_parser("env")

    argcomplete.autocomplete(parser)
    args = parser.parse_args(args=args)

    logger.debug(f"{args=}")

    if args.subcommand == "get":
        print(db.mapping[args.key].value)
    elif args.subcommand == "set":
        db.mapping[args.key] = Value(value=args.value, comment=args.comment)
        kv_file.write_text(db.to_json())
    elif args.subcommand == "remove" or args.subcommand == "rm":
        for key in args.key:
            db.mapping.pop(key)
        kv_file.write_text(db.to_json())
    elif args.subcommand == "clear":
        kv_file.write_text(Database(mapping={}).to_json())
    elif args.subcommand == "env":
        for key, value in db.mapping.items():
            if is_valid_env_var_name(key):
                print(f"{key}={shlex.quote(value.value)}")
            else:
                logger.info(f"Skipping invalid key {key}")
