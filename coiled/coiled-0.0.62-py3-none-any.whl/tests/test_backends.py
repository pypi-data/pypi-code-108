"""
This is an initial set of backend tests.  It is a WIP since there are still
several structural issues:

    - currently we are using function scoping for fixtures because module
      scoping is causing some stuble DB breakage (possibly transactions
      happening in a callback are not visible elsehwere).
    - for some reason we are not able to get a client connection to the cluster
      (this might be a docker-compose/ports issue??)

"""

import asyncio
import os
import time
from distutils.util import strtobool
from typing import NamedTuple, Union

import coiled
import dask

# import dask.array as da
import pytest
from coiled.core import Async, Cloud
from dask.distributed import Client
from typing_extensions import Literal

from cloud.apps import CloudConfig
from users.models import Account, Membership, User, get_default_registry_data

pytestmark = [
    # Don't run these tests unless we specifically ask, because they
    # require an CLOUDBRIDGE cluster
    pytest.mark.skipif(
        not strtobool(os.environ.get("TEST_AGAINST_CLOUDBRIDGE", "n")),
        reason="skipping VM tests because TEST_AGAINST_CLOUDBRIDGE is False",
    ),
    # only run VM backend tests if "aws" flag is set -- note here "aws" actually
    # means ECS but these tests will run against VMs instead of ECS -- obviously
    # this should all be changed!
    pytest.mark.skipif(
        os.environ.get("TEST_BACKEND", "") == "in_process",
        reason="skipping VM because TEST_BACKEND == 'in_process'",
    ),
]


class UserOrgMembership(NamedTuple):
    user: User
    account: Account
    membership: Membership


PASSWORD = "mypassword"
ACCOUNT = "dhl"
SOFTWARE_NAME = "myenv42"

# This toggle lets use make the fixtures module or function scope
# Ideally we would use module scope so we have a re-usable cluster we can run
# several tests on but currently this is causing subtle database issues (we
# don't find the scheduler entry in the DB, possibly becuase of some kind of
# transction scoping).  so for now we stick to `function` scoping but hope to
# eventually move back to module-level scope.
# USE_SCOPE = "module"
USE_SCOPE: Union[Literal["module"], Literal["function"]] = "function"


@pytest.fixture(scope=USE_SCOPE)
@pytest.mark.asyncio
async def backends():
    """Provide the backends as a fixture, and ensure that the rest
    of the application uses it too (we don't need real AWS resources for these
    tests!)"""

    yield CloudConfig.enabled_backends


@pytest.fixture(
    scope=USE_SCOPE,
    params=[
        pytest.param(
            "vm_aws",
            marks=[
                pytest.mark.test_group("backend-vm-aws"),
            ],
        ),
        pytest.param(
            "vm_gcp",
            marks=[
                pytest.mark.test_group("backend-vm-gcp"),
            ],
        ),
    ],
)
def backend_name(request):
    yield request.param


if USE_SCOPE == "module":

    @pytest.fixture(scope="module")
    def module_dhl_account(
        django_db_setup,
        django_db_blocker,
        backend_name,
    ):
        with django_db_blocker.unblock():
            account = Account(
                slug="dhl",
                name="DHL",
                backend=backend_name,
                container_registry=get_default_registry_data(backend=backend_name),
            )
            account.save()
            yield account
            # not sure if we need this or if contextmanager does it??
            # django_db_blocker.restore()

    @pytest.fixture(scope="module")
    def module_jack_from_dhl(
        django_db_setup,
        django_db_blocker,
        backends,
        remote_access_url,
        dhl_account,
    ):
        with django_db_blocker.unblock():
            jack = User.objects.create(
                username="jack",
                email="jack@dhl.com",
            )
            jack.set_password(PASSWORD)
            jack.save()
            dhl_membership = Membership(user=jack, account=dhl_account)
            dhl_membership.save()
            with dask.config.set(
                {
                    "coiled": {
                        "user": f"{jack.username}",
                        "token": f"{jack.auth_token.key}",
                        "server": remote_access_url,
                        "account": "dhl",
                        "no-minimum-version-check": True,
                        # note: this breaks non-aws stuff
                        # "backend-options": {"region": "us-east-2"},
                    }
                }
            ):
                yield jack
            # django_db_blocker.restore()

    dhl_account = module_dhl_account
    jack_from_dhl = module_jack_from_dhl


else:

    @pytest.fixture(scope="function")
    @pytest.mark.django_db(transaction=True)
    def function_dhl_account(transactional_db, django_user_model, backend_name):
        account = Account(
            slug="dhl",
            name="DHL",
            backend=backend_name,
            container_registry=get_default_registry_data(backend=backend_name),
        )
        account.save()
        yield account

    @pytest.fixture(scope="function")
    def function_jack_from_dhl(
        django_user_model, backends, remote_access_url, dhl_account
    ):
        jack = django_user_model.objects.create(
            username="jack",
            email="jack@dhl.com",
        )
        jack.set_password(PASSWORD)
        jack.save()
        dhl_membership = Membership(user=jack, account=dhl_account)
        dhl_membership.save()
        with dask.config.set(
            {
                "coiled": {
                    "user": f"{jack.username}",
                    "token": f"{jack.auth_token.key}",
                    "server": remote_access_url,
                    "account": "dhl",
                    "no-minimum-version-check": True,
                    # note: this breaks non-aws stuff
                    # "backend-options": {"region": "us-east-2"},
                }
            }
        ):
            yield jack

    dhl_account = function_dhl_account
    jack_from_dhl = function_jack_from_dhl


@pytest.fixture(autouse=True)
def set_remote_url(settings, remote_access_url):
    settings.WEBAPP_SERVICE_URL = remote_access_url


@pytest.fixture(scope=USE_SCOPE)
# @pytest.mark.django_db(transaction=True)  # implied by `live_server`, but explicit
async def cloud(backends, jack_from_dhl):
    async with coiled.Cloud(account="dhl", asynchronous=True) as cloud:
        # Remove default software environments and cluster configurations
        default_envs = await cloud.list_software_environments()
        await asyncio.gather(
            *[
                cloud.delete_software_environment(name=name)
                for name, info in default_envs.items()
            ]
        )
        default_configs = await cloud.list_cluster_configurations()
        await asyncio.gather(
            *[
                cloud.delete_cluster_configuration(name=name)
                for name, info in default_configs.items()
            ]
        )

        yield cloud


@pytest.fixture(scope=USE_SCOPE)
async def cleanup(cloud):
    clusters = await cloud.list_clusters()
    await asyncio.gather(
        *[
            cloud.delete_cluster(cluster_id=cluster["id"])
            for cluster in clusters.values()
        ]
    )

    yield

    clusters = await cloud.list_clusters()
    await asyncio.gather(
        *[
            cloud.delete_cluster(cluster_id=cluster["id"])
            for cluster in clusters.values()
        ]
    )


@pytest.fixture(scope=USE_SCOPE)
async def software_env_daskdev(cloud):
    await cloud.create_software_environment(
        name=SOFTWARE_NAME, container="daskdev/dask:latest"
    )

    yield f"{ACCOUNT}/{SOFTWARE_NAME}"

    await cloud.delete_software_environment(name=SOFTWARE_NAME)


@pytest.fixture(scope=USE_SCOPE)
async def dhl_cluster_config(cloud, cleanup, dhl_account, software_env_daskdev):
    await cloud.create_cluster_configuration(
        name="dhl-config", software=software_env_daskdev
    )

    yield cloud


@pytest.fixture(scope=USE_SCOPE)
async def cluster_with_create_time(
    cloud: Cloud[Async], cleanup, dhl_cluster_config, jack_from_dhl
):
    create_time = time.time()
    cluster = await coiled.Cluster(
        name="dhl-cluster-1", account="dhl", configuration="dhl-config", cloud=cloud
    )
    yield cluster, create_time

    coiled.delete_cluster(name="dhl-cluster-1")


@pytest.mark.skip(
    "logs are still flaky :-( https://github.com/coiled/cloud/issues/2937"
)
@pytest.mark.asyncio
async def test_cluster_logs(
    cloud, cleanup, dhl_cluster_config, cluster_with_create_time
):
    """This is currently a large monolithic test.  We can try to break it up
    once we have figured out how to get module-scope fixtures (because
    launching a cluster for each function/test takes too long).
    """
    cluster, create_time = cluster_with_create_time
    async with Client(cluster, asynchronous=True) as client:
        await client.wait_for_workers(4, timeout=4 * 60)
    t0 = time.time()
    logs = dict()
    # logs may lag a bit so we give them some time to come up fully
    while time.time() - t0 < 120:
        logs = await cluster.logs()
        if len(logs) == 5 and "Starting established connection" in logs["Scheduler"]:
            break
        await asyncio.sleep(10)
    assert len(logs) == 5
    assert set(logs.keys()).union(
        set(worker["name"] for worker in cluster.scheduler_info["workers"].values())
    ) == set(logs.keys())
    assert "Starting established connection" in logs["Scheduler"]
