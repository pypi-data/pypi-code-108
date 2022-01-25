from multiprocessing import Process
from pathlib import Path
from types import SimpleNamespace
from typing import List
from unittest.mock import Mock, patch

import pytest
from tests.test_connect import _make_test_builder

from anyscale.background.job_context import BackgroundJobContext
from anyscale.background.job_runner import (
    _generate_job_name,
    BackgroundJobRunner,
    run,
    run_kill_child,
)
from anyscale.connect import ClientBuilder
from anyscale.shared_anyscale_utils.conf import (
    ANYSCALE_BACKGROUND_JOB_CONTEXT,
    BACKGROUND_ACTOR_NAME,
)


def test_job_runner_actor():
    """
    Test that the job runner actor is passing the correct args to the subprocess
    """
    mock_runtime_env = {"uris": ["a", "b", "c"]}
    mock_ray = Mock()
    mock_ray.get_runtime_context.return_value.runtime_env = mock_runtime_env

    mock_run_kill_child = Mock()

    mock_actor_handle = Mock()
    mock_actor_handle.stop.remote = Mock()

    mock_os = Mock()
    mock_os.environ = {}

    context = BackgroundJobContext("creator", "cmd", "ns", [], "par_job_id")

    with patch.dict("sys.modules", ray=mock_ray, os=mock_os), patch.multiple(
        "anyscale.background.job_runner",
        os=mock_os,
        run_kill_child=mock_run_kill_child,
    ):
        runner = BackgroundJobRunner()
        runner.run_background_job("cmd", mock_actor_handle, context)

        context.runtime_env_uris = mock_runtime_env["uris"]

        mock_run_kill_child.assert_called_once_with(
            "cmd",
            shell=True,
            check=True,
            env={
                "PYTHONUNBUFFERED": "1",  # Make sure python subprocess streams logs https://docs.python.org/3/using/cmdline.html#cmdoption-u
                "RAY_ADDRESS": "anyscale://",  # Make sure that internal ray.init has an anyscale RAY_ADDRESS
                ANYSCALE_BACKGROUND_JOB_CONTEXT: context.to_json(),
            },
        )

        mock_actor_handle.stop.remote.assert_called_once()


def test_generate_command_name_default() -> None:
    """
    Test generation of job name default from command
    """

    assert _generate_job_name("python abc.py") == "python_abc_py"
    assert _generate_job_name("rllib train -f train.py") == "rllib_train_f_train_py"
    assert _generate_job_name("./my_script.sh") == "_my_script_sh"


def test_non_anyscale_address() -> None:
    """
    Test that anyscale.background.run fails for non anyscale addresses
    """
    try:
        run("cmd", {"pip": "r"}, "ray://")
    except ValueError:
        pass
    except Exception:
        pytest.fail("ray:// address should not be accepted")


def test_run_job(tmp_path: Path):
    """
    Tests the anyscale.background.run function
    Ensure that data is passed into ray correctly
    Ensure the context is set correctly
    """
    builder, _, _, _ = _make_test_builder(tmp_path)
    mock_background_job_runner = Mock()
    builder.connect = Mock()
    cluster_id = "cluster_id"
    builder.connect.return_value.anyscale_cluster_info.cluster_id = cluster_id
    builder._job_config.metadata["creator_id"] = "cid"
    builder._anyscale_sdk.search_jobs.return_value.results = [
        SimpleNamespace(id="job_id")
    ]
    mock_client_builder = Mock(return_value=builder)
    mock_uuid = Mock(return_value="ns")
    mock_get_runtime_ctx = Mock()
    mock_get_runtime_ctx.return_value.job_id.hex.return_value = "par_job_id"

    with patch.multiple("anyscale", ClientBuilder=mock_client_builder), patch(
        "ray.remote", new=Mock(return_value=mock_background_job_runner),
    ), patch("uuid.uuid4", new=mock_uuid), patch(
        "ray.get_runtime_context", new=mock_get_runtime_ctx
    ):

        address = "anyscale://cluster"
        job = run("cmd", {"pip": "r"}, address)
        mock_client_builder.assert_called_once_with("cluster")
        mock_uuid.assert_called_once()

        b: ClientBuilder = builder
        b._job_config.set_ray_namespace.assert_called_once_with("bg_ns")
        b._job_config.set_metadata.assert_called_with("job_name", "cmd")
        b._job_config.set_metadata.has_call("inherit_from_child", "1")

        mock_background_job_runner.options.assert_called_once_with(
            lifetime="detached", name=BACKGROUND_ACTOR_NAME
        )

        context = BackgroundJobContext(
            "cid",
            "cmd",
            namespace="bg_ns",
            runtime_env_uris=[],
            parent_ray_job_id="par_job_id",
        )
        actor = mock_background_job_runner.options.return_value.remote.return_value
        mock_background_job_runner.options.return_value.remote.return_value.run_background_job.remote.assert_called_once_with(
            command="cmd", context=context, self_handle=actor,
        )

        # Check that we are waiting for the job correctly
        b._anyscale_sdk.search_jobs.assert_called_once_with(
            {"ray_job_id": "par_job_id", "cluster_id": cluster_id}
        )

        assert job.context == context

        # Check the private variables and make sure they are correct
        assert job._BackgroundJob__actor == actor  # type: ignore
        assert job.ref == actor.run_background_job.remote.return_value  # type: ignore
        assert job.id == "job_id"


def _run_in_new_process():
    run_kill_child(
        "echo 'mfjrk' && sleep 5 && echo 'do not print this'", shell=True,
    )


async def test_run_kill_child():
    import asyncio

    import psutil

    p = Process(target=_run_in_new_process)
    p.start()

    main_pid = p.pid
    main_process = psutil.Process(main_pid)

    await asyncio.sleep(2)
    all_children: List[psutil.Process] = main_process.children(recursive=True)

    assert len(all_children) > 2  # assert that children were spawned
    for child in all_children:
        assert child.is_running()  # assert that all children are running
    p.terminate()
    p.join()

    await asyncio.sleep(2)
    # Assert that all of the children are dead
    for child in all_children:
        assert not child.is_running()
