import typing as tp
from time import sleep

from ..procedures.procedure import Procedure
from ..procedures.run_function import RunFunction
from ..units.messenger import Messenger
from ..units.task import Task


class MapFunction(Procedure):
    def __init__(self, function, params):
        self.function = function
        self.params = params

    def run(self, messenger: Messenger):
        task_id_to_index: tp.Dict[str, int] = dict()
        res = [...] * len(self.params)
        tasks = []
        for idx, param in enumerate(self.params):
            procedure = RunFunction(self.function, param)
            task = Task(procedure, is_source_blocking=True)
            tasks.append(task)
            task_id_to_index[task.task_id] = idx

        messenger.submit_tasks(tasks)

        while len(task_id_to_index) > 0:
            sleep(0.1)
            task_ids_to_query = list(task_id_to_index.keys())
            results = messenger.query_results(task_ids_to_query)
            for task_id, result in zip(task_ids_to_query, results):
                if result is None:
                    # no such task
                    raise Exception(f"One of the mapped tasks (ID: {task_id}) does not exist. "
                                    f"This should not occur.")
                else:
                    if result.is_successful is True:
                        # task successful
                        res[task_id_to_index.pop(task_id)] = result.data
                    elif result.is_successful is False:
                        # task unsuccessful
                        if isinstance(result.data, Exception):
                            raise result.data
                        else:
                            raise Exception(str(result.data))
        return res
