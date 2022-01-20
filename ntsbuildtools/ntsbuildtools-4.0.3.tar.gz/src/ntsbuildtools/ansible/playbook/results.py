import json
import datetime
from typing import Collection
from dataclasses import dataclass

import ntsbuildtools.ansible.return_values.default
import ntsbuildtools.ansible.return_values.factory as return_values_factory
from ntsbuildtools.markdown.comments import MarkdownComment

@dataclass
class TaskResult:
    """Stores the results from an Ansible Task that executed against a specific Ansible host/target.
    """
    failed: bool
    host_name: str
    task_name: str
    ansible_module: str
    start_time: datetime.datetime
    end_time: datetime.datetime
    return_values: ntsbuildtools.ansible.return_values.default.ReturnValues

    def as_markdown(self):
        markdown = MarkdownComment()
        if self.failed:
            markdown.add_heading(3, f'[TASK] {self.task_name}')
            markdown.add_heading(4, f'{self.host_name} ***(ERROR)***')
            markdown.add_message(self.return_values.pretty_error())
        else:
            markdown.add_heading(3, f'[TASK] {self.task_name}')
            markdown.add_heading(4, f'{self.host_name} ***(diff)***')
            markdown.add_diff_markdown(self.return_values.pretty_diff())
        return str(markdown)


class PlaybookResults:
    def __init__(self):
        self._results = []
        self._results_by_task = {}

    @property
    def tasks(self):
        """Get the list of the task names that are associated with this PlaybookResults.

        Returns:
            List[str]: List of the tasks names associated to this PlaybookResults.
        """
        return self._results_by_task.keys()

    def add(self, task_result: TaskResult):
        """Add a TaskResult to this collection.

        TaskResults should be added in the same order as they were executed.

        Args:
            task_result (TaskResult): A TaskResult to be added to this collection.
        """
        # 1. Store in a flat data structure
        self._results.append(task_result)
        # 2. Store in task-nested data structure
        if task_result.task_name not in self._results_by_task:
            self._results_by_task[task_result.task_name] = []
        self._results_by_task[task_result.task_name].append(task_result)

    def has_failures(self):
        return any(task_result.failed for task_result in self._results)

    def failures(self) -> Collection[TaskResult]:
        return list(filter(lambda task_result: task_result.failed, self._results))

    def by_task_name(self, task_name) -> Collection[TaskResult]:
        return self._results_by_task[task_name]
        # return filter(lambda task_result: task_result.task_name == task_name, self._results)

    def by_ansible_module(self, ansible_module):
        return list(filter(lambda task_result: task_result.ansible_module == ansible_module, self._results))

    @classmethod
    def from_json(cls, json_payload):
        """Take the json output of an ansible-playbook run and process it into a PlaybookResults data structure.

        Args:
            json_payload: The raw json output from running ansible-playbook. 
            This can be configured in the ansible.cfg file under [Defaults] > stdout_callback = json
        Requirements:
            Playbook runs need to be ran with --diff to get the correct output.

        Raises:
            JSONDecodeError: If the json_payload is not well formed.
        """
        output = json.loads(json_payload)

        # We should only have one play here, so let's make that assumption and allow the index error to take place otherwise.
        play = output['plays'][0]
        return cls._parse_playbook_results(play)

    @classmethod
    def _parse_playbook_results(cls, play):
        results = cls()
        for task in play['tasks']:
            for host_name, return_values in task['hosts'].items():
                task_details = task['task']
                results.add(cls._parse_task_result(return_values, host_name, task_details))
        return results

    @staticmethod
    def _parse_task_result(return_values_raw, host_name, task_details):
        # Surprising: the 'Ansible Module' associated to the task is not provided in task_details... 
        #   Instead, it is found as the `action` property from the return_values.
        ansible_module = return_values_raw['action']

        # Build a more useful return_values object to operate on
        return_values = return_values_factory.build(return_values_raw, ansible_module)

        # Generate the TaskResult data structure
        return TaskResult(return_values=return_values, failed=return_values.failed, 
                          ansible_module=ansible_module, host_name=host_name, task_name=task_details['name'],
                          start_time=task_details['duration']['start'], end_time=task_details['duration']['end'])
