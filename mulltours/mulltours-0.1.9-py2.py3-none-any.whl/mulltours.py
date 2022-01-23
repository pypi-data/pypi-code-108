import argparse
import logging
import os
import pathlib
import sys

import cookiecutter.main
from clinepunk import clinepunk

from mulltours import git


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "basedir",
        nargs="?",
        default=".",
        help="create project_name in basedir so it results in basedir/project_name",
    )
    parser.add_argument(
        "--project",
        nargs="?",
        default=None,
        help="choose specific name instead of random",
    )

    args = parser.parse_args()

    name = "".join(clinepunk.get_words(count=2)) if not args.project else args.project
    path = pathlib.Path(args.basedir) / name

    url = "https://github.com/audreyr/cookiecutter-pypackage.git"
    logging.debug(f"creating project {name} from template {url}")
    os.chdir(args.basedir)
    cookiecutter.main.cookiecutter(
        url,
        extra_context={"project_name": name},
        no_input=True,
    )

    # commit boilerplate
    git.main(path)
    print(path.resolve())


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="{%(filename)s:%(lineno)d} %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(f"{pathlib.Path(__file__).stem}.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    main()
