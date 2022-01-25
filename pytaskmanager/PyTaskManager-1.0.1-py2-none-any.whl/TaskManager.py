from contextlib import contextmanager
import time


class ExistTaskNameError(Exception):
    def __init__(self, task_name):
        super().__init__(f"Task name {task_name} is already exist.")


class SubTaskManager:
    def __init__(self, task_name):
        self.task_name = task_name

    def start(self):
        self.st = time.time()
        return self

    def stop(self):
        self.et = time.time()
        self.elapsed_time = self.et - self.st
 

class TaskManager:
    latest_task_name = None
    sub_task = {}
    task_name = []
    elapsed_time = {}

    def __init__(self, task_name):
        assert not task_name in self.task_name, ExistTaskNameError(task_name)
        self.latest_task_name = task_name
        self.sub_task[task_name] = SubTaskManager(task_name)
        self.task_name.append(task_name)
        self.elapsed_time[task_name] = None

    def __enter__(self):
        self.sub_task[self.latest_task_name].start()
        return self.sub_task[self.latest_task_name]

    def __exit__(self, exc_type, exc_value, tracaback):
        self.sub_task[self.latest_task_name].stop()

    @staticmethod
    def make_summary():
        for sub_task_name, sub_task in TaskManager.sub_task.items():
            TaskManager.elapsed_time[sub_task_name] = sub_task.elapsed_time

    @staticmethod
    def summary():
        print("Task Summary")
        TaskManager.make_summary()
        for task_name in TaskManager.task_name:
            print(f"\tTask name: {task_name} -> Elapsed time: {TaskManager.elapsed_time[task_name]:.4f}")



if __name__ == "__main__":
    with TaskManager("Sleep1") as tm1:
        with TaskManager("Sleep2") as tm2:
            time.sleep(1.0)
    
            with TaskManager("Sleep3") as tm3:
                time.sleep(1.0)
    
            with TaskManager("Sleep3") as tm4:
                time.sleep(1.0)
    
        time.sleep(1)
    
    
    TaskManager.summary()
