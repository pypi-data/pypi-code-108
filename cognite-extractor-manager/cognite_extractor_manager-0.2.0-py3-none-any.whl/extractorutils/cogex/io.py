#  Copyright 2020 Cognite AS
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
from typing import List, Optional

import termcolor

try:
    import readline  # noqa
except ModuleNotFoundError:
    pass


def prompt(name: str, default: Optional[str] = None) -> str:
    prompt_default = f" [default: {default}]" if default else ""

    while True:
        answer = input(f"Enter {name}{prompt_default}: ")

        if not answer:
            if default:
                return default
        else:
            return answer


def choice(name: str, choices: List[str], default: Optional[str] = None) -> str:
    while True:
        answer = prompt(f"{name} ({'/'.join(choices)})", default)
        if answer in choices:
            return answer


def headerprint(s: str) -> None:
    termcolor.cprint(s, "green", attrs=["bold"])


def errorprint(s: str) -> None:
    print(f"{termcolor.colored('Error:', 'red', attrs=['bold'])} {termcolor.colored(s, 'red')}")


def lineprint(color: str = "cyan") -> None:
    print()
    termcolor.cprint("-" * 79, color)
    print()


def get_git_user() -> Optional[str]:
    name = os.popen("git config --get user.name").read().strip()
    email = os.popen("git config --get user.email").read().strip()

    if name and email:
        return f"{name} <{email}>"
    return None
