import concurrent.futures
import datetime
import os
import time
from typing import List

import pendulum
import pytest
from dagster import RunRequest, daily_schedule, graph, in_process_executor, op, repository, sensor
from dagster.core.errors import DagsterUserCodeUnreachableError
from dagster.core.host_representation.origin import (
    ExternalRepositoryOrigin,
    RegisteredRepositoryLocationOrigin,
)
from dagster.core.host_representation.repository_location import GrpcServerRepositoryLocation
from dagster.core.launcher.base import LaunchRunContext
from dagster.core.test_utils import poll_for_finished_run, poll_for_step_start
from dagster.grpc.types import (
    ExecutionPlanSnapshotArgs,
    ExternalScheduleExecutionArgs,
    NotebookPathArgs,
    PartitionArgs,
    PartitionNamesArgs,
    PartitionSetExecutionParamArgs,
    PipelineSubsetSnapshotArgs,
    SensorExecutionArgs,
)
from dagster.serdes import deserialize_json_to_dagster_namedtuple, serialize_dagster_namedtuple
from dagster.utils import file_relative_path
from dagster.utils.error import SerializableErrorInfo
from dagster_cloud.agent.dagster_cloud_agent import (
    AGENT_HEARTBEAT_INTERVAL_SECONDS,
    CHECK_WORKSPACE_INTERVAL_SECONDS,
    DagsterCloudAgent,
    upload_api_response,
)
from dagster_cloud.api.dagster_cloud_api import (
    DagsterCloudApi,
    DagsterCloudApiGrpcResponse,
    DagsterCloudApiSuccess,
    DagsterCloudApiUnknownCommandResponse,
    DagsterCloudUploadApiResponse,
    LaunchRunArgs,
    TerminateRunArgs,
)
from dagster_cloud.execution.watchful_run_launcher.process import PID_TAG
from dagster_cloud.version import __version__ as DAGSTER_CLOUD_VERSION
from dagster_cloud.workspace.origin import CodeDeploymentMetadata
from ursula.agent_details import AgentDetails, AgentStatus
from ursula.storage.host_cloud.cloud_storage.schema import (
    RepositoryLocationsDataTable,
    RepositoryLocationsTable,
)
from ursula.user_code.workspace import dagster_cloud_api_call, gen_dagster_cloud_api_call

FAKE_AGENT_UUID = "FAKE_UUID"


def _add_location(cloud_storage, location_name="location"):
    cloud_storage.add_location(
        location_name,
        deployment_metadata=CodeDeploymentMetadata(python_file=__file__),
    )

    return RegisteredRepositoryLocationOrigin(location_name)


@pytest.fixture(name="stop_time")
def stop_time_fixture(monkeypatch):
    curr_time = pendulum.now()

    def fake_sleep(s):
        pendulum.set_test_now(pendulum.now().add(seconds=s))

    with pendulum.test(curr_time):
        monkeypatch.setattr(time, "sleep", fake_sleep)
        yield


@pytest.fixture(name="agent")
def agent_fixture(
    # Depends on cloud storage to ensure that we wait to delete the cloud storage data
    # until the agent has finished running
    cloud_storage,  # pylint: disable=unused-argument
):
    with DagsterCloudAgent() as agent:
        yield agent


@pytest.fixture(name="user_code_launcher")
def user_code_launcher_fixture(agent_instance):
    user_code_launcher = agent_instance.user_code_launcher
    user_code_launcher.start()

    yield user_code_launcher


@pytest.fixture(name="agent_replicas_user_code_launcher")
def agent_replicas_user_code_launcher_fixture(agent_replicas_instance):
    user_code_launcher = agent_replicas_instance.user_code_launcher
    user_code_launcher.start()

    yield user_code_launcher


@pytest.fixture(name="cloud_storage")
def cloud_storage_fixture(host_instance):
    cloud_storage = host_instance.cloud_storage

    yield cloud_storage

    with cloud_storage.transaction() as conn:
        conn.execute(RepositoryLocationsDataTable.delete())
        conn.execute(RepositoryLocationsTable.delete())


@pytest.fixture(name="user_cloud_agent_request_storage")
def user_agent_request_storage_fixture(host_instance):
    user_cloud_agent_request_storage = host_instance.user_cloud_agent_request_storage

    yield user_cloud_agent_request_storage

    user_cloud_agent_request_storage.wipe()


@pytest.fixture(name="repository_location")
def repository_location_fixture(agent, agent_instance, user_code_launcher, cloud_storage):
    repository_location_origin = _add_location(cloud_storage)

    _run_initial_reconcilation(agent, agent_instance, user_code_launcher)

    endpoint = user_code_launcher.get_grpc_endpoint(repository_location_origin)

    with GrpcServerRepositoryLocation(
        origin=repository_location_origin,
        server_id=endpoint.server_id,
        port=endpoint.port,
        socket=endpoint.socket,
        host=endpoint.host,
        heartbeat=True,
        watch_server=False,
    ) as location:
        yield location


@pytest.fixture(name="repository_location_agent_replicas")
def repository_location_agent_replicas_fixture(
    agent, agent_replicas_instance, agent_replicas_user_code_launcher, cloud_storage
):
    repository_location_origin = _add_location(cloud_storage)

    _run_initial_reconcilation(agent, agent_replicas_instance, agent_replicas_user_code_launcher)

    endpoint = agent_replicas_user_code_launcher.get_grpc_endpoint(repository_location_origin)

    with GrpcServerRepositoryLocation(
        origin=repository_location_origin,
        server_id=endpoint.server_id,
        port=endpoint.port,
        socket=endpoint.socket,
        host=endpoint.host,
        heartbeat=True,
        watch_server=False,
    ) as location:
        yield location


@op
def success():
    time.sleep(1)


@graph
def success_graph():
    success()


@op
def sleepy_op():
    start_time = time.time()
    while True:
        time.sleep(1)
        if time.time() - start_time > 120:
            raise Exception("Timed out")


@graph
def sleepy_graph():
    sleepy_op()


@daily_schedule(
    name="daily_success_job", pipeline_name="success_job", start_date=datetime.datetime(2020, 1, 1)
)
def daily_success_job(_):
    return {}


@sensor(name="success_job_sensor", pipeline_name="success_job")
def success_job_sensor():
    yield RunRequest(run_key=None)


success_job = success_graph.to_job(name="success_job", executor_def=in_process_executor)
sleepy_job = sleepy_graph.to_job(name="sleepy_job", executor_def=in_process_executor)


@repository
def repo():
    return [success_job, daily_success_job, success_job_sensor, sleepy_job]


def _assert_responses_for_requests(
    gen_responses,
    num_requests,
    response_type=(DagsterCloudApiGrpcResponse, DagsterCloudApiSuccess),
):
    assert len(gen_responses) == num_requests

    for gen_response in gen_responses:
        response = next(gen_response)
        print(response)
        assert isinstance(response, response_type)

        assert response.thread_telemetry


def _run_to_request_completion(agent, agent_instance, user_code_launcher):
    assert user_code_launcher.is_workspace_ready

    # Submit requests to thread pool
    next(agent.run_iteration(agent_instance, user_code_launcher))

    # Wait for all futures to return before processing
    futures = [
        future_context.future for future_context in agent.request_ids_to_future_context.values()
    ]
    _done, not_done = concurrent.futures.wait(futures, timeout=60)
    if not_done:
        raise Exception("Futures did not finish after 60 seconds: " + str(not_done))

    # Process all finished requests
    next(agent.run_iteration(agent_instance, user_code_launcher))

    # Assert that dictionary of future contexts is empty
    assert not agent.request_ids_to_future_context


def _run_initial_reconcilation(agent, agent_instance, user_code_launcher):
    # pulls initial locations from graphql and tells the user code launcher to asynchronously
    # reconcile them
    agent._check_update_workspace(  # pylint: disable=protected-access
        agent_instance, user_code_launcher
    )

    agent._check_add_heartbeat(  # pylint: disable=protected-access
        agent_instance, FAKE_AGENT_UUID, AGENT_HEARTBEAT_INTERVAL_SECONDS
    )

    # trigger the reconiliation
    user_code_launcher.reconcile()


def test_initial_reconcilation_populates_servers(
    agent,
    agent_instance,
    user_code_launcher,
    cloud_storage,
):
    repository_location_origin = _add_location(cloud_storage, location_name="location1")

    with pytest.raises(Exception):
        user_code_launcher.get_grpc_endpoint(repository_location_origin)

    _run_initial_reconcilation(agent, agent_instance, user_code_launcher)

    assert user_code_launcher.get_grpc_endpoint(repository_location_origin)

    # Does not automatically upload data
    location_entry = cloud_storage.get_workspace_location_entry("location1")
    assert not location_entry.load_error
    assert not location_entry.repository_location


def test_agent_metadata(
    agent,
    agent_instance,
    user_code_launcher,
    host_instance,
):
    _run_initial_reconcilation(agent, agent_instance, user_code_launcher)

    agent_details: List[AgentDetails] = host_instance.get_all_agent_details()
    assert len(agent_details) == 1
    assert agent_details[0].status == AgentStatus.RUNNING
    assert agent_details[0].agent_id == FAKE_AGENT_UUID
    assert agent_details[0].metadata.get("type") == "ProcessUserCodeLauncher"
    assert agent_details[0].metadata.get("version") == DAGSTER_CLOUD_VERSION


def test_agent_automatically_syncs(
    agent,
    agent_instance,
    user_code_launcher,
    cloud_storage,
    stop_time,  # pylint:disable=unused-argument
):
    repository_location_origin_one = _add_location(cloud_storage, location_name="location1")

    _run_initial_reconcilation(agent, agent_instance, user_code_launcher)

    repository_location_origin_two = _add_location(cloud_storage, location_name="location2")

    list(agent.run_iteration(agent_instance, user_code_launcher))
    agent._check_update_workspace(  # pylint: disable=protected-access
        agent_instance, user_code_launcher
    )

    user_code_launcher.reconcile()

    assert user_code_launcher.get_grpc_endpoint(repository_location_origin_one)

    with pytest.raises(Exception):
        user_code_launcher.get_grpc_endpoint(repository_location_origin_two)

    time.sleep(CHECK_WORKSPACE_INTERVAL_SECONDS)

    agent._check_update_workspace(  # pylint: disable=protected-access
        agent_instance, user_code_launcher
    )
    user_code_launcher.reconcile()

    assert user_code_launcher.get_grpc_endpoint(repository_location_origin_two)


def test_autosync_while_checking_for_workspace_updates(
    agent,
    agent_instance,
    user_code_launcher,
    cloud_storage,
    host_instance,
    stop_time,  # pylint: disable=unused-argument
):
    # Verify that if a reconciliation happens right after a CHECK_FOR_WORKSPACE_UPDATE
    # call (to write outdated data back to Dagit), the write still happens

    _run_initial_reconcilation(agent, agent_instance, user_code_launcher)

    repository_location_origin_one = _add_location(cloud_storage, location_name="location1")

    assert not cloud_storage.get_workspace_location_entry("location1").repository_location

    dagster_cloud_api_call(
        host_instance,
        DagsterCloudApi.CHECK_FOR_WORKSPACE_UPDATES,
        wait_for_response=False,
    )
    _run_to_request_completion(agent, agent_instance, user_code_launcher)

    time.sleep(CHECK_WORKSPACE_INTERVAL_SECONDS)

    # agent also polls for an update, gets one
    agent._check_update_workspace(  # pylint: disable=protected-access
        agent_instance, user_code_launcher
    )

    # next reconcilation should still result in the upload triggered by the
    # CHECK_FOR_WORKSPACE_UPDATES call form dagit
    user_code_launcher.reconcile()

    assert user_code_launcher.get_grpc_endpoint(repository_location_origin_one)
    assert cloud_storage.get_workspace_location_entry("location1").repository_location


@pytest.mark.parametrize("num_requests", [1, 10])
def test_check_for_workspace_updates(
    agent,
    user_code_launcher,
    agent_instance,
    cloud_storage,
    host_instance,
    num_requests,
):
    repository_location_origin_one = _add_location(cloud_storage, location_name="location1")

    _run_initial_reconcilation(agent, agent_instance, user_code_launcher)

    repository_location_origin_two = _add_location(cloud_storage, location_name="location2")

    gen_responses = []
    for _ in range(num_requests):
        gen_response = gen_dagster_cloud_api_call(
            host_instance,
            DagsterCloudApi.CHECK_FOR_WORKSPACE_UPDATES,
        )
        next(gen_response)

        gen_responses.append(gen_response)

    _run_to_request_completion(agent, agent_instance, user_code_launcher)

    user_code_launcher.reconcile()

    assert user_code_launcher.get_grpc_endpoint(repository_location_origin_one)

    # Also uploads data to cloud for both locations (one already reconciled, one not)
    assert cloud_storage.get_workspace_location_entry("location1").repository_location

    assert user_code_launcher.get_grpc_endpoint(repository_location_origin_two)
    assert cloud_storage.get_workspace_location_entry("location2").repository_location

    _assert_responses_for_requests(gen_responses, num_requests)


@pytest.mark.parametrize("num_requests", [1, 10])
def test_get_external_execution_plan(
    agent,
    agent_instance,
    user_code_launcher,
    host_instance,
    repository_location,
    num_requests,
):

    _run_initial_reconcilation(agent, agent_instance, user_code_launcher)

    external_pipeline = repository_location.get_repository("repo").get_full_external_pipeline(
        "success_job"
    )

    gen_responses = []
    for _ in range(num_requests):
        gen_response = gen_dagster_cloud_api_call(
            host_instance,
            DagsterCloudApi.GET_EXTERNAL_EXECUTION_PLAN,
            ExecutionPlanSnapshotArgs(
                pipeline_origin=external_pipeline.get_external_origin(),
                solid_selection=external_pipeline.solid_selection,
                run_config={},
                mode="default",
                step_keys_to_execute=None,
                pipeline_snapshot_id=external_pipeline.identifying_pipeline_snapshot_id,
                known_state=None,
            ),
        )
        next(gen_response)

        gen_responses.append(gen_response)

    _run_to_request_completion(agent, agent_instance, user_code_launcher)

    _assert_responses_for_requests(gen_responses, num_requests)


@pytest.mark.parametrize("num_requests", [1, 10])
def test_get_subset_external_pipeline_result(
    agent,
    agent_instance,
    user_code_launcher,
    host_instance,
    repository_location,
    num_requests,
):

    _run_initial_reconcilation(agent, agent_instance, user_code_launcher)

    external_pipeline = repository_location.get_repository("repo").get_full_external_pipeline(
        "success_job"
    )

    gen_responses = []
    for _ in range(num_requests):
        gen_response = gen_dagster_cloud_api_call(
            host_instance,
            DagsterCloudApi.GET_SUBSET_EXTERNAL_PIPELINE_RESULT,
            PipelineSubsetSnapshotArgs(
                pipeline_origin=external_pipeline.get_external_origin(),
                solid_selection=None,
            ),
        )
        next(gen_response)
        gen_responses.append(gen_response)

    _run_to_request_completion(agent, agent_instance, user_code_launcher)

    _assert_responses_for_requests(gen_responses, num_requests)


@pytest.mark.parametrize("num_requests", [1, 10])
def test_get_external_partition_config(
    agent,
    agent_instance,
    user_code_launcher,
    host_instance,
    repository_location,
    num_requests,
):

    _run_initial_reconcilation(agent, agent_instance, user_code_launcher)

    external_repository = repository_location.get_repository("repo")

    gen_responses = []
    for _ in range(num_requests):
        gen_response = gen_dagster_cloud_api_call(
            host_instance,
            DagsterCloudApi.GET_EXTERNAL_PARTITION_CONFIG,
            PartitionArgs(
                repository_origin=external_repository.get_external_origin(),
                partition_set_name="daily_success_job_partitions",
                partition_name="2020-01-01",
            ),
        )
        next(gen_response)

        gen_responses.append(gen_response)

    _run_to_request_completion(agent, agent_instance, user_code_launcher)

    _assert_responses_for_requests(gen_responses, num_requests)


@pytest.mark.parametrize("num_requests", [1, 10])
def test_get_external_partition_tags(
    agent,
    agent_instance,
    user_code_launcher,
    host_instance,
    repository_location,
    num_requests,
):
    _run_initial_reconcilation(agent, agent_instance, user_code_launcher)

    external_repository = repository_location.get_repository("repo")

    gen_responses = []
    for _ in range(num_requests):
        gen_response = gen_dagster_cloud_api_call(
            host_instance,
            DagsterCloudApi.GET_EXTERNAL_PARTITION_TAGS,
            PartitionArgs(
                repository_origin=external_repository.get_external_origin(),
                partition_set_name="daily_success_job_partitions",
                partition_name="2020-01-01",
            ),
        )
        next(gen_response)

        gen_responses.append(gen_response)

    _run_to_request_completion(agent, agent_instance, user_code_launcher)

    _assert_responses_for_requests(gen_responses, num_requests)


@pytest.mark.parametrize("num_requests", [1, 10])
def test_get_external_partition_names(
    agent,
    agent_instance,
    user_code_launcher,
    host_instance,
    repository_location,
    num_requests,
):
    _run_initial_reconcilation(agent, agent_instance, user_code_launcher)

    external_repository = repository_location.get_repository("repo")

    gen_responses = []
    for _ in range(num_requests):
        gen_response = gen_dagster_cloud_api_call(
            host_instance,
            DagsterCloudApi.GET_EXTERNAL_PARTITION_NAMES,
            PartitionNamesArgs(
                repository_origin=external_repository.get_external_origin(),
                partition_set_name="daily_success_job_partitions",
            ),
        )
        next(gen_response)

        gen_responses.append(gen_response)

    _run_to_request_completion(agent, agent_instance, user_code_launcher)

    _assert_responses_for_requests(gen_responses, num_requests)


@pytest.mark.parametrize("num_requests", [1, 10])
def test_get_external_partition_set_execution_param_data(
    agent,
    agent_instance,
    user_code_launcher,
    host_instance,
    repository_location,
    num_requests,
):
    _run_initial_reconcilation(agent, agent_instance, user_code_launcher)

    external_repository = repository_location.get_repository("repo")

    gen_responses = []
    for _ in range(num_requests):
        gen_response = gen_dagster_cloud_api_call(
            host_instance,
            DagsterCloudApi.GET_EXTERNAL_PARTITION_SET_EXECUTION_PARAM_DATA,
            PartitionSetExecutionParamArgs(
                repository_origin=external_repository.get_external_origin(),
                partition_set_name="daily_success_job_partitions",
                partition_names=["2020-01-01"],
            ),
        )
        next(gen_response)

        gen_responses.append(gen_response)

    _run_to_request_completion(agent, agent_instance, user_code_launcher)

    _assert_responses_for_requests(gen_responses, num_requests)


@pytest.mark.parametrize("num_requests", [1, 10])
def test_get_external_schedule_execution_data(
    agent,
    agent_instance,
    user_code_launcher,
    host_instance,
    repository_location,
    num_requests,
):
    _run_initial_reconcilation(agent, agent_instance, user_code_launcher)

    external_repository = repository_location.get_repository("repo")

    gen_responses = []
    for _ in range(num_requests):
        gen_response = gen_dagster_cloud_api_call(
            host_instance,
            DagsterCloudApi.GET_EXTERNAL_SCHEDULE_EXECUTION_DATA,
            ExternalScheduleExecutionArgs(
                repository_origin=external_repository.get_external_origin(),
                instance_ref=agent_instance.get_ref(),
                schedule_name="daily_success_job",
            ),
        )
        next(gen_response)

        gen_responses.append(gen_response)

    _run_to_request_completion(agent, agent_instance, user_code_launcher)

    _assert_responses_for_requests(gen_responses, num_requests)


@pytest.mark.parametrize("num_requests", [1, 10])
def test_get_external_sensor_execution_data(
    agent,
    agent_instance,
    user_code_launcher,
    host_instance,
    repository_location,
    num_requests,
):
    _run_initial_reconcilation(agent, agent_instance, user_code_launcher)

    external_repository = repository_location.get_repository("repo")

    gen_responses = []
    for _ in range(num_requests):
        gen_response = gen_dagster_cloud_api_call(
            host_instance,
            DagsterCloudApi.GET_EXTERNAL_SENSOR_EXECUTION_DATA,
            SensorExecutionArgs(
                repository_origin=external_repository.get_external_origin(),
                instance_ref=agent_instance.get_ref(),
                sensor_name="success_job_sensor",
                last_completion_time=None,
                last_run_key=None,
                cursor=None,
            ),
        )

        next(gen_response)

        gen_responses.append(gen_response)

    _run_to_request_completion(agent, agent_instance, user_code_launcher)

    _assert_responses_for_requests(gen_responses, num_requests)


def _wait_for_run_process(host_instance, run_id):
    # Ensure that the pid used to launch this run has termianted
    run = host_instance.get_run_by_id(run_id)
    pid = int(run.tags[PID_TAG])
    start_time = time.time()
    while True:
        if time.time() - start_time > 60:
            raise Exception("Timed out waiting for process to finish")

        print(f"Waiting for process {str(pid)} to finish")
        try:
            os.kill(pid, 0)
        except OSError:
            # Error indicates the process has finished
            return

        time.sleep(1)


@pytest.mark.parametrize("num_requests", [1, 10])
def test_get_external_notebook_data(
    agent,
    agent_instance,
    user_code_launcher,
    host_instance,
    repository_location,
    num_requests,
):
    _run_initial_reconcilation(agent, agent_instance, user_code_launcher)

    gen_responses = []
    for _ in range(num_requests):
        gen_response = gen_dagster_cloud_api_call(
            host_instance,
            DagsterCloudApi.GET_EXTERNAL_NOTEBOOK_DATA,
            NotebookPathArgs(
                repository_location_origin=repository_location.origin,
                notebook_path=file_relative_path(__file__, "foo.ipynb"),
            ),
        )
        next(gen_response)

        gen_responses.append(gen_response)

    _run_to_request_completion(agent, agent_instance, user_code_launcher)

    _assert_responses_for_requests(gen_responses, num_requests)


@pytest.mark.parametrize(
    "num_requests",
    [
        1,
        pytest.param(
            5,
            marks=pytest.mark.xfail(
                reason="https://linear.app/elementl/issue/COM-424/dagster-cloud-agent-launch-run-test-is-flaky"
            ),
        ),
    ],
)
def test_launch_run(
    agent,
    agent_instance,
    user_code_launcher,
    host_instance,
    repository_location,
    num_requests,
):
    _run_initial_reconcilation(agent, agent_instance, user_code_launcher)

    external_pipeline = repository_location.get_repository("repo").get_full_external_pipeline(
        "success_job"
    )

    runs = {}

    gen_responses = []
    for _ in range(num_requests):

        pipeline_run = host_instance.create_run_for_pipeline(
            pipeline_def=success_job,
            external_pipeline_origin=external_pipeline.get_external_origin(),
            pipeline_code_origin=external_pipeline.get_python_origin(),
        )
        runs[pipeline_run.run_id] = pipeline_run
        gen_response = gen_dagster_cloud_api_call(
            host_instance,
            DagsterCloudApi.LAUNCH_RUN,
            LaunchRunArgs(pipeline_run=pipeline_run),
        )
        next(gen_response)

        gen_responses.append(gen_response)

    _run_to_request_completion(agent, agent_instance, user_code_launcher)

    _assert_responses_for_requests(gen_responses, num_requests)

    for run_id in runs:
        poll_for_finished_run(host_instance, run_id)
        _wait_for_run_process(host_instance, run_id)


@pytest.mark.parametrize("num_requests", [1, 10])
def test_terminate_run(
    agent,
    agent_instance,
    user_code_launcher,
    host_instance,
    repository_location,
    num_requests,
):
    _run_initial_reconcilation(agent, agent_instance, user_code_launcher)

    external_pipeline = repository_location.get_repository("repo").get_full_external_pipeline(
        "sleepy_job"
    )

    launcher = user_code_launcher.run_launcher()

    runs = {}

    for _ in range(num_requests):

        pipeline_run = host_instance.create_run_for_pipeline(
            pipeline_def=sleepy_job,
            external_pipeline_origin=external_pipeline.get_external_origin(),
            pipeline_code_origin=external_pipeline.get_python_origin(),
        )
        runs[pipeline_run.run_id] = pipeline_run

        launcher.launch_run(LaunchRunContext(pipeline_run=pipeline_run, workspace=None))

    for run_id in runs:
        poll_for_step_start(host_instance, run_id)

    gen_responses = []
    for run_id in runs:
        pipeline_run = runs[run_id]
        gen_response = gen_dagster_cloud_api_call(
            host_instance,
            DagsterCloudApi.TERMINATE_RUN,
            TerminateRunArgs(pipeline_run=pipeline_run),
        )
        next(gen_response)

        gen_responses.append(gen_response)

    _run_to_request_completion(agent, agent_instance, user_code_launcher)

    _assert_responses_for_requests(gen_responses, num_requests)

    for run_id in runs:
        poll_for_finished_run(host_instance, run_id)
        _wait_for_run_process(host_instance, run_id)


@pytest.mark.parametrize("num_requests", [1, 10])
def test_terminate_run_agent_replicas(
    agent,
    agent_replicas_instance,
    agent_replicas_user_code_launcher,
    host_instance,
    repository_location_agent_replicas,
    num_requests,
):
    _run_initial_reconcilation(agent, agent_replicas_instance, agent_replicas_user_code_launcher)

    external_pipeline = repository_location_agent_replicas.get_repository(
        "repo"
    ).get_full_external_pipeline("sleepy_job")

    launcher = agent_replicas_user_code_launcher.run_launcher()

    runs = {}

    for _ in range(num_requests):

        pipeline_run = host_instance.create_run_for_pipeline(
            pipeline_def=sleepy_job,
            external_pipeline_origin=external_pipeline.get_external_origin(),
            pipeline_code_origin=external_pipeline.get_python_origin(),
        )
        runs[pipeline_run.run_id] = pipeline_run

        launcher.launch_run(LaunchRunContext(pipeline_run=pipeline_run, workspace=None))

    for run_id in runs:
        poll_for_step_start(host_instance, run_id)

    gen_responses = []
    for run_id in runs:
        pipeline_run = runs[run_id]
        gen_response = gen_dagster_cloud_api_call(
            host_instance,
            DagsterCloudApi.TERMINATE_RUN,
            TerminateRunArgs(pipeline_run=pipeline_run),
        )
        next(gen_response)

        gen_responses.append(gen_response)

    start_time = time.time()
    while not agent_replicas_user_code_launcher.is_workspace_ready:
        if time.time() - start_time > 30:
            raise Exception("Timed out waiting for workspace to be ready")
        time.sleep(1)

    _run_to_request_completion(agent, agent_replicas_instance, agent_replicas_user_code_launcher)

    _assert_responses_for_requests(gen_responses, num_requests)

    for run_id in runs:
        poll_for_finished_run(host_instance, run_id)
        _wait_for_run_process(host_instance, run_id)


@pytest.mark.parametrize("exception", [concurrent.futures.TimeoutError(), Exception("Failure")])
def test_future_exception(
    agent,
    agent_instance,
    user_code_launcher,
    host_instance,
    repository_location,
    monkeypatch,
    exception,
):
    _run_initial_reconcilation(agent, agent_instance, user_code_launcher)

    external_pipeline = repository_location.get_repository("repo").get_full_external_pipeline(
        "success_job"
    )

    original_submit = agent.executor.submit

    def submit(*args, **kwargs):
        future = original_submit(*args, **kwargs)
        future.set_exception(exception)

        return future

    monkeypatch.setattr(agent.executor, "submit", submit)

    dagster_cloud_api_call(
        host_instance,
        DagsterCloudApi.GET_EXTERNAL_EXECUTION_PLAN,
        ExecutionPlanSnapshotArgs(
            pipeline_origin=external_pipeline.get_external_origin(),
            solid_selection=external_pipeline.solid_selection,
            run_config={},
            mode="default",
            step_keys_to_execute=None,
            pipeline_snapshot_id=external_pipeline.identifying_pipeline_snapshot_id,
            known_state=None,
        ),
        wait_for_response=False,
    )

    result = next(agent.run_iteration(agent_instance, user_code_launcher))

    assert isinstance(result, SerializableErrorInfo)
    assert result.cls_name == exception.__class__.__name__

    # loop recovers
    result = next(agent.run_iteration(agent_instance, user_code_launcher))
    assert not result


def test_unknown_api(
    agent,
    agent_instance,
    user_code_launcher,
    user_cloud_agent_request_storage,
):
    _run_initial_reconcilation(agent, agent_instance, user_code_launcher)

    agent._process_api_request(  # pylint: disable=protected-access
        {"requestId": "foobar", "requestApi": "DO_THE_HOKEY_POKEY", "requestBody": ""},
        agent_instance,
        user_code_launcher,
        pendulum.now("UTC").timestamp(),
    )

    serialized_response = user_cloud_agent_request_storage.get_response("foobar")
    response = deserialize_json_to_dagster_namedtuple(serialized_response)
    assert isinstance(response, DagsterCloudApiUnknownCommandResponse)
    assert response.thread_telemetry


def test_upload_api_response(
    agent,
    agent_instance,
    user_code_launcher,
    user_cloud_agent_request_storage,
):
    _run_initial_reconcilation(agent, agent_instance, user_code_launcher)

    response_body = DagsterCloudApiSuccess()

    upload_response = DagsterCloudUploadApiResponse(
        request_id="my_request", request_api="my_api", response=response_body
    )

    upload_api_response(agent_instance, upload_response)

    response = user_cloud_agent_request_storage.get_response("my_request")
    assert response == serialize_dagster_namedtuple(response_body)


def test_no_server_endpoint_unreachable(
    agent,
    agent_instance,
    user_code_launcher,
    host_instance,
):
    _run_initial_reconcilation(agent, agent_instance, user_code_launcher)

    invalid_repository_origin = ExternalRepositoryOrigin(
        repository_location_origin=RegisteredRepositoryLocationOrigin(
            location_name="missing_location",
        ),
        repository_name="fake_repo",
    )

    gen_api_call = gen_dagster_cloud_api_call(
        host_instance,
        DagsterCloudApi.GET_EXTERNAL_PARTITION_TAGS,
        PartitionArgs(
            repository_origin=invalid_repository_origin,
            partition_set_name="daily_success_job_partitions",
            partition_name="2020-01-01",
        ),
    )
    next(gen_api_call)

    _run_to_request_completion(agent, agent_instance, user_code_launcher)

    with pytest.raises(
        DagsterUserCodeUnreachableError,
        match="No server endpoint exists for location missing_location",
    ):
        next(gen_api_call)


def test_invalid_server_endpoint_unreachable(
    agent,
    agent_instance,
    user_code_launcher,
    host_instance,
):
    host_instance.cloud_storage.add_location(
        "bad_location",
        deployment_metadata=CodeDeploymentMetadata(
            python_file=__file__, image="images_do_not_work"
        ),
    )

    _run_initial_reconcilation(agent, agent_instance, user_code_launcher)

    bad_repository_origin = ExternalRepositoryOrigin(
        repository_location_origin=RegisteredRepositoryLocationOrigin(
            location_name="bad_location",
        ),
        repository_name="fake_repo",
    )

    gen_api_call = gen_dagster_cloud_api_call(
        host_instance,
        DagsterCloudApi.GET_EXTERNAL_PARTITION_TAGS,
        PartitionArgs(
            repository_origin=bad_repository_origin,
            partition_set_name="daily_success_job_partitions",
            partition_name="2020-01-01",
        ),
    )
    next(gen_api_call)

    _run_to_request_completion(agent, agent_instance, user_code_launcher)

    with pytest.raises(
        DagsterUserCodeUnreachableError,
        match="Failure loading server endpoint for location bad_location: Exception: Your agent's configuration cannot load locations that specify a Docker image",
    ):
        next(gen_api_call)


def test_timeout_unreachable(
    agent,
    agent_instance,
    user_code_launcher,
    host_instance,
):
    _run_initial_reconcilation(agent, agent_instance, user_code_launcher)

    with pytest.raises(
        DagsterUserCodeUnreachableError,
        match="Timed out waiting for response to request",
    ):
        dagster_cloud_api_call(
            host_instance,
            DagsterCloudApi.CHECK_FOR_WORKSPACE_UPDATES,
            timeout=1,
        )


def test_agent_not_running_unreachable(host_instance):
    host_instance.cloud_storage.wipe()
    host_instance.run_storage.wipe()
    with pytest.raises(
        DagsterUserCodeUnreachableError,
        match="Could not send request to agent since no agents have recently heartbeated",
    ):
        dagster_cloud_api_call(host_instance, DagsterCloudApi.CHECK_FOR_WORKSPACE_UPDATES)
