import time
from collections import OrderedDict


class ExistTaskNameError(Exception):
    def __init__(self, task_name):
        super().__init__(f"Task name {task_name} is already exist.")


class SubTaskManager:
    def __init__(self, task_name):
        """
        Arguments:
        ----------
            task_name {str} -- task name
        """
        self.task_name = task_name
        self.elapsed_time = 0.0

    def _start_timer(self):
        """start timer"""
        self.st = time.time()
        self.is_tracking = True

    def start(self):
        """call this function when SubTaskManager is started."""
        self._start_timer()
        return self

    def stop(self):
        """stop timer and calculate elapsed time."""
        self.elapsed_time += time.time() - self.st

    def pause_track(self):
        self.stop()

    def restart_track(self):
        self._start_timer()


class TaskManager:
    latest_task_name = None
    sub_task = OrderedDict()
    elapsed_time = {}
    running_tasks = []

    def __init__(self, task_name):
        self.latest_task_name = task_name
        self.running_tasks.append(task_name)
        if not task_name in self.sub_task:
            self.sub_task[task_name] = {0: SubTaskManager(task_name)}
            self.elapsed_time[task_name] = {0: None}
        else:
            self.sub_task[task_name][self.get_latest_task_length()] = SubTaskManager(
                task_name
            )
            self.elapsed_time[task_name][self.get_latest_task_length()] = None

    def get_latest_task_length(self) -> int:
        return len(self.sub_task[self.latest_task_name])

    @staticmethod
    def get_task_length(task_name) -> int:
        return len(TaskManager.sub_task[task_name])

    def __enter__(self):
        self.sub_task[self.latest_task_name][self.get_latest_task_length() - 1].start()
        return self.sub_task[self.latest_task_name][self.get_latest_task_length() - 1]

    def __exit__(self, exc_type, exc_value, tracaback):
        self.sub_task[self.latest_task_name][self.get_latest_task_length() - 1].stop()
        self.running_tasks.remove(self.latest_task_name)

    @staticmethod
    def make_summary():
        for sub_task_name, sub_task in TaskManager.sub_task.items():
            avg_time = sum([task.elapsed_time for task in sub_task.values()]) / len(
                sub_task
            )
            TaskManager.elapsed_time[sub_task_name] = avg_time

    @staticmethod
    def summary():
        print("Task Summary")
        TaskManager.make_summary()
        for task_name in TaskManager.sub_task.keys():
            print(
                f"\tTask name: {task_name} -> Average Elapsed time: {TaskManager.elapsed_time[task_name]:.4f}"
            )

    @staticmethod
    def pause_track(root_task_name: str = "all"):
        assert root_task_name in TaskManager.running_tasks or root_task_name == "all"
        if root_task_name == "all":
            for task_name in TaskManager.running_tasks:
                TaskManager.sub_task[task_name][
                    TaskManager.get_task_length(task_name) - 1
                ].pause_track()

        else:
            execute_pause = False
            for task_name in TaskManager.running_tasks:
                if task_name == root_task_name:
                    execute_pause = True

                if execute_pause:
                    TaskManager.sub_task[task_name][
                        TaskManager.get_task_length(task_name) - 1
                    ].pause_track()

    @staticmethod
    def restart_track(root_task_name: str = "all"):
        assert root_task_name in TaskManager.running_tasks or root_task_name == "all"
        if root_task_name == "all":
            for task_name in TaskManager.running_tasks:
                TaskManager.sub_task[task_name][
                    TaskManager.get_task_length(task_name) - 1
                ].restart_track()

        else:
            execute_pause = False
            for task_name in TaskManager.running_tasks:
                if task_name == root_task_name:
                    execute_pause = True

                if execute_pause:
                    TaskManager.sub_task[task_name][
                        TaskManager.get_task_length(task_name) - 1
                    ].restart_track()