from itertools import count

from .pdb.proxy import PdbProxy
from .registry import PdbCIRegistry
from .utils import UniqThreadTaskIdComposer


##__________________________________________________________________||
class Trace:
    """The main trace function

    An instance of this class, which is callable, should be set as the
    trace function by sys.settrace() and threading.settrace().

    Parameters
    ----------
    registry : object
        An instance of Registry
    modules_to_trace : set
        The names of modules to trace
    """

    def __init__(self, registry, modules_to_trace):

        self.registry = registry
        self.pdb_ci_registry = PdbCIRegistry()

        self.prompting_counter = count().__next__
        self.prompting_counter()  # consume 0

        self.pdb_proxies = {}

        self.modules_to_trace = set(modules_to_trace)
        # Make a copy so that the original won't be modified.
        # self.modules_to_trace will be shared and modified by
        # multiple instances of PdbProxy.

        self.id_composer = UniqThreadTaskIdComposer()

    def __call__(self, frame, event, arg):
        """Called by the Python interpreter when a new local scope is entered.

        https://docs.python.org/3/library/sys.html#sys.settrace

        """

        thread_asynctask_id = self.id_composer.compose()
        # print(*thread_asynctask_id)

        pdb_proxy = self.pdb_proxies.get(thread_asynctask_id)
        if not pdb_proxy:
            pdb_proxy = PdbProxy(
                trace=self,
                thread_asynctask_id=thread_asynctask_id,
                modules_to_trace=self.modules_to_trace,
                registry=self.registry,
                ci_registry=self.pdb_ci_registry,
                prompting_counter=self.prompting_counter,
            )
            self.pdb_proxies[thread_asynctask_id] = pdb_proxy

        return pdb_proxy.trace_func(frame, event, arg)

    def returning(self, thread_asynctask_id):
        self.id_composer.exited(thread_asynctask_id)
        del self.pdb_proxies[thread_asynctask_id]


##__________________________________________________________________||
