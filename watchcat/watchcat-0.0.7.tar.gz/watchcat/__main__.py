import sys

import termcolor

from watchcat import cli
from watchcat.config.config import ConfigLoader
from watchcat.diff_detector.simple import SimpleDiffDetector
from watchcat.storage.sql_storage import SqlStorage


def main():
    parser = cli.build_parser()
    args = parser.parse_args()

    config = ConfigLoader(args.config)
    diff_detector = SimpleDiffDetector()

    update = []
    no_update = []
    first_fetch = []

    with SqlStorage(args.db) as storage:
        for resource_id, resource in config.resources.items():
            try:
                new_snapshot = resource.get()
                old_snapshot = storage.get(resource_id)
                storage.set(new_snapshot)
                if old_snapshot is not None:
                    if diff_detector.has_update(old_snapshot, new_snapshot):
                        resource.notifier.send(
                            f"{resource.title} has updated!",
                            resource.description(),
                            diff_detector.diff(old_snapshot, new_snapshot),
                        )
                        update.append(resource_id)
                    else:
                        no_update.append(resource_id)
                else:
                    first_fetch.append(resource_id)
            except Exception as e:
                print(e, file=sys.stderr)

    if update:
        termcolor.cprint("[update found]", file=sys.stderr, color="green")
        for i in update:
            print(f"  - {i}", file=sys.stderr)
    if no_update:
        termcolor.cprint("[no update found]", file=sys.stderr)
        for i in no_update:
            print(f"  - {i}", file=sys.stderr)
    if first_fetch:
        termcolor.cprint("[first fetch found]", file=sys.stderr, color="yellow")
        for i in first_fetch:
            print(f"  - {i}", file=sys.stderr)
