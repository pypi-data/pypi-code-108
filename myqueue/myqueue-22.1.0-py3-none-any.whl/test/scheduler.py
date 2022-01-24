from __future__ import annotations
import subprocess
import sys

from myqueue.config import Configuration
from myqueue.scheduler import Scheduler
from myqueue.states import State
from myqueue.task import Task


class TestScheduler(Scheduler):
    current_scheduler: TestScheduler | None = None

    def __init__(self, config: Configuration):
        Scheduler.__init__(self, config)
        self.folder = self.config.home / '.myqueue'
        self.tasks: list[Task] = []
        self.number = 0

    def submit(self,
               task: Task,
               dry_run: bool = False,
               verbose: bool = False) -> None:
        if dry_run:
            task.id = '1'
            return
        if task.dtasks:
            ids = {t.id for t in self.tasks}
            for t in task.dtasks:
                assert t.id in ids
        self.number += 1
        task.id = str(self.number)
        self.tasks.append(task)

    def cancel(self, task):
        assert task.state == 'queued', task
        for i, j in enumerate(self.tasks):
            if task.id == j.id:
                break
        else:
            return
        del self.tasks[i]

    def hold(self, task):
        assert task.state == 'queued', task
        for i, j in enumerate(self.tasks):
            if task.id == j.id:
                break
        else:
            raise ValueError('No such task!')
        j.state = State.hold

    def release_hold(self, task):
        assert task.state == 'hold', task
        for i, j in enumerate(self.tasks):
            if task.id == j.id:
                break
        else:
            raise ValueError('No such task!')
        j.state = State.queued

    def get_ids(self):
        return {task.id for task in self.tasks}

    def kick(self) -> bool:
        for task in self.tasks:
            if task.state == 'queued' and not task.deps:
                break
        else:
            return True

        self.run(task)
        return False

    def run(self, task):
        out = f'{task.cmd.short_name}.{task.id}.out'
        err = f'{task.cmd.short_name}.{task.id}.err'

        cmd = str(task.cmd)
        cmd = cmd.replace('python3', sys.executable)
        if task.resources.processes > 1:
            n = task.resources.processes
            cmd = f'MYQUEUE_TEST_NPROCESSES={n} ' + cmd
        cmd = f'cd {task.folder} && {cmd} 2> {err} > {out}'
        activation_script = task.activation_script
        if activation_script:
            cmd = f'. {activation_script} && ' + cmd
        (self.folder / f'test-{task.id}-0').write_text('')
        tmax = task.resources.tmax
        try:
            result = subprocess.run(cmd,
                                    shell=True,
                                    check=not True,
                                    timeout=tmax)
        except subprocess.TimeoutExpired:
            state = State.TIMEOUT
        else:
            if result.returncode == 0:
                state = State.done
            else:
                state = State.FAILED
        self.update(task, state)

    def update(self, task: Task, state: State) -> None:
        n = {State.done: 1,
             State.FAILED: 2,
             State.TIMEOUT: 3}[state]

        (self.folder / f'test-{task.id}-{n}').write_text('')

        if state == 'done':
            tasks = []
            for j in self.tasks:
                if j is not task:
                    if task.dname in j.deps:
                        j.deps.remove(task.dname)
                    tasks.append(j)
            self.tasks = tasks
        else:
            task.state = State.CANCELED
            task.cancel_dependents(self.tasks, 0)
            self.tasks = [task for task in self.tasks
                          if task.state != 'CANCELED']
