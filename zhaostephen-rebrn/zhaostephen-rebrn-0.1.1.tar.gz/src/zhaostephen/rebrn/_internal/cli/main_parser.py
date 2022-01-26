import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from zhaostephen.rebrn import __version__ as VERSION
from zhaostephen.rebrn._internal.exceptions import CliInvalidArgumentError


@dataclass
class CliMainArgs:
    in_dir_path: Path
    search_pattern: str
    replacement_pattern: str


def __create_invalid_arguments_msg(
    argparser: argparse.ArgumentParser,
    argument_dict: Dict[str, str],
    details: Optional[str],
) -> str:
    msg = []

    if len(argument_dict) == 0:
        pass
    elif len(argument_dict) == 1:
        for arg_name, arg_val in argument_dict.items():
            msg.append(f"Invalid argument: {arg_name} = {arg_val}")
    else:
        msg.append("Invalid arguments:")
        for arg_name, arg_val in argument_dict.items():
            msg.append(f"    {arg_name} = {arg_val}")

    if len(argument_dict) > 0:
        msg.append("")

    if details is not None:
        msg.append(details)
        msg.append("")

    msg.append(argparser.format_usage())

    return "\n".join(msg)


def __create_argparser(program_name: str) -> argparse.ArgumentParser:
    argparser = argparse.ArgumentParser(
        prog=program_name,
        description="Renames files by substituting a search pattern with a replacement pattern, with datetime formatting and regex support.",
    )
    argparser.add_argument(
        "in_dir", help="The input directory containing the files to be renamed."
    )
    argparser.add_argument(
        "search_pattern",
        help="The dfregex expression used to filter filenames and to extract substrings from filenames.",
    )
    argparser.add_argument(
        "replacement_pattern",
        help="The replacement pattern to generate new file names, using backslash references for sed-style processing.",
    )
    argparser.add_argument(
        "-v", "--version", action="version", version="%(prog)s v" + str(VERSION)
    )
    return argparser


def parse_args(program_name: str, args: List[str]) -> CliMainArgs:
    argparser = __create_argparser(program_name)
    parsed_args = argparser.parse_args(args)

    # Validate directory
    in_dir_path = Path(parsed_args.in_dir)
    if in_dir_path.is_file():
        raise CliInvalidArgumentError(
            __create_invalid_arguments_msg(
                argparser,
                {"in_dir": parsed_args.in_dir},
                "Input directory cannot be a file.",
            )
        )
    if not in_dir_path.is_dir():
        raise CliInvalidArgumentError(
            __create_invalid_arguments_msg(
                argparser,
                {"in_dir": parsed_args.in_dir},
                "Input directory is not a valid directory.",
            )
        )

    return CliMainArgs(
        in_dir_path=in_dir_path,
        search_pattern=parsed_args.search_pattern,
        replacement_pattern=parsed_args.replacement_pattern,
    )
