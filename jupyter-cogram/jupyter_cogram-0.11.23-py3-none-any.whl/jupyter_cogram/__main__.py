import argparse
import os
import sys
import urllib.parse
from pathlib import Path
from typing import Text, Optional

import requests

config_location = Path().home() / ".ipython/nbextensions/jupyter-cogram"
token_file_name = "cogram_auth_token"
log_file_name = "cogram_access_log"
backend_url = os.environ.get("BACKEND_URL", "https://api.cogram.com")


def _print(t: Text, pre: Optional[Text] = None, post: Optional[Text] = None) -> None:
    """Print text to the console with a prefix and a suffix which may contain unicode
    characters. On windows, these unicode characters aren't printed.

    Args:
        t: Text to print to the console.
        pre: Prefix which may contain unicode.
        post: Suffix which may contain unicode.
    """
    if not sys.platform == "win32":
        t = f"{pre or ''}{t}{post or ''}"

    print(t)


def install_token() -> None:
    """Install the global token stored in `token` into `config_location`."""
    loc = config_location.absolute()

    if not loc.is_dir():
        loc.mkdir(parents=True)

    p = loc / token_file_name

    p.write_text(token)

    _print(f"Successfully stored API token at '{p}'", post=" 🎉")


def add_log_file() -> None:
    """Touch a log file in the user directory."""
    p = config_location.absolute() / log_file_name
    if not p.is_file():
        p.touch()


def set_installed_flag() -> None:
    """Instruct the backend server to set the `installed` flag."""
    url = urllib.parse.urljoin(backend_url, "setInstalled")

    # noinspection PyBroadException
    try:
        requests.post(url, json={"auth_token": token}, timeout=10)
    except Exception:
        pass


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Set your Cogram API token")
    parser.add_argument(
        "-t",
        "--token",
        help="Your Cogram API token",
        required=True,
    )

    token: Optional[Text] = parser.parse_args().token

    if not token:
        _print(
            "Could not find token! The full command is\n"
            "python3 -m jupyter_cogram --token YOUR_TOKEN",
            pre="⚠️  ",
        )

        sys.exit(1)

    # noinspection PyBroadException
    try:
        install_token()
        set_installed_flag()
        add_log_file()
    except Exception as e:
        _print(f"Could not install token. Error:\n{e}", pre="⚠️  ")
