from miroflowexport.internal.task import Task
from miroflowexport.internal import transform

def create_tasks(log, cards):
    tasks_by_id = {}
    for card_entry in cards:
        task = transform.convert_json_entry_to_task_entry(log, card_entry)
        tasks_by_id[task.id()] = task

    return tasks_by_id

def add_task_dependencies(log, dependency_tuples):
    for (source, sink) in dependency_tuples:
        source._post += [sink]
        sink._pre += [source]
