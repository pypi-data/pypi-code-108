import json
import os
from typing import Any, Dict, List, Optional

from anyscale.shared_anyscale_utils.conf import ANYSCALE_BACKGROUND_JOB_CONTEXT
from anyscale.utils.connect_helpers import AnyscaleClientContext


class BackgroundJobContext:
    """
    This class represents the runtime context that is passed from the outer job to the inner job for background jobs.
    It is intended to be serialized and passed as an environment variable.
    """

    # Each of these fields represents some metadata that will be attached to the inner job

    # The user id of the creator of this job
    creator_db_id: str

    # The original command used to run the job
    original_command: str

    # The namespace the job should be run in
    namespace: str

    # The packaged working directory that this job should use.
    # We use this instead of working directory becuase it's machine agnostic
    runtime_env_uris: List[str]

    # The ray job id of the parent job
    parent_ray_job_id: str

    def __init__(
        self,
        creator_db_id: str,
        original_command: str,
        namespace: str,
        runtime_env_uris: List[str],
        parent_ray_job_id: str,
    ):
        self.creator_db_id = creator_db_id
        self.original_command = original_command
        self.namespace = namespace
        self.runtime_env_uris = runtime_env_uris
        self.parent_ray_job_id = parent_ray_job_id

    def to_json(self) -> str:
        return json.dumps(self.__dict__)

    def to_env_dict(self) -> Dict[str, Any]:
        return {
            ANYSCALE_BACKGROUND_JOB_CONTEXT: self.to_json(),
        }

    @staticmethod
    def from_json(j: str) -> "BackgroundJobContext":
        return BackgroundJobContext(**json.loads(j))

    @staticmethod
    def load_from_env() -> Optional["BackgroundJobContext"]:

        env_var = os.environ.get(ANYSCALE_BACKGROUND_JOB_CONTEXT)
        if not env_var:
            return None
        return BackgroundJobContext.from_json(env_var)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, BackgroundJobContext):
            return self.__dict__ == other.__dict__  # type: ignore
        return False


class BackgroundJob:
    """
    This class is used to manage a backgrounded job.

    Examples:
        >>> bg_job = run(...)
        >>> bg_job.wait() # wait for the job sync
        >>> await bg_job # await the job
        >>> bg_job.kill() # kill the job
    """

    def __init__(
        self,
        actor: Any,
        remote_ref: Any,
        context: BackgroundJobContext,
        ray_client_context: AnyscaleClientContext,
        db_job: Any,
    ):
        import ray

        self.__ref = remote_ref
        self.__actor = actor
        self.__ray = ray
        self.__context = context
        self.__ray_client_context = ray_client_context
        self.__db_job = db_job
        self.id: str = db_job.id

    @property
    def context(self) -> BackgroundJobContext:
        return self.__context

    @property
    def client_context(self) -> Any:
        return self.__ray_client_context

    @property
    def ref(self) -> Any:
        return self.__ref

    @property
    def cluster_id(self) -> str:
        return self.__ray_client_context.anyscale_cluster_info.cluster_id

    def wait(self) -> None:
        self.__ray.get(self.__ref)

    def __await__(self) -> Any:
        return self.__ref.__await__()

    def kill(self) -> None:
        self.__ray.kill(self.__actor)
