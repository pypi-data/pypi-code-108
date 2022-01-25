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

from argparse import ArgumentParser

from cognite.extractorutils.cogex.build import build, generate_spec
from cognite.extractorutils.cogex.initialize import initialize_project
from cognite.extractorutils.cogex.io import errorprint


def get_argparser() -> ArgumentParser:
    argparser = ArgumentParser("cogex", description="A project manager for Cognite extractors")
    argparser.set_defaults(command=None)
    subparsers = argparser.add_subparsers(help="Command to run")

    build_parser = subparsers.add_parser(
        "build", help="Build executable", description="Build self-contained executables of Python extractors"
    )
    build_parser.add_argument("--spec", nargs="+", help="Build from spec file(s)", metavar="SPECFILE", default=None)
    build_parser.set_defaults(command="build")

    init_parser = subparsers.add_parser(
        "init", help="Initialize project directory", description="Create a new extractor project in this directory"
    )
    init_parser.set_defaults(command="init")

    spec_parser = subparsers.add_parser(
        "generate-spec",
        help="Generate spec file(s)",
        description="Generate spec file(s) for the project based on the script(s) in pyproject.toml",
    )
    spec_parser.set_defaults(command="spec")

    return argparser


def main() -> None:
    argparser = get_argparser()
    args = argparser.parse_args()

    if args.command == "build":
        build(args)

    elif args.command == "spec":
        generate_spec()

    elif args.command == "init":
        initialize_project()

    else:
        argparser.print_usage()
        errorprint("No command given")


if __name__ == "__main__":
    main()
