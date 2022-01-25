import os

class BaseJudge:
    def __init__(self, base_dir, tests, args):
        self.base_dir = base_dir

        self.exercises = tests.get("exercises", [])

        self.volumes = args.volume
        self.volumes.extend(tests.get("volumes", []))

        self.verbose = args.verbose


