import asyncio
import os
from types import SimpleNamespace

from anyscale.background.job_context import BackgroundJob, BackgroundJobContext
from anyscale.shared_anyscale_utils.conf import ANYSCALE_BACKGROUND_JOB_CONTEXT


def test_job_context() -> None:
    """"
    Test that the job context can be serialized and deserialized correctly
    """
    context = BackgroundJobContext("creator", "cmd", "ns", ["uri"], "par_job_id")
    d = context.to_env_dict()
    assert ANYSCALE_BACKGROUND_JOB_CONTEXT in d
    os.environ[ANYSCALE_BACKGROUND_JOB_CONTEXT] = d[ANYSCALE_BACKGROUND_JOB_CONTEXT]
    c2 = BackgroundJobContext.load_from_env()
    assert c2.__dict__ == context.__dict__


async def test_job_await() -> None:
    """
    Test that if the ref to a background job is awaitable, so is the job itself
    """

    async def hang_and_return() -> str:

        await asyncio.sleep(1)
        return "done hanging!"

    ref = hang_and_return()

    job = BackgroundJob(None, ref, None, None, SimpleNamespace(id="id"))  # type: ignore

    # Job should be awaitable
    result = await job
    assert result == "done hanging!"
