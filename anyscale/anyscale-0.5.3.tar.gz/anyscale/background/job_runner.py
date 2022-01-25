import os
import re
import subprocess
import time
from typing import Any, Dict, Optional, Union
import uuid

import yaml

from anyscale.background.job_context import BackgroundJob, BackgroundJobContext
from anyscale.sdk.anyscale_client.sdk import AnyscaleSDK
from anyscale.shared_anyscale_utils.conf import (
    ANYSCALE_BACKGROUND_JOB_CONTEXT,
    BACKGROUND_ACTOR_NAME,
)


class BackgroundJobRunner:
    """
    This class is an actor that runs a shell command on the head node for an anyscale cluster.
    This class will:
    1. Pass a BackgroundJobContext as an environment variable
    2. execute the command in a subprocess (and stream logs appropriately)
    3. Gracefully exit when the command is complete
    """

    def run_background_job(
        self, command: str, self_handle: Any, context: BackgroundJobContext,
    ) -> None:
        import ray

        # Update the context with the runtime env uris
        uris = [u for u in ray.get_runtime_context().runtime_env["uris"]]
        context.runtime_env_uris = uris
        env_vars = {
            "PYTHONUNBUFFERED": "1",  # Make sure python subprocess streams logs https://docs.python.org/3/using/cmdline.html#cmdoption-u
            "RAY_ADDRESS": "anyscale://",  # Make sure that internal ray.init has an anyscale RAY_ADDRESS
            ANYSCALE_BACKGROUND_JOB_CONTEXT: context.to_json(),
        }
        env = {**os.environ, **env_vars}

        try:
            run_kill_child(command, shell=True, check=True, env=env)  # noqa
        finally:
            # allow time for any logs to propogate before the task exits
            time.sleep(1)

            self_handle.stop.remote()

    def stop(self) -> None:
        import ray

        ray.actor.exit_actor()


def _parse_runtime_env(
    env: Optional[Union[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    """
    If `env` is a string, it represents a YAML file. Load the file and return the dict.
    Otherwise, return the dict that is passed in, or {} if nothing is passed
    """
    if isinstance(env, str):
        with open(env, "r") as stream:
            try:
                return yaml.safe_load(stream)  # type: ignore
            except yaml.YAMLError as e:
                raise ValueError(
                    f"Failed while attempting to load a runtime env yaml spec into a runtime environment dictionary. Please ensure that the file {env} is specified correctly",
                    e,
                )
    else:
        return env or {}


# TODO(mattweber): Once this code has been deployed in a CLI release
# that we can expect to be available on product clusters, migrate all
# use of _run_kill_child to this function.
def run_kill_child(
    *popenargs, input=None, timeout=None, check=False, **kwargs
) -> subprocess.CompletedProcess:
    return _run_kill_child(
        *popenargs, input=input, timeout=timeout, check=check, **kwargs
    )


# TODO(mattweber): This is a public function despite the underscore.
# Renaming this function in this PR is problematic for setup_dev_ray in
# config_controller because it needs to import this function
# for use in a remote function.
def _run_kill_child(
    *popenargs, input=None, timeout=None, check=False, **kwargs
) -> subprocess.CompletedProcess:
    """
    This function is a fork of subprocess.run with fewer args.
    The goal is to create a child subprocess that is GUARANTEED to exit when the parent exits
    This is accomplished by:
    1. Making sure the child is the head of a new process group
    2. Create a third "Killer" process that is responsible for killing the child when the parent dies
    3. Killer process checks every second if the parent is dead.
    4. Killing the entire process group when we want to kill the child

    Arguments are the same as subprocess.run
    """
    # Start new session ensures that this subprocess starts as a new process group
    with subprocess.Popen(start_new_session=True, *popenargs, **kwargs) as process:
        parent_pid = os.getpid()
        child_pid = process.pid
        child_pgid = os.getpgid(child_pid)

        # Open a new subprocess to kill the child process when the parent process dies
        # kill -s 0 parent_pid will succeed if the parent is alive.
        # If it fails, SIGKILL the child process group and exit
        subprocess.Popen(
            f"while kill -s 0 {parent_pid}; do sleep 1; done; kill -9 -{child_pgid}",
            shell=True,
            # Suppress output
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        try:
            stdout, stderr = process.communicate(input, timeout=timeout)
        except:  # noqa      (this is taken from subprocess.run directly)
            # Including KeyboardInterrupt, communicate handled that.
            process.kill()
            # We don't call process.wait() as .__exit__ does that for us.
            raise

        retcode = process.poll()
        if check and retcode:
            raise subprocess.CalledProcessError(
                retcode, process.args, output=stdout, stderr=stderr
            )
    return subprocess.CompletedProcess(process.args, retcode or 0, stdout, stderr)


def _generate_job_name(command: str) -> str:
    """
    Escape the command string to get the job name, and replace spaces and periods with _
    """
    return re.sub(r"\W+", "", re.sub(r"[\. ]", "_", command))


def _wait_for_db_id(
    sdk: AnyscaleSDK, cluster_id: str, ray_job_id: str, timeout_secs=20
) -> Any:
    for _ in range(timeout_secs):
        time.sleep(1)
        jobs = sdk.search_jobs(
            {"ray_job_id": ray_job_id, "cluster_id": cluster_id}
        ).results

        if len(jobs) > 0:
            # This should be the db job
            return jobs[0]

    return None


class JobNotFoundError(RuntimeError):
    pass


def run(
    command: str,
    runtime_env: Optional[Union[str, Dict[str, Any]]] = None,
    address: Optional[str] = None,
) -> BackgroundJob:
    """
    This function lets you execute a shell command in the background on a ray cluster, in a specific environment

    This function returns a BackgroundJobContext object that let's you wait for or kill the scheduled job

    :param command: This is the first param
    @param param2: this is the second param

    Args:
        command: The shell command to run. Eg. "python script.py"
        runtime_env: The OSS Ray runtime environment in which to run the command. Should be a dict or a path.
            Please see the Ray runtime env documentation for the format
        address: The address of the cluster to run the command on. Must start with 'anyscale://'

    Returns:
        BackgroundJob object. You can use this object to wait for the job, or to kill it

    Examples:
        >>> script.py
        >>> # connect as normal
        >>> ray.init("anyscale://")

        >>> runner.py
        >>> ctx = run("python script.py", runtime_env="env.yaml", address="anyscale://")
        >>> ctx.wait() # wait for the job
        >>> ctx.kill() # kill the job
    """
    # lazy imports
    # ray is required to run in the background
    import ray

    from anyscale import ClientBuilder

    # handle optional args
    address = address or os.getenv("RAY_ADDRESS") or "anyscale://"
    runtime_env = _parse_runtime_env(runtime_env)
    namespace = f"bg_{str(uuid.uuid4())}"

    if not address.startswith("anyscale://"):
        raise ValueError(
            "Anyscale run can only be used to connect to anyscale clusters"
        )

    _, inner_address = address.split("://", maxsplit=1)

    # This is just setting a default, and will be overwritten by the inner job name
    outer_job_name = _generate_job_name(command)

    # Connect the outer ray client.
    # Start an outer job that will be used to ship the users file system
    client = ClientBuilder(inner_address)
    logger = client._log
    logger.info(
        f"Running in namespace: {namespace}. You can use this namespace as a reference to access this background job in the future."
    )
    # Enable this job's metadata to be overwritten by any children jobs
    client._bg_set_outer_overwritable()
    client_context = (
        client.env(runtime_env).job_name(outer_job_name).namespace(namespace).connect()
    )

    # Construct the actor to run the inner job in
    BackgroundJobRunnerActor = ray.remote(BackgroundJobRunner)  # noqa
    actor = BackgroundJobRunnerActor.options(
        lifetime="detached", name=BACKGROUND_ACTOR_NAME
    ).remote()

    # grab the creator id from the job config of the outer job
    creator_db_id = client._job_config.metadata["creator_id"]
    outer_job_id = ray.get_runtime_context().job_id.hex()

    # generate a random cross reference id to identify the created job later
    context = BackgroundJobContext(
        creator_db_id=creator_db_id,
        original_command=command,
        namespace=namespace,
        # This will be populated in the actor
        runtime_env_uris=[],
        parent_ray_job_id=outer_job_id,
    )

    # Kick off the job
    remote_ref = actor.run_background_job.remote(
        command=command, self_handle=actor, context=context
    )

    # Wait for the Job to be populated in the db table and then fetch it and grab it's id
    db_job = _wait_for_db_id(
        client._anyscale_sdk,
        cluster_id=client_context.anyscale_cluster_info.cluster_id,
        ray_job_id=outer_job_id,
    )
    if not db_job:
        raise JobNotFoundError(
            "Failed to find the corresponding job in the Anyscale DB. This job may not have been scheduled."
        )

    return BackgroundJob(actor, remote_ref, context, client_context, db_job)
