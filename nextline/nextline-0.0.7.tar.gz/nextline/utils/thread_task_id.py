import threading
import asyncio
from collections import namedtuple
from itertools import count


##__________________________________________________________________||
class UniqThreadTaskIdComposer:
    """Compose paris of unique thread Id and async task Id"""

    ThreadSpecifics = namedtuple(
        "ThreadSpecifics", ["thread_ident", "task_id_counter", "task_ids"]
    )
    # thread_ident: threading.get_ident()
    # task_id_counter: count().__next__
    # task_ids: set()

    def __init__(self):

        self.non_uniq_id_dict = {}  # non_uniq_id -> uniq_id
        self.uniq_id_dict = {}  # uniq_id -> non_uniq_id
        # uniq_id = (thread_id, task_id)
        # non_uniq_id = (threading.get_ident(), id(asyncio.current_task()))

        self.non_uniq_thread_id_dict = {}  # threading.get_ident() -> thread_id
        self.thread_id_dict = {}  # thread_id -> ThreadSpecifics

        self.thread_id_counter = count().__next__
        self.thread_id_counter()  # consume 0

        self.condition = threading.Condition()

    def compose(self):
        """Return the pair of the current thread ID and async task ID

        Returns
        -------
        tuple
            The pair of the current thread ID and async task ID. If
            not in an async task, the async task ID will be None.
        """

        non_uniq_id = self._compose_non_uniq_id()

        uniq_id = self._find_previsouly_composed_uniq_id(non_uniq_id)
        if uniq_id:
            return uniq_id

        return self._compose_uniq_id(non_uniq_id)

    def exited(self, thread_task_id):
        thread_id, task_id = thread_task_id
        with self.condition:
            non_uniq_thread_id, non_uniq_task_id = self.uniq_id_dict.pop(
                thread_task_id
            )
            self.non_uniq_id_dict.pop((non_uniq_thread_id, non_uniq_task_id))
            self.thread_id_dict[thread_id].task_ids.remove(task_id)
            if not self.thread_id_dict[thread_id].task_ids:
                self.non_uniq_thread_id_dict.pop(non_uniq_thread_id)

    def _compose_non_uniq_id(self):

        non_uniq_thread_id = threading.get_ident()
        # the "thread identifier", which can be recycled after a thread exits
        # https://docs.python.org/3/library/threading.html#threading.get_ident

        non_uniq_task_id = None
        try:
            non_uniq_task_id = id(asyncio.current_task())
            # the id of the task object, which can be also recycled
            # https://docs.python.org/3/library/functions.html#id
        except RuntimeError:
            # no running event loop
            pass

        return non_uniq_thread_id, non_uniq_task_id

    def _find_previsouly_composed_uniq_id(self, non_uniq_id):
        try:
            return self.non_uniq_id_dict[non_uniq_id]
        except KeyError:
            return None

    def _compose_uniq_id(self, non_uniq_id):
        thread_id = self._find_previsouly_composed_thread_id(non_uniq_id)
        if not thread_id:
            thread_id = self._compose_thread_id(non_uniq_id)
        task_id = self._compose_task_id(non_uniq_id)
        uniq_id = (thread_id, task_id)
        with self.condition:
            self.non_uniq_id_dict[non_uniq_id] = uniq_id
            self.uniq_id_dict[uniq_id] = non_uniq_id
        return uniq_id

    def _find_previsouly_composed_thread_id(self, non_uniq_id):
        non_uniq_thread_id = non_uniq_id[0]
        try:
            return self.non_uniq_thread_id_dict[non_uniq_thread_id]
        except KeyError:
            return None

    def _compose_thread_id(self, non_uniq_id):

        non_uniq_thread_id = non_uniq_id[0]
        thread_id = self.thread_id_counter()

        task_id_counter = count().__next__
        task_id_counter()  # consume 0

        thread_specifics = self.ThreadSpecifics(
            thread_ident=non_uniq_thread_id,
            task_id_counter=task_id_counter,
            task_ids=set(),
        )

        with self.condition:
            self.non_uniq_thread_id_dict[non_uniq_thread_id] = thread_id
            self.thread_id_dict[thread_id] = thread_specifics
        return thread_id

    def _compose_task_id(self, non_uniq_id):

        non_uniq_thread_id, non_uniq_task_id = non_uniq_id

        thread_id = self.non_uniq_thread_id_dict[non_uniq_thread_id]

        thread_specifics = self.thread_id_dict[thread_id]

        task_id = None
        if non_uniq_task_id:
            task_id = thread_specifics.task_id_counter()
        thread_specifics.task_ids.add(task_id)

        return task_id


##__________________________________________________________________||
2
