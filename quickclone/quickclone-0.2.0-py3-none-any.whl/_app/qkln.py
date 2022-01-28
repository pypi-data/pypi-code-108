import argparse
from pathlib import Path
import typing as t
import subprocess
import sys

from quickclone import DESCRIPTION, NAME, VERSION
from quickclone.config.common import DEFAULTS_FOLDER
from quickclone.config.configurator import load_user_config
from quickclone.delegation.vcs.common import Command
from quickclone.delegation.vcs.git import GitCloneCommand
from quickclone.local import local_dest_path
from quickclone.remote import DirtyLocator, UniformResourceLocator, UrlAuthority, remote_to_string


def program():
    sys.exit(main(sys.argv))


def create_argument_parser() -> argparse.ArgumentParser:
    app = argparse.ArgumentParser(description=f"{NAME} v{VERSION}: {DESCRIPTION}")
    app.add_argument(
        "--version",
        "-v",
        dest="show_version",
        help="display the version number and exit",
        action="store_const",
        const=True,
        default=False
    )
    app.add_argument(
        "remote_url",
        metavar="REMOTE_URL",
        nargs="?",
        type=str,
        default="",
        help="the url of the remote to be cloned"
    )
    app.add_argument(
        "dest_path",
        metavar="DEST_PATH",
        nargs="?",
        type=str,
        default="",
        help="the directory where the remote repository should be cloned to"
    )
    app.add_argument(
        "--pretend",
        "-P",
        dest="pretend",
        action="store_const",
        const=True,
        default=False,
        help=(
            "if this flag is found, QuickClone will not perform any important "
            "actions that it would have if this flag is not found"
        )
    )
    app.add_argument(
        "--config-file",
        "-C",
        dest="config_file",
        metavar="CONFIG_FILE_PATH",
        help="override the default config file location"
    )
    app.add_argument(
        "--ignore",
        "-I",
        dest="ignore",
        metavar="CONFIG_KEY",
        action="append",
        required=False,
        default=[],
        help=(
            "what part of the config file to ignore. "
            "you can use dot-separated keys (like 'options.local.remotes_dir') or "
            "their short forms to specify which config values to ignore"
        )
    )
    app.add_argument(
        "--test",
        "-T",
        dest="tests",
        metavar="TEST",
        action="append",
        required=False,
        default=[],
        help=(
            "which tests to conduct: "
            "parse_authority, parse_full_url, parse_dirty_url, print_defaults_folder, config_file"
        )
    )
    return app


def ignore_config(keys: t.List[str]) -> t.Set[str]:
    SHORT_FORMS = {
        "d": "options.local.remotes_dir",
        "s": "options.remote.force_scp"
    }
    ignored = set(keys)
    for short, long in SHORT_FORMS.items():
        if short in keys:
            ignored.add(long)
    return ignored


def main(argv: t.List[str]) -> int:
    app = create_argument_parser()
    args = app.parse_args(argv[1:])
    if args.show_version:
        print(f"{NAME} v{VERSION}")
        return 0
    if len(args.tests) > 0:
        successes, test_count = conduct_tests(args.tests, args.remote_url)
        if successes < test_count:
            print("Not all tests succeeded")
            return 1
        else:
            return 0
    else:
        return normal(args)


# Call this function if quickclone is run with the normal set of clargs.
def normal(args: argparse.Namespace) -> int:
    dirty = DirtyLocator.process_dirty_url(args.remote_url)
    ignored = ignore_config(args.ignore)
    try:
        configs = load_user_config(None if args.config_file is None else Path(args.config_file))
        builder = configs.to_locator_builder()
        built_url = UniformResourceLocator.from_user_and_defaults(dirty, builder)
        built_url.kwargs["explicit_scp"] = (
            (
                configs.from_dotted_string("options.remote.force_scp")
                and not "options.remote.force_scp" in ignored
            ) or
            built_url.kwargs.get("explicit_scp")
        )
        final_url = remote_to_string(built_url, "git")
        print(f"Final URL: {str(final_url)}")
        dest_path = local_dest_path(
            args.dest_path,
            configs.from_dotted_string("options.local.remotes_dir"),
            built_url.get_host(),
            built_url.get_path(),
            "options.local.remotes_dir" in ignored
        )
        print(f"Destination path: {dest_path}")
        git_clone_command = GitCloneCommand(final_url, dest_path)
        print(f"Command> {git_clone_command.format_command_str()}")
        if args.pretend:
            print("pretend flag found! Not executing command.")
        else:
            run_command(git_clone_command)
    except Exception as e:
        raise e
        print(f"Error occurred:\n{e}")
        return 1
    else:
        return 0


def run_command(command: Command) -> subprocess.CompletedProcess:
    result = command.run()
    if isinstance(result, subprocess.CompletedProcess):
        return result
    elif isinstance(result, subprocess.SubprocessError):
        raise result


def conduct_tests(tests: t.List[str], remote_url: str) -> t.Tuple[int, int]:
    success_counts: int = 0
    for test in tests:
        try:
            if test == "parse_authority":
                authority = UrlAuthority.process_authority(remote_url)
                print(authority)
                success_counts += 1
            elif test == "parse_full_url":
                url = UniformResourceLocator.process_url(remote_url)
                print(url)
                success_counts += 1
            elif test == "parse_dirty_url":
                dirty_url = DirtyLocator.process_dirty_url(remote_url)
                print(dirty_url)
                success_counts += 1
            elif test == "print_defaults_folder":
                print(DEFAULTS_FOLDER)
                success_counts += 1
            elif test == "config_file":
                success_counts += int(test_config_file())
            else:
                print(f"Unrecognised test: {test}")
        except:
            pass
    return success_counts, len(tests)


def test_config_file() -> bool:
    try:
        config = load_user_config()
        print(config)
        for key in ["options.remote.scheme"]:
            print(f"{key}: {config.from_dotted_string(key)}")
    except Exception as e:
        print(e)
        return False
    else:
        return True


if __name__ == "__main__":
    program()
