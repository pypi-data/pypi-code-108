"""
Base class for command-line driven asynchronous worker.

"""
from abc import ABCMeta, abstractmethod, abstractproperty
from argparse import ArgumentParser, Namespace

from inflection import underscore
from microcosm.api import create_object_graph
from microcosm.caching import ProcessCache
from microcosm.loaders import load_each, load_from_dict, load_from_environ

from microcosm_daemon.api import StateMachine
from microcosm_daemon.runner import ProcessRunner, SimpleRunner


class Daemon:
    __metaclass__ = ABCMeta

    def __init__(self):
        self.parser = None
        self.args = None
        self.graph = None

    @abstractproperty
    def name(self):
        """
        Define the name for this process's object graph.

        Must be overridden in a subclass.

        """
        pass

    def __str__(self):
        """
        Define the printable name of this daemon.

        Multiple daemons may share the same code base (and object graph), but each such
        daemon should have different printable name.

        """
        return underscore(self.__class__.__name__)

    @property
    def components(self):
        """
        Define the required object graph components.

        Most subclasses will override to inject additional components.

        """
        return [
            "logger",
            "logging",
            "error_policy",
            "signal_handler",
            "sleep_policy",
        ]

    @property
    def defaults(self):
        return {}

    @property
    def loader(self):
        """
        Define the object graph config loader.

        """
        return load_each(
            load_from_dict(self.defaults),
            load_from_environ,
        )

    @property
    def import_name(self):
        """
        Define the object graph import name, if any.

        """
        return None

    @property
    def root_path(self):
        """
        Define the object graph root path, if any.

        """
        return None

    @property
    def initial_state(self):
        return self

    @abstractmethod
    def __call__(self, graph):
        """
        Define the graph's initial callable state.

        """
        pass

    def run(self):
        """
        Run the daemon.

        """
        parser = self.make_arg_parser()
        args = parser.parse_args()

        if args.processes < 1:
            parser.error("--processes must be positive")
        elif args.processes == 1:
            runner = SimpleRunner(self)
        else:
            runner = ProcessRunner(args.processes, self)

        runner.run()

    def start(self, *args, **kwargs):
        """
        Start the state machine.

        """
        self.initialize()
        self.graph.logger.info("Starting daemon {}".format(self.name))

        try:
            self.run_state_machine()
            exit(0)
        except Exception as exc:
            try:
                self.graph.logger.error(
                    f"Unexpected error, exiting with non-zero error code: {exc}",
                )
            finally:
                exit(1)

    def initialize(self):
        # reprocess the arguments because some aspects of argparse are not pickleable
        # and will fail under multiprocessing
        self.parser = self.make_arg_parser()
        self.args = self.parser.parse_args()
        self.graph = self.create_object_graph(self.args)

    def run_state_machine(self):
        state_machine = StateMachine(self.graph, self.initial_state)
        state_machine.run()

    def make_arg_parser(self):
        """
        Create the argument parser.

        """
        parser = ArgumentParser()

        flags = parser.add_mutually_exclusive_group()
        flags.add_argument("--debug", action="store_true")
        flags.add_argument("--testing", action="store_true")

        parser.add_argument("--processes", type=int, default=1)
        return parser

    def create_object_graph(self, args, cache=None, loader=None):
        """
        Create (and lock) the object graph.

        """
        graph = create_object_graph(
            name=self.name,
            debug=args.debug,
            testing=args.testing,
            import_name=self.import_name,
            root_path=self.root_path,
            cache=cache,
            loader=load_each(loader, self.loader) if loader else self.loader,
        )
        self.create_object_graph_components(graph)
        graph.lock()
        return graph

    def create_object_graph_components(self, graph):
        graph.use(*self.components)

    @classmethod
    def create_for_testing(cls, loader=None, cache=None, **kwargs):
        """
        Initialize the daemon for unit testing.

        The daemon's graph will be populated but it will not be started.

        """
        if cache is None:
            scope = cls.__name__
            cache = ProcessCache(scope=scope)

        daemon = cls()
        daemon.args = Namespace(debug=False, testing=True, **kwargs)
        daemon.graph = daemon.create_object_graph(daemon.args, cache=cache, loader=loader)
        return daemon
