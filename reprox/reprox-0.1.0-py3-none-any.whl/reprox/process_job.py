import os
import utilix
from utilix import batchq
from reprox import core


class ProcessingJob:
    """
    Class for starting jobs and keeping an eye on their status
    """
    submit_message = None

    def __init__(self, run_id, targets, submit_kwargs):
        self.run_id = run_id
        self.targets = targets
        self.submit_kwargs = submit_kwargs

    def submit(self, **extra_kwargs):
        """Submit the job to be run"""
        self.submit_message = self._submit(
            **{**self.submit_kwargs,
               **extra_kwargs}
        )
        core.log.info(f'Submitted {self}')

    @staticmethod
    def _submit(**kwargs):
        return utilix.batchq.submit_job(**kwargs)

    def __repr__(self):
        rep = f"Process {self.run_id}-{self.targets}| status: {self.get_run_job_state()}"
        if self.submit_message is not None:
            rep += '| ' + str(self.submit_message)
        return rep

    def get_run_job_state(
            self,
            read_last=10,
            ignore_patterns=core.config['processing']['ignore_patterns_in_logs'].split(',')
    ) -> str:
        """Get the state of the current job"""
        fn = core.log_fn.format(run_id=self.run_id)
        if not os.path.exists(fn):
            return 'queue'

        with open(fn, 'r') as f:
            lines = f.read().splitlines()
            end = lines[-read_last * 2:]
        end = [line for line in end if all(p not in line for p in ignore_patterns)]
        _pr = ' '.join(end).lower()

        if 'killed' in _pr or 'error' in _pr or 'raise' in _pr:
            return 'error'
        if 'end' in _pr:
            return 'done'
        return 'busy'
