from contextlib import contextmanager

import pytest
from dagster.core.test_utils import instance_for_test
from dagster_postgres.utils import get_conn_string, wait_for_connection
from ursula.test_utils import make_live_graphql_client


@pytest.fixture(name="agent_instance")
def agent_instance_fixture(agent_token, ursula_graphql_client):  # pylint: disable=unused-argument
    with instance_for_test(
        {
            "instance_class": {
                "module": "dagster_cloud",
                "class": "DagsterCloudAgentInstance",
            },
            "user_code_launcher": {
                "module": "dagster_cloud.workspace.user_code_launcher",
                "class": "ProcessUserCodeLauncher",
            },
            "dagster_cloud_api": {
                "url": "http://localhost:2873",
                "agent_token": agent_token,
            },
            "compute_logs": {
                "module": "dagster.core.storage.noop_compute_log_manager",
                "class": "NoOpComputeLogManager",
            },
        }
    ) as instance:
        yield instance


@pytest.fixture(name="agent_replicas_instance")
def agent_replicas_instance_fixture(
    agent_token, ursula_graphql_client
):  # pylint: disable=unused-argument
    with instance_for_test(
        {
            "instance_class": {
                "module": "dagster_cloud",
                "class": "DagsterCloudAgentInstance",
            },
            "user_code_launcher": {
                "module": "dagster_cloud.workspace.user_code_launcher",
                "class": "ProcessUserCodeLauncher",
            },
            "dagster_cloud_api": {
                "url": "http://localhost:2873",
                "agent_token": agent_token,
            },
            "compute_logs": {
                "module": "dagster.core.storage.noop_compute_log_manager",
                "class": "NoOpComputeLogManager",
            },
            "agent_replicas": {"enabled": True},
        }
    ) as instance:
        yield instance


@pytest.fixture(name="host_storage_hostnames", scope="module")
def host_storage_hostnames_fixture(docker_compose_cm):
    with docker_compose_cm() as docker_compose:
        host_storage_hostnames = docker_compose
        postgres_hostname = host_storage_hostnames["postgres"]

        wait_for_connection(
            get_conn_string(
                username="test",
                password="test",
                hostname=postgres_hostname,
                db_name="test",
            ),
            retry_limit=10,
            retry_wait=3,
        )

        yield host_storage_hostnames


@pytest.fixture(name="host_instance", scope="module")
def host_instance_fixture(host_storage_hostnames, agent_token):
    with _create_host_instance(host_storage_hostnames) as instance:
        instance.wipe_db()
        assert instance.get_alembic_rev() is None

        instance.init_db()
        assert instance.get_alembic_rev() != None

        organization_id = instance.cloud_storage.create_organization("acme")
        instance.cloud_storage.create_deployment(organization_id, "sandbox")

        test_user = instance.cloud_storage.create_or_update_user(email="test@acme.com")

        instance.cloud_storage.create_agent_token(
            organization_id,
            test_user.user_id,
            token_value=agent_token,
        )

        instance.check_loaded()
        with instance.for_deployment("acme", "sandbox") as scoped_instance:
            yield scoped_instance
        instance.wipe_db()
        assert instance.get_alembic_rev() is None


@contextmanager
def _create_host_instance(
    host_storage_hostnames,
    set_dagster_home=True,
):
    postgres_hostname = host_storage_hostnames["postgres"]
    redis_hostname = host_storage_hostnames["redis"]
    postgres_config = {
        "postgres_db": {
            "hostname": postgres_hostname,
            "username": "test",
            "password": "test",
            "db_name": "test",
        },
    }
    instance_overrides = {
        "run_storage": {
            "module": "ursula.storage.host_cloud.run_storage",
            "class": "PostgresCloudRunStorage",
            "config": postgres_config,
        },
        "event_log_storage": {
            "module": "ursula.storage.host_cloud.event_log_storage",
            "class": "PostgresCloudEventLogStorage",
            "config": postgres_config,
        },
        "schedule_storage": {
            "module": "ursula.storage.host_cloud.schedule_storage",
            "class": "PostgresCloudScheduleStorage",
            "config": postgres_config,
        },
        "instance_class": {
            "module": "ursula.instance",
            "class": "UnscopedHostInstance",
            "config": {},
        },
        "cloud_storage": {
            "module": "ursula.storage.host_cloud.cloud_storage",
            "class": "PostgresCloudStorage",
            "config": postgres_config,
        },
        "code_preview_storage": {
            "module": "ursula.storage.host_cloud.code_preview_storage",
            "class": "PostgresCodePreviewStorage",
            "config": postgres_config,
        },
        "email_client": {
            "module": "ursula.daemon.monitoring.email.recording",
            "class": "RecordingSESEmailClient",
            "config": {},
        },
        "redis": {
            "host": redis_hostname,
        },
    }

    with instance_for_test(
        overrides=instance_overrides, set_dagster_home=set_dagster_home
    ) as instance:
        yield instance


@pytest.fixture(name="ursula_graphql_client", scope="module")
def ursula_graphql_client_fixture(agent_token, host_instance):  # pylint: disable=unused-argument
    yield from make_live_graphql_client(agent_token=agent_token)
