class Counter:
    """
    A class which counts how many steps are in your verbose function.
    To use, just change the parameter:
    verbose_manager = VerboseManager.instance(counter=True)
    """
    _instance = None

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
            cls._instance._init()
        return cls._instance

    def _init(self):
        # self.starts: the number of start() functions.
        # self.subprocesses: the subprocess nesting level.
        # self.in_process: how many start()s have run since the last finish()
        # self.steps: the number of step() functions.
        self.starts = 0
        self.subprocesses = -1
        self.in_process = 0
        self.steps = 0

    # **ignored avoids errors from it not matching signature of verbose_manager.start()
    def start(self, ignored, **ignored_again):
        """Counts how many subprocesses are in your function."""

        self.subprocesses += 1
        self.in_process += 1
        if self.in_process > self.subprocesses + 1:
            raise RuntimeError(f"Verbose processing on process {self.starts} is missing a finish() function.")
        self.starts += 1

    def finish(self, ignored):
        """Ensures every subprocess finishes."""

        if self.subprocesses == 0:
            results = self._print_results()
            self._init()
            return results
        elif self.subprocesses > 0:
            self.subprocesses -= 1
            self.in_process -= 1
        else:
            raise RuntimeError(f"Verbose processing on process {self.starts + 1} is missing a start() function.")

    def step(self, ignored):
        """Counts how many steps are in the process."""

        self.steps += 1

    def header(self, ignored):
        pass

    def _print_results(self):
        """Prints final results when process finishes."""

        print(f"Your process contains {self.starts - 1} subprocesses, and {self.steps} steps.")
        results_dict = {"subprocesses": self.starts - 1,
                        "steps": self.steps}
        return results_dict
