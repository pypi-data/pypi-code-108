from __future__ import annotations
import os
import subprocess
from pathlib import Path

from .task import Task
from .scheduler import Scheduler


class PBS(Scheduler):
    output_file_pattern = r'[a-zA-Z]+.*\.[eo]+[1-9]+[0-9]*'

    def submit(self,
               task: Task,
               dry_run: bool = False,
               verbose: bool = False) -> None:
        nodelist = self.config.nodes
        nodes, nodename, nodedct = task.resources.select(nodelist)

        processes = task.resources.processes

        if processes < nodedct['cores']:
            ppn = processes
        else:
            assert processes % nodes == 0
            ppn = processes // nodes

        hours, rest = divmod(task.resources.tmax, 3600)
        minutes, seconds = divmod(rest, 60)

        qsub = ['qsub',
                '-N',
                task.cmd.short_name,
                '-l',
                f'walltime={hours}:{minutes:02}:{seconds:02}',
                '-l',
                f'nodes={nodes}:ppn={ppn}',
                '-d', str(task.folder)]

        qsub += self.config.extra_args + nodedct.get('extra_args', [])

        if task.dtasks:
            ids = ':'.join(tsk.id for tsk in task.dtasks)
            qsub.extend(['-W', f'depend=afterok:{ids}'])

        cmd = str(task.cmd)
        if task.resources.processes > 1:
            mpiexec = 'mpiexec -x OMP_NUM_THREADS=1 -x MPLBACKEND=Agg '
            if 'mpiargs' in nodedct:
                mpiexec += nodedct['mpiargs'] + ' '
            cmd = mpiexec + cmd.replace('python3',
                                        self.config.parallel_python)
        else:
            cmd = 'MPLBACKEND=Agg ' + cmd

        home = self.config.home

        script = '#!/bin/bash -l\n'

        script += task.get_venv_activation_line()

        script += (
            '#!/bin/bash -l\n'
            'id=${{PBS_JOBID%.*}}\n'
            'mq={home}/.myqueue/pbs-$id\n'
            '(touch $mq-0 && cd {dir} && {cmd} && touch $mq-1) || '
            'touch $mq-2\n'
            .format(home=home, dir=task.folder, cmd=cmd))

        if dry_run:
            print(qsub, script)
            return

        p = subprocess.Popen(qsub,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE)
        out, err = p.communicate(script.encode())
        assert p.returncode == 0
        id = out.split(b'.')[0].decode()
        task.id = id

    def error_file(self, task: Task) -> Path:
        return task.folder / f'{task.cmd.short_name}.e{task.id}'

    def cancel(self, task: Task) -> None:
        subprocess.run(['qdel', task.id])

    def get_ids(self) -> set[str]:
        user = os.environ['USER']
        cmd = ['qstat', '-u', user]
        p = subprocess.run(cmd, stdout=subprocess.PIPE)
        queued = {line.split()[0].split(b'.')[0].decode()
                  for line in p.stdout.splitlines()
                  if line[:1].isdigit()}
        return queued
