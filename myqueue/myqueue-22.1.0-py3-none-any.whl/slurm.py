from __future__ import annotations
import os
import subprocess
import warnings
from math import ceil

from .task import Task
from .scheduler import Scheduler


class SLURM(Scheduler):
    def submit(self,
               task: Task,
               dry_run: bool = False,
               verbose: bool = False) -> None:
        nodelist = self.config.nodes
        nodes, nodename, nodedct = task.resources.select(nodelist)

        name = task.cmd.short_name
        sbatch = ['sbatch',
                  f'--partition={nodename}',
                  f'--job-name={name}',
                  f'--time={ceil(task.resources.tmax / 60)}',
                  f'--ntasks={task.resources.cores}',
                  f'--nodes={nodes}',
                  f'--chdir={task.folder}',
                  f'--output={name}.%j.out',
                  f'--error={name}.%j.err']

        extra_args = self.config.extra_args + nodedct.get('extra_args', [])
        if extra_args:
            sbatch += extra_args

        features = nodedct.get('features')
        if features:
            warnings.warn('Please use extra_args instead of features!')
            sbatch.append(f'--constraint={features}')

        reservation = nodedct.get('reservation')
        if reservation:
            warnings.warn('Please use extra_args instead of reservation!')
            sbatch.append(f'--reservation={reservation}')

        if task.dtasks:
            ids = ':'.join(tsk.id for tsk in task.dtasks)
            sbatch.append(f'--dependency=afterok:{ids}')

        env = []

        cmd = str(task.cmd)
        if task.resources.processes > 1:
            if 'OMP_NUM_THREADS' not in os.environ:
                env.append(('OMP_NUM_THREADS', '1'))
            mpiexec = self.config.mpiexec
            if 'mpiargs' in nodedct:
                mpiexec += ' ' + nodedct['mpiargs']
            cmd = mpiexec + ' ' + cmd.replace('python3',
                                              self.config.parallel_python)

        # Use bash for the script
        script = '#!/bin/bash -l\n'

        # Add environment variables
        if len(env) > 0:
            script += '\n'.join(f'export {name}={val}' for name, val in env)
            script += '\n'

        home = self.config.home
        script += (
            'id=$SLURM_JOB_ID\n'
            f'mq={home}/.myqueue/slurm-$id\n')

        script += task.get_venv_activation_line()

        script += (
            '(touch $mq-0 && \\\n'
            f' cd {str(task.folder)!r} && \\\n'
            f' {cmd} && \\\n'
            ' touch $mq-1) || \\\n'
            '(touch $mq-2; exit 1)\n')

        if dry_run:
            if verbose:
                print(' \\\n    '.join(sbatch))
                print(script)
            task.id = '1'
            return

        # Use a clean set of environment variables without any MPI stuff:
        p = subprocess.Popen(sbatch,
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             env=os.environ)
        out, err = p.communicate(script.encode())

        if p.returncode != 0:
            raise RuntimeError(err)

        task.id = out.split()[-1].decode()

    def cancel(self, task: Task) -> None:
        subprocess.run(['scancel', task.id])

    def hold(self, task: Task) -> None:
        subprocess.run(['scontrol', 'hold', task.id])

    def release_hold(self, task: Task) -> None:
        subprocess.run(['scontrol', 'release', task.id])

    def get_ids(self) -> set[str]:
        user = os.environ['USER']
        cmd = ['squeue', '--user', user]
        p = subprocess.run(cmd, stdout=subprocess.PIPE)
        queued = {line.split()[0].decode()
                  for line in p.stdout.splitlines()[1:]}
        return queued

    def maxrss(self, id: str) -> int:
        assert '.' not in id
        cmd = ['sacct',
               '-j', id,
               '-n',
               '--units=K',
               '-o', 'MaxRSS']
        try:
            p = subprocess.run(cmd, stdout=subprocess.PIPE)
        except FileNotFoundError:
            return 0
        mem = 0
        for line in p.stdout.splitlines():
            line = line.strip()
            if line.endswith(b'K'):
                mem = max(mem, int(line[:-1]) * 1000)
        return mem

    def get_config(self, queue: str = '') -> tuple[list[tuple[str, int, str]],
                                                   list[str]]:
        cmd = ['sinfo',
               '--noheader',
               '--format=%c %m %P']
        p = subprocess.run(cmd, stdout=subprocess.PIPE)
        nodes = []
        for line in p.stdout.decode().splitlines():
            cores, mem, name = line.split()
            nodes.append((name.rstrip('*'),
                          int(cores),
                          mem.rstrip('+') + 'M'))
        return nodes, []
