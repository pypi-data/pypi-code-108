"""
Runs jobs passing a function as an argument. Thread safe.
"""
import time

from delphixpy.v1_10_2 import exceptions
from delphixpy.v1_10_2.web import job
from colorama import Fore
from colorama import Style

from . import dlpx_exceptions
from . import dx_logging as log
from dxi._lib import util


def run_job(main_func, dx_obj, engine="default", single_thread=True):
    """
    This method runs the main_func asynchronously against all the
    delphix engines specified
    :param main_func: function to run against the DDP(s).
     In these examples, it's main_workflow().
    :type main_func: function
    :param dx_obj: Delphix session object from config
    :type dx_obj: lib.get_session.GetSession object
    :param engine: name of an engine, all or None
    :type engine: str
    :param single_thread: Run as single thread (True) or
                    multiple threads (False)
    :type single_thread: bool
    """
    threads = []
    # if engine ="all", run against every engine in config_file
    if engine == "all":
        log.print_info(f"Executing on all Delphix Engines")
        try:
            for delphix_ddp in dx_obj.dlpx_ddps:
                t = main_func(
                    dx_obj.dlpx_ddps[delphix_ddp], dx_obj, single_thread
                )
                threads.append(t)
                # TODO: Revisit threading logic
                # This sleep has been tactically added to prevent errors in the parallel
                # processing of operations across multiple engines
                time.sleep(1)
        except dlpx_exceptions.DlpxException as err:
            log.print_exception(f"Error encountered in run_job():{err}")
    elif engine == "default":
        try:
            for delphix_ddp in dx_obj.dlpx_ddps.keys():
                if dx_obj.dlpx_ddps[delphix_ddp]["default"] == "True":
                    dx_obj_default = dx_obj
                    dx_obj_default.dlpx_ddps = {
                        delphix_ddp: dx_obj.dlpx_ddps[delphix_ddp]
                    }
                    log.print_info(
                        "Executing on the default Delphix Engine"
                    )
                    t = main_func(
                        dx_obj.dlpx_ddps[delphix_ddp], dx_obj, single_thread
                    )
                    threads.append(t)
                break
        except TypeError as err:
            raise dlpx_exceptions.DlpxException(f"Error in run_job: {err}")
    else:
        # Test to see if the engine exists in config_file
        try:
            engine_ref = dx_obj.dlpx_ddps[engine]
            t = main_func(engine_ref, dx_obj, single_thread)
            threads.append(t)
            log.print_info(
                f"Executing on Delphix Engine: " f'{engine_ref["hostname"]}'
            )
        except (exceptions.RequestError, KeyError):
            raise dlpx_exceptions.DlpxException(
                f"\nERROR: Delphix Engine {engine} cannot be found. Please "
                f"check your input and try again."
            )
    if engine is None:
        raise dlpx_exceptions.DlpxException(
            f"ERROR: No default Delphix Engine found."
        )
    return threads


def _get_thread(main_func, engine, dx_obj, single_thread, helper_ref):
    if helper_ref:
        t = main_func(engine, dx_obj, single_thread, helper_ref)
    else:
        t = main_func(engine, dx_obj, single_thread)
    return t


def run_job_mt(
    main_func, dx_obj, engine="default", single_thread=True, helper_ref=None
):
    """
    This method runs the main_func asynchronously against all the
    delphix engines specified
    :param main_func: function to run against the DDP(s).
     In these examples, it's main_workflow().
    :type main_func: function
    :param dx_obj: Delphix session object from config
    :type dx_obj: lib.get_session.GetSession object
    :param engine: name of an engine, all or None
    :type engine: str
    :param single_thread: Run as single thread (True) or
                    multiple threads (False)
    :type single_thread: bool
    """
    threads = []
    # if engine ="all", run against every engine in config_file
    if engine == "all":
        log.print_debug(f"Executing on all configured Delphix Engines.")
        try:
            for delphix_ddp in dx_obj.dlpx_ddps:
                engine_ref = dx_obj.dlpx_ddps[delphix_ddp]
                dx_obj.jobs[engine_ref["ip_address"]] = []

                t = _get_thread(
                    main_func, engine_ref, dx_obj, single_thread, helper_ref
                )
                threads.append(t)
                time.sleep(2)
        except dlpx_exceptions.DlpxException as err:
            log.print_exception(
                f"Error encountered in run_job():\n{err}"
            )
            raise err
    elif engine == "default":
        try:
            for delphix_ddp in dx_obj.dlpx_ddps.keys():
                is_default = dx_obj.dlpx_ddps[delphix_ddp]["default"]
                if is_default and is_default.lower() == "true":
                    dx_obj_default = dx_obj
                    dx_obj_default.dlpx_ddps = {
                        delphix_ddp: dx_obj.dlpx_ddps[delphix_ddp]
                    }
                    engine_ref = dx_obj.dlpx_ddps[delphix_ddp]
                    dx_obj.jobs[engine_ref["ip_address"]] = []
                    log.print_debug(
                        f"Running on Delphix Engine {engine_ref['hostname']}"
                    )
                    t = _get_thread(
                        main_func,
                        engine_ref,
                        dx_obj,
                        single_thread,
                        helper_ref,
                    )
                    threads.append(t)
                    break
        except TypeError as err:
            log.print_exception(f"Error in run_job: {err}")
            raise dlpx_exceptions.DlpxException(f"Error in run_job: {err}")
        except (dlpx_exceptions.DlpxException) as e:
            log.print_exception(f"Error in run_job():\n{e}")
            raise e
    else:
        # Test to see if the engine exists in config_file
        try:
            engine_ref = dx_obj.dlpx_ddps[engine]
            dx_obj.jobs[engine_ref["ip_address"]] = []
            t = _get_thread(
                main_func, engine_ref, dx_obj, single_thread, helper_ref
            )
            threads.append(t)
            log.print_debug(
                f"Running on Delphix Engine {engine_ref['hostname']}"
            )
        except (exceptions.RequestError, KeyError):
            raise dlpx_exceptions.DlpxException(
                f"\nERROR: Delphix Engine: {engine} cannot be found. Please "
                f"check your input and try again."
            )
        except (dlpx_exceptions.DlpxException) as e:
            raise e
    if engine is None:
        raise dlpx_exceptions.DlpxException(
            f"ERROR: No default Delphix Engine found."
        )
    return threads


def track_running_jobs(
    engine, dx_obj, poll=10, failures=None, with_progress_bar=True
):
    """
    Tracks running jobs on an engine.
    Args:
        engine (Dictionary): Dictionary containing info on the DDP (IP, username, etc.)
        poll (int): How long to sleep between querying jobs
        dx_obj (GetSession): Delphix session object from config
    Raises:
        Exception

    """
    # get all the jobs, then inspect them
    if failures is None:
        failures = [False]
    engine_running_jobs = ""
    if engine["ip_address"] in dx_obj.jobs:
        engine_running_jobs = dx_obj.jobs[engine["ip_address"]]
    if not engine_running_jobs:
        log.print_debug(
            f'No running jobs on engine : {engine["hostname"]}'
        )
    else:
        log.print_info(f'Tracking running jobs on {engine["hostname"]}')
    while engine_running_jobs:
        for j in engine_running_jobs:
            job_obj = job.get(dx_obj.server_session, j)
            if job_obj.job_state in ["COMPLETED"]:
                engine_running_jobs.remove(j)
                print(f"\t{engine['hostname']} : {Fore.CYAN}{job_obj.reference} : 100% {Style.RESET_ALL}")
            elif job_obj.job_state in ["CANCELED", "FAILED"]:
                err_msg = extract_failure_message(job_obj, engine["hostname"])
                engine_running_jobs.remove(j)
                log.print_exception(f"{engine['hostname']}:{job_obj.reference} FAILED or was CANCELLED "
                      f"due to an error.", stdout= False)
                log.print_exception(f"{err_msg}")
                print(f"\t{engine['hostname']}:{Fore.RED}{job_obj.reference}:{job_obj.percent_complete}% {Style.RESET_ALL}")
                failures[0] = True
            elif job_obj.job_state in "RUNNING":
                print(f"\t{engine['hostname']} : {Fore.CYAN}{job_obj.reference} : {job_obj.percent_complete}% {Style.RESET_ALL}")
        if engine_running_jobs:
            time.sleep(poll)


def extract_failure_message(jobobj, engine_ref):
    try:
        if jobobj.job_state=='CANCELED':
            err_msg = util.format_err_msg(
                jobobj.cancel_reason,
                operation=jobobj.action_type,
                object_name=jobobj.target_name,
                engine_name=engine_ref
            )
        return err_msg
    except Exception as err:
        log.print_exception(err)
        return


def find_job_state(engine, dx_obj, poll=5):
    """
    Retrieves running job state
    :param engine: Dictionary containing info on the DDP (IP, username, etc.)
    :param poll: How long to sleep between querying jobs
    :param dx_obj: Delphix session object from config
    :type dx_obj: lib.get_session.GetSession object
    :type poll: int
    :return:
    """
    # get all the jobs, then inspect them
    log.print_debug(f"Checking running jobs state")
    i = 0
    for j in dx_obj.jobs.keys():
        print(len(dx_obj.jobs), j)
        job_obj = job.get(dx_obj.server_session, dx_obj.jobs[j])
        log.print_debug(
            f'{engine["ip_address"]}: Running job: ' f"{job_obj.job_state}"
        )
        if job_obj.job_state in ["CANCELED", "COMPLETED", "FAILED"]:
            # If the job is in a non-running state, remove it
            # from the running jobs list.
            del dx_obj.jobs[j]
            if len(dx_obj.jobs) == 0:
                break
        elif job_obj.job_state in "RUNNING":
            # If the job is in a running state, increment the
            # running job count.
            i += 1
        log.print_debug(f'{engine["ip_address"]}: {i} jobs running.')
        # If we have running jobs, pause before repeating the
        # checks.
        if dx_obj.jobs:
            time.sleep(poll)
        else:
            log.print_debug(f"No jobs running")
            break


def find_job_state_by_jobid(engine, dx_obj, job_id, poll=20):
    """
    Retrieves running job state
    :param engine: Dictionary containing info on the DDP (IP, username, etc.)
    :param poll: How long to sleep between querying jobs
    :param dx_obj: Delphix session object from config
    :type dx_obj: lib.get_session.GetSession object
    :param job_id: Job ID to check the state
    :type poll: int
    :return:
    """
    # get the job object
    job_obj = job.get(dx_obj.server_session, job_id)
    log.print_debug(job_obj)
    log.print_debug(f" Waiting for : {job_id} to finish")
    while job_obj.job_state == "RUNNING":
        time.sleep(poll)
        job_obj = job.get(dx_obj.server_session, job_id)
    log.print_debug(
        f"Job: {job_id} completed with status: {job_obj.job_state}"
    )
    return job_obj.job_state


def time_elapsed(time_start):
    """
    This function calculates the time elapsed since the beginning of the script.
    Call this anywhere you want to note the progress in terms of time
    :param time_start: start time of the script.
    :type time_start: float
    """
    return round((time.time() - time_start) / 60, +1)
