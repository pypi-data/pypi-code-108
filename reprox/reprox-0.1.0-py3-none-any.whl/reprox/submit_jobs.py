import glob
import json
import time
import os
import shlex
import subprocess
import typing as ty
from collections import defaultdict
import pandas as pd
import utilix
from strax.utils import tqdm
from utilix import batchq
from reprox import core
from reprox.process_job import ProcessingJob


def submit_jobs(submit_kwargs: ty.Optional[dict] = None,
                targets: ty.Union[
                    str,
                    ty.List[str],
                    ty.Tuple[str],
                ] = ('event_info', 'event_pattern_fit'),
                break_if_n_jobs_left_running: ty.Union[None, int] = None,
                clear_logs: bool = False,
                sleep_s_when_queue_full: int = 60,
                submit_only: ty.Union[None, int] = None,
                known_partitions: ty.Union[
                    tuple,
                    list,
                ] = core.config['processing']['allowed_partitions'].split(','),
                ) -> ty.List[ProcessingJob]:
    """
    Submit jobs to the queue for the given options

    :param submit_kwargs: dict of options that are passed on to the job
        submission
    :param targets: List of datatypes to produce
    :param break_if_n_jobs_left_running: threshold when to stop
        reporting the status
    :param clear_logs: If true, clear the logs from previous jobs
    :param sleep_s_when_queue_full: sleep this many seconds if the
    :param submit_only: maximum number of jobs to submit
    :param known_partitions: list of partitions this user can submit to
    :return: a list of all the jobs that were submitted
    """
    kwargs = dict(package=core.config['context']['package'],
                  context=core.config['context']['context'],
                  base_folder=core.config['context']['base_folder'],
                  )
    if submit_kwargs is not None:
        kwargs.update(submit_kwargs)

    if not os.path.exists(core.runs_csv):
        raise FileNotFoundError(f'{core.runs_csv} does not exist, run determine_data.py first!')

    if break_if_n_jobs_left_running is None:
        break_if_n_jobs_left_running = n_jobs_running()
        core.log.info(f'Currently have {break_if_n_jobs_left_running} jobs running'
                      f'We will keep updating the status until you have fewer than '
                      f'{break_if_n_jobs_left_running} jobs running')
    if clear_logs:
        _clear_old_logs()
    runs = pd.read_csv(core.runs_csv)['name'].values
    runs = [f'{r:06}' for r in runs]
    if submit_only != 0:
        runs = runs[:submit_only]
        core.log.info(f'Passed submit_only={submit_only}. Only processing a subset of runs')

    jobs = _make_jobs(
        runs=runs,
        targets=targets,
        **kwargs,
    )

    for i, job in enumerate(jobs):
        while not can_submit_more_jobs(core.config['processing']['max_jobs']):
            _print_jobs_status(_jobs_status_summary(jobs))
            time.sleep(sleep_s_when_queue_full)
        if i % 10 == 0 or i == 0:
            partition = cycle_queue(queues=known_partitions)
        job.submit(**dict(partition=partition,
                          qos=partition, ))

    core.log.info('Finished submitting jobs, let\'t keep updating the logs')
    _print_jobs_status(_jobs_status_summary(jobs))
    while n_jobs_running() > break_if_n_jobs_left_running:
        core.log.info(f"{n_jobs_running()} running jobs")
        _print_jobs_status(_jobs_status_summary(jobs))
        time.sleep(sleep_s_when_queue_full)
    return jobs


def _print_jobs_status(jobs_status: ty.Dict[str, int]):
    """Parse dict to log statement"""
    message = ''
    for status in sorted(list(jobs_status.keys())):
        n = jobs_status[status]
        message += f'{status}: {n} | '
    core.log.info(f'Running: {message[:-2]}')


def _jobs_status_summary(jobs: ty.List[ProcessingJob]):
    """For a list of jobs, extract the status"""
    status = defaultdict(int)
    status['total'] = len(jobs)
    for j in jobs:
        status[j.get_run_job_state()] += 1
    if status['busy'] + status['queue'] < 5:
        for j in jobs:
            if j.get_run_job_state() in ['busy', 'queue']:
                core.log.info(f'Running:\t{j}')
    return status


def _make_jobs(runs: ty.List[str],
               targets: ty.Union[str, ty.List[str], ty.Tuple[str]],
               base_folder: str,
               context: str,
               package: str,
               ram: int = int(core.config['processing']['ram']),
               cpus_per_task: int = int(core.config['processing']['cpus_per_job']),
               overwrite_kr_targets: bool = True,
               container='xenonnt-development.simg',
               include_config: ty.Union[None, dict] = None,
               context_config_kwargs: ty.Union[None, dict] = None,
               ) -> ty.List[ProcessingJob]:
    if not isinstance(targets, str):
        # Targets should be a string, if not, let's try or fail miserably
        targets = ' '.join(targets)
    jobs = []
    for i, run_name in tqdm(enumerate(runs),
                            total=len(runs),
                            disable=not bool(core.config['display']['progress_bar']),
                            desc='submitting runs'
                            ):
        job = _make_job(run_name=run_name,
                        targets=targets,
                        base_folder=base_folder,
                        context=context,
                        package=package,
                        ram=ram,
                        cpus_per_task=cpus_per_task,
                        overwrite_kr_targets=overwrite_kr_targets,
                        container=container,
                        include_config=include_config
                        )
        jobs.append(job)
    return jobs


def _make_job(run_name: ty.List[str],
              targets: ty.Union[str, ty.List[str], ty.Tuple[str]],
              base_folder: str,
              context: str,
              package: str,
              ram: int = int(core.config['processing']['ram']),
              cpus_per_task: int = int(core.config['processing']['cpus_per_job']),
              overwrite_kr_targets: bool = True,
              container='xenonnt-development.simg',
              include_config: ty.Union[None, dict] = None,
              context_config_kwargs: ty.Union[None, dict] = None,
              ) -> ProcessingJob:
    rd = get_rundoc(run_name)
    source = rd.get('source', 'none')
    submit_target = targets
    if source == 'kr-83m':
        submit_ram = ram * float(core.config['processing']['ram_multiplier_for_calibrations'])
        if overwrite_kr_targets:
            submit_target = submit_target.replace('event_info',
                                                  'event_info_double')
    elif source in ['rn-220', 'ambe']:
        submit_ram = ram * float(core.config['processing']['ram_multiplier_for_calibrations'])
    else:
        submit_ram = ram

    # Allow a different config to be set.
    if include_config is not None:
        extra_commands = f'--config_kwargs {json.dumps(include_config)}'
    else:
        extra_commands = ''
    if context_config_kwargs is not None and context_config_kwargs:
        extra_commands += f' --context_kwargs {json.dumps(context_config_kwargs)}'
    job_dir = os.path.join(core.config['context']['base_folder'], 'job_scripts')
    if not os.path.exists(job_dir):
        os.makedirs(job_dir)
    sbatch_file = os.path.join(job_dir, f'{run_name}-{targets.replace(" ", "_")}.sh')

    exec_command = core.command.format(
        base_folder=base_folder,
        context=context,
        package=package,
        run_name=run_name,
        target=submit_target,
        timeout=int(core.config['context']['straxer_timeout_seconds']),
        extra_options=extra_commands,
    )
    return ProcessingJob(
        run_id=run_name,
        targets=targets,
        submit_kwargs=dict(
            jobstring=exec_command,
            log=core.log_fn.format(run_id=run_name),
            jobname=f'{run_name}-{submit_target[:5]}_reprocess',
            mem_per_cpu=int(submit_ram / cpus_per_task),
            cpus_per_task=cpus_per_task,  # Almost never an issue, better ask for more RAM
            container=container,
            sbatch_file=sbatch_file,
        ),
    )


def n_jobs_running():
    return utilix.batchq.count_jobs(string=':')


def can_submit_more_jobs(nmax=core.config['processing']['max_jobs']):
    return n_jobs_running() < int(nmax)


def cycle_queue(queues=('xenon1t', 'dali', 'broadwl')
                ):
    res = {}
    cmd = f'squeue -u {os.environ["USER"]}'
    output = subprocess.check_output(shlex.split(cmd))
    lines = output.decode('utf-8').split('\n')
    for q in queues:
        q_lines = [l for l in lines if q in l]
        res[q] = len(q_lines)
    for k, v in res.items():
        if v == min(res.values()):
            core.log.debug(f'{k} is lowest with {v}')
            return k


def get_rundoc(run_id):
    return utilix.rundb.xent_collection().find_one({'number': int(run_id)})


def _clear_old_logs():
    old_logs = glob.glob(os.path.join(core.log_folder, '*.txt'))
    core.log.info(f'Clearing {len(old_logs)}-logfiles')
    for old_log_file in old_logs:
        core.log.debug(f'Clearing {old_log_file}')
        os.remove(old_log_file)
