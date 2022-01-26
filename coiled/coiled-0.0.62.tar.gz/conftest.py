import asyncio
import json
import random
import shutil
import string
from os import environ
from typing import AsyncGenerator, NamedTuple

import coiled
import dask
import pytest
import structlog
import toolz
from coiled.core import Async, Cloud
from coiled.utils import run_command_in_subprocess
from distributed.utils_test import loop  # noqa: F401
from django.conf import settings
from django.utils import timezone

from api_tokens.models import ApiToken, generate_token
from backends.types import BackendChoices
from tiers.models import Program
from users.models import Account, Membership, User, get_default_registry_data

logger = structlog.get_logger(__name__)

HAS_BUILDAH = shutil.which("buildah") is not None

account_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))


class UserOrgMembership(NamedTuple):
    user: User
    account: Account
    membership: Membership


PASSWORD = "mypassword"
ACCOUNT = f"test-{account_suffix}"
CONFIGURATION = "myclusterconfig"
SOFTWARE_NAME = "myenv"


class MockResponse:
    def __init__(self, json_data, status):
        self.json_data = json_data
        self.response = asyncio.Future()
        self.response.set_result({"next": None, "results": json_data})
        self.status = status

    async def json(self):
        return {"next": None, "results": self.json_data}


@pytest.fixture()
# lets keep this a fixture so we can eventually support multiple backends in a
# single run via paramters
def backend_name(request):
    yield settings.DEFAULT_CLUSTER_BACKEND


def get_options(backend_name):
    if backend_name == "k8s":
        config_file_data = environ.get("K8S_TEST_KUBECONFIG_DATA", "")
        if not config_file_data:
            kubeconfig_file = environ["K8S_TEST_KUBECONFIG"]
            with open(kubeconfig_file, "r") as fl:
                config_file_data = fl.read()
        options = dict(
            config_file_data=config_file_data,
            namespace=environ.get("K8S_TEST_NAMESPACE", "coiled"),
        )
        return options
    return {}


@pytest.fixture
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


@pytest.fixture
async def docker_prune():
    MIN_DISK_SPACE = 15.0  # GiB
    # If the disk usage has dropped below MIN_DISK_SPACE GB, prune aggressively
    used = shutil.disk_usage("/").free / 1024 ** 3
    print(f"Current disk space available: {used} GB")
    if used < MIN_DISK_SPACE:
        print(f"Free disk space has dropped to {used} GB, pruning...")
        if HAS_BUILDAH:
            async for _ in run_command_in_subprocess("buildah rmi -a -f"):
                pass
        else:
            async for _ in run_command_in_subprocess(
                "docker rmi -f $(docker images -aq)"
            ):
                pass
        print(f"Free disk space now at {shutil.disk_usage('/').free/1024**3} GB")
    before = set()

    # Get a list of images before the test is run.
    if HAS_BUILDAH:
        images_json = ""
        async for line in run_command_in_subprocess("buildah images --json"):
            images_json += line
        for image_data in json.loads(images_json):
            before.add(image_data["id"])
    else:
        async for l in run_command_in_subprocess("docker images --format '{{json .}}'"):
            data = json.loads(l)
            before.add(data["ID"])

    print(f"Starting images: {before}")
    yield

    # Attempt to remove new images created during the test.
    after = set()
    if HAS_BUILDAH:
        images_json = ""
        async for line in run_command_in_subprocess("buildah images --json"):
            images_json += line
        for image_data in json.loads(images_json):
            after.add(image_data["id"])
    else:
        async for l in run_command_in_subprocess("docker images --format '{{json .}}'"):
            data = json.loads(l)
            after.add(data["ID"])
    print(f"Ending images: {after}")

    new_images = after - before
    if len(new_images) == 0:
        return

    print(f"New images to be removed: {new_images}")
    cmd = "buildah" if HAS_BUILDAH else "docker"
    try:
        async for _ in run_command_in_subprocess(
            f"{cmd} rmi -f {' '.join(new_images)}"
        ):
            pass
        print(f"Cleaned up images {new_images}")
    except ValueError as e:
        print(f"Failed to remove {new_images} with error {e}")

    # If the disk usage has dropped below MIN_DISK_SPACE GB, prune aggressively
    used = shutil.disk_usage("/").free / 1024 ** 3
    print(f"Current disk space available: {used} GB")
    if used < MIN_DISK_SPACE:
        print(f"Free disk space has dropped to {used} GB, pruning...")
        if HAS_BUILDAH:
            async for _ in run_command_in_subprocess("buildah rmi -a -f"):
                pass
        else:
            async for _ in run_command_in_subprocess(
                "docker rmi -f $(docker images -aq)"
            ):
                pass
        print(f"Free disk space now at {shutil.disk_usage('/').free/1024**3} GB")


@pytest.fixture(scope="function")
def container_registry_fixture():
    if settings.TEST_BACKEND == "in_process":
        return get_default_registry_data(BackendChoices.IN_PROCESS)
    # TODO will have to update this when we start testing multi-cloud
    return get_default_registry_data()


@pytest.fixture(scope="function")
def fedex_account(
    transactional_db, django_user_model, container_registry_fixture, backend_name
):
    account = Account(
        slug="fedex",
        name="FedEx",
        backend=backend_name,
        options=get_options(backend_name),
        container_registry=container_registry_fixture,
    )
    account.save()
    return account


@pytest.fixture(scope="function")
def base_user_object(
    transactional_db,
    django_user_model,
    remote_access_url,
    container_registry_fixture,
    backend_name,
):
    joined = timezone.datetime(2021, 11, 7, tzinfo=timezone.get_current_timezone())
    user = django_user_model.objects.create(
        username=ACCOUNT,
        email="myuser@users.com",
        date_joined=joined,
    )
    user.set_password(PASSWORD)
    user.save()
    return user


@pytest.fixture(scope="function")
def base_user_token(base_user_object):
    secret_value, token_hash = generate_token()
    token = ApiToken.objects.create(
        user=base_user_object,
        token_hash=token_hash,
    )
    token.save()
    token = token.get_token(secret_value)
    return token


@pytest.fixture(scope="function")
def base_user(
    transactional_db,
    remote_access_url,
    container_registry_fixture,
    backend_name,
    base_user_object,
    base_user_token,
):

    user = base_user_object
    membership = Membership.objects.filter(user=user).first()
    membership.account.container_registry = container_registry_fixture
    membership.account.backend = backend_name
    membership.account.options = get_options(backend_name)
    membership.account.save()

    user.auth_token.delete()

    with dask.config.set(
        {
            "coiled": {
                "user": f"{user.username}",
                "token": base_user_token,
                "server": remote_access_url,
                "account": ACCOUNT,
                "backend-options": {"region": "us-east-2"},
                "no-minimum-version-check": True,
            },
        }
    ):
        yield UserOrgMembership(user, membership.account, membership)


# fixture must be function-scoped because `transactional_db` is
@pytest.fixture(scope="function")
def sample_user(base_user, backend):
    yield base_user


@pytest.fixture(scope="function")
def disabled_free_tier_user(
    transactional_db,
    django_user_model,
    backend,
    remote_access_url,
    container_registry_fixture,
    backend_name,
):
    user = django_user_model.objects.create(
        username="kryptominer",
        email="kryptominer@users.com",
    )
    user.set_password(PASSWORD)
    user.save()
    account = Account.objects.create(
        name=f"{ACCOUNT}-kryptominer-inc",
        backend=backend_name,
        options=get_options(backend_name),
        container_registry=container_registry_fixture,
    )
    membership = Membership.objects.create(
        user=user, account=account, is_admin=True, limit=4
    )

    program = Program.get_active(account)  # should be free by default
    program.limit = 0
    program.save()

    with dask.config.set(
        {
            "coiled": {
                "user": f"{user.username}",
                "token": f"{user.auth_token.key}",
                "server": remote_access_url,
                "account": account.slug,
                "backend-options": {"region": "us-east-2"},
                "no-minimum-version-check": True,
            }
        }
    ):
        yield UserOrgMembership(user, membership.account, membership)


@pytest.fixture(scope="function")
def sample_user_token(base_user_token):
    """this is a duplicate of base_user_token, to match the name of sample_user
    (so that when we use it next to sample_user it's obvious to readers that this token corresponds to that user"""
    return base_user_token


@pytest.fixture()
def long_lived_token_for_sample_user(sample_user):
    secret_value, token_hash = generate_token()
    token = ApiToken.objects.create(
        user=sample_user.user,
        token_hash=token_hash,
    )
    token.save()
    return token.get_token(secret_value)


@pytest.fixture(scope="function")
def sample_gpu_user(transactional_db, django_user_model, backend, remote_access_url):
    user = django_user_model.objects.create(
        username="mygpuuser",
        email="myuser@gpuusers.com",
    )
    user.set_password(PASSWORD)
    user.save()
    membership = Membership.objects.filter(user=user).first()
    program = membership.account.active_program
    program.gpus_limit = 4
    program.save()

    with dask.config.set(
        {
            "coiled": {
                "user": f"{user.username}",
                "token": f"{user.auth_token.key}",
                "server": remote_access_url,
                "account": "myuser",
                "backend-options": {"region": "us-east-2"},
                "no-minimum-version-check": True,
            }
        }
    ):
        yield UserOrgMembership(user, membership.account, membership)


@pytest.fixture(scope="function")
def jess_from_fedex(
    transactional_db, django_user_model, backend, remote_access_url, fedex_account
):
    jess = django_user_model.objects.create(
        username="jess",
        email="jess@fedex.com",
    )
    jess.set_password(PASSWORD)
    jess.save()
    fedex_membership = Membership(user=jess, account=fedex_account)
    fedex_membership.save()
    with dask.config.set(
        {
            "coiled": {
                "user": f"{jess.username}",
                "token": f"{jess.auth_token.key}",
                "server": remote_access_url,
                "account": None,
                "backend-options": {"region": "us-east-2"},
                "no-minimum-version-check": True,
            }
        }
    ):
        yield jess


# fixture must be function-scoped because `transactional_db` is
@pytest.fixture(scope="function")
def second_user(
    transactional_db,
    django_user_model,
    backend,
    remote_access_url,
    container_registry_fixture,
    backend_name,
):
    user = django_user_model.objects.create(
        username="charlie",
        email="charlie@users.com",
    )
    user.set_password(PASSWORD)
    user.save()
    account = Account.objects.create(
        name="mycorp",
        backend=backend_name,
        options=get_options(backend_name),
        container_registry=container_registry_fixture,
    )
    membership = Membership.objects.create(
        user=user, account=account, is_admin=True, limit=4
    )
    with dask.config.set(
        {
            "coiled": {
                "user": f"{user.username}",
                "token": f"{user.auth_token.key}",
                "server": remote_access_url,
                "account": None,
                "backend-options": {"region": "us-east-2"},
                "no-minimum-version-check": True,
            }
        }
    ):
        yield UserOrgMembership(user, membership.account, membership)


# fixture must be function-scoped because `transactional_db` is
@pytest.fixture(scope="function")
def external_aws_account_user(
    transactional_db, django_user_model, backend, remote_access_url
):
    user = django_user_model.objects.create(
        username="externalaws",
        email="aws@users.com",
    )
    user.set_password(PASSWORD)
    user.save()

    account = Account.objects.get(slug=user.username)
    options = {
        "credentials": {
            "aws_secret_access_key": environ.get("TEST_AWS_SECRET_ACCESS_KEY", ""),
            "aws_access_key_id": environ.get("TEST_AWS_ACCESS_KEY_ID", ""),
        },
        "account_role": environ.get("TEST_AWS_IAM_ROLE", ""),  # Optional
    }
    account.options = options
    account.save()
    with dask.config.set(
        {
            "coiled": {
                "user": f"{user.username}",
                "token": f"{user.auth_token.key}",
                "server": remote_access_url,
                "account": user.username,
                "backend-options": {"region": "us-east-2"},
                "no-minimum-version-check": True,
            }
        }
    ):
        yield user


@pytest.fixture(scope="function")
def second_account(sample_user, container_registry_fixture, backend_name):
    account = Account.objects.create(
        name="OtherOrg",
        backend=backend_name,
        options=get_options(backend_name),
        container_registry=container_registry_fixture,
    )
    membership = Membership.objects.create(
        user=sample_user.user, account=account, is_admin=False, limit=2
    )
    sample_user.user.save()
    return UserOrgMembership(sample_user.user, account, membership)


@pytest.fixture(scope="function")
def account_with_options(sample_user, container_registry_fixture, backend_name):
    account = Account.objects.create(
        name="GotOptions",
        backend=backend_name,
        options=toolz.merge(get_options(backend_name), {"region": "us-west-1"}),
        container_registry=container_registry_fixture,
    )
    membership = Membership.objects.create(
        user=sample_user.user, account=account, is_admin=False, limit=2
    )
    sample_user.user.save()
    return UserOrgMembership(sample_user.user, account, membership)


@pytest.fixture(scope="function")
@pytest.mark.django_db(transaction=True)  # implied by `live_server`, but explicit
async def cloud(sample_user, backend) -> AsyncGenerator[Cloud[Async], None]:
    async with coiled.Cloud(account=ACCOUNT, asynchronous=True) as cloud:
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


@pytest.fixture(scope="function")
@pytest.mark.django_db(transaction=True)  # implied by `live_server`, but explicit
async def disabled_free_tier_cloud(
    disabled_free_tier_user, backend
) -> AsyncGenerator[Cloud[Async], None]:
    async with coiled.Cloud(
        account=disabled_free_tier_user.account.slug, asynchronous=True
    ) as cloud:
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


@pytest.fixture(scope="function")
@pytest.mark.django_db(transaction=True)  # implied by `live_server`, but explicit
async def cloud_with_gpu(sample_gpu_user):
    async with coiled.Cloud(
        account=sample_gpu_user.account.slug, asynchronous=True
    ) as cloud:
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


@pytest.fixture
async def cluster_configuration(cloud, software_env):
    await cloud.create_cluster_configuration(
        name=CONFIGURATION,
        software=software_env,
        worker_cpu=1,
        worker_memory="2 GiB",
        scheduler_cpu=1,
        scheduler_memory="2 GiB",
    )

    yield f"{ACCOUNT}/{CONFIGURATION}"

    await cloud.delete_cluster_configuration(name=CONFIGURATION)

    out = await cloud.list_cluster_configurations(account=ACCOUNT)
    assert CONFIGURATION not in out


@pytest.fixture
async def software_env(cloud):
    await cloud.create_software_environment(
        name=SOFTWARE_NAME, container="daskdev/dask:latest"
    )

    yield f"{ACCOUNT}/{SOFTWARE_NAME}"

    await cloud.delete_software_environment(name=SOFTWARE_NAME)


@pytest.fixture
async def cloud_with_account(cleanup, jess_from_fedex, fedex_account, software_env):
    async with coiled.Cloud(
        account="fedex",
        token=jess_from_fedex.auth_token.key,
        user="jess",
        asynchronous=True,
    ) as cloud:
        await cloud.create_cluster_configuration(
            name="fedex-config", software=software_env
        )

        yield cloud


@pytest.fixture(scope="function")
def account_with_env_variables(sample_user, container_registry_fixture, backend_name):
    account = Account.objects.create(
        name=f"GotEnvs-{account_suffix}",
        backend=backend_name,
        options=get_options(backend_name),
        environment_variables={"MY_TESTING_ENV": "env_variable"},
        container_registry=container_registry_fixture,
    )
    membership = Membership.objects.create(
        user=sample_user.user, account=account, is_admin=False, limit=20
    )
    sample_user.user.save()

    return UserOrgMembership(sample_user.user, account, membership)


@pytest.fixture
def api_instance_types_gcp():
    return {
        "t2d-standard-8": {
            "name": "t2d-standard-8",
            "cores": 8,
            "gpus": 0,
            "gpu_name": None,
            "memory": 32768,
            "backend_type": "vm_gcp",
        },
        "t2d-standard-60": {
            "name": "t2d-standard-60",
            "cores": 60,
            "gpus": 0,
            "gpu_name": None,
            "memory": 245760,
            "backend_type": "vm_gcp",
        },
        "t2d-standard-48": {
            "name": "t2d-standard-48",
            "cores": 48,
            "gpus": 0,
            "gpu_name": None,
            "memory": 196608,
            "backend_type": "vm_gcp",
        },
        "t2d-standard-4": {
            "name": "t2d-standard-4",
            "cores": 4,
            "gpus": 0,
            "gpu_name": None,
            "memory": 16384,
            "backend_type": "vm_gcp",
        },
        "t2d-standard-32": {
            "name": "t2d-standard-32",
            "cores": 32,
            "gpus": 0,
            "gpu_name": None,
            "memory": 131072,
            "backend_type": "vm_gcp",
        },
        "t2d-standard-2": {
            "name": "t2d-standard-2",
            "cores": 2,
            "gpus": 0,
            "gpu_name": None,
            "memory": 8192,
            "backend_type": "vm_gcp",
        },
        "t2d-standard-16": {
            "name": "t2d-standard-16",
            "cores": 16,
            "gpus": 0,
            "gpu_name": None,
            "memory": 65536,
            "backend_type": "vm_gcp",
        },
        "g1-small": {
            "name": "g1-small",
            "cores": 1,
            "gpus": 0,
            "gpu_name": None,
            "memory": 1740,
            "backend_type": "vm_gcp",
        },
        "f1-micro": {
            "name": "f1-micro",
            "cores": 1,
            "gpus": 0,
            "gpu_name": None,
            "memory": 614,
            "backend_type": "vm_gcp",
        },
    }
