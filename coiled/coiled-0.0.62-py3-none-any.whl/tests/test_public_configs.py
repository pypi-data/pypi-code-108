from typing import Tuple

import coiled
import pytest
from coiled.core import Async, Cloud
from coiled.utils import ParseIdentifierError
from distributed.utils_test import loop  # noqa: F401

pytestmark = pytest.mark.test_group("test_public_configs")


@pytest.fixture
async def three_clouds(
    cleanup, sample_user, jess_from_fedex, remote_access_url, settings, base_user_token
):
    """
    Return a tuple of three clouds, one for coiled, one for jess,
    and one for fedex. Each will have one environment and one configuration
    """
    # coiled is not a member of FedEx
    coiled_user = sample_user.user
    jess = jess_from_fedex

    async with coiled.Cloud(
        user=coiled_user.username,
        token=base_user_token,
        asynchronous=True,
    ) as my_cloud:
        async with coiled.Cloud(
            user=jess.username,
            token=jess.auth_token.key,
            asynchronous=True,
        ) as jesss_cloud:
            async with coiled.Cloud(
                user=jess.username,
                token=jess.auth_token.key,
                account="fedex",
                asynchronous=True,
            ) as fedex_cloud:
                await my_cloud.create_software_environment(
                    name="env1", container="daskdev/dask:latest"
                )
                await jesss_cloud.create_software_environment(
                    name="env1", container="daskdev/dask:latest"
                )
                await fedex_cloud.create_software_environment(
                    name="fedex/env1", container="daskdev/dask:latest"
                )

                await my_cloud.create_cluster_configuration(
                    name="conf1", software="env1"
                )
                await jesss_cloud.create_cluster_configuration(
                    name="conf1", software="env1"
                )
                await fedex_cloud.create_cluster_configuration(
                    name="conf1", software="env1"
                )
                yield my_cloud, jesss_cloud, fedex_cloud


@pytest.mark.asyncio
async def test_list_configs_and_envs_only_show_your_accounts_stuff(three_clouds):
    for cloud in three_clouds:
        envs = await cloud.list_software_environments()
        configs = await cloud.list_cluster_configurations()
        for env, config in zip(envs.values(), configs.values()):
            assert env["account"] == cloud.default_account
            assert config["account"] == cloud.default_account


@pytest.mark.asyncio
async def test_creating_with_nonexistent_config_gives_informative_error(
    sample_user, cloud, software_env
):
    with pytest.raises(ValueError) as error_info:
        async with coiled.Cluster(configuration="bad-config", asynchronous=True):
            pass

    error_msg = str(error_info.value)
    assert "bad-config" in error_msg
    assert "not found" in error_msg

    # Trying to use software environment name as a cluster configuration
    with pytest.raises(ValueError) as error_info:
        async with coiled.Cluster(configuration=software_env, asynchronous=True):
            pass

    error_msg = str(error_info.value)
    assert "create_cluster_configuration" in error_msg
    assert f"software='{sample_user.account.name}/myenv'" in error_msg


@pytest.mark.asyncio
async def test_creating_with_bad_name_gives_informative_error(three_clouds):
    my_cloud, _, _ = three_clouds
    with pytest.raises(ParseIdentifierError) as error_info:
        await my_cloud.create_software_environment(
            name="extra/slash/nogood", container="daskdev/dask:latest"
        )
    assert error_info.value.args[0].startswith("Invalid name")
    with pytest.raises(ParseIdentifierError) as error_info:
        await my_cloud.create_cluster_configuration(
            name="extra/slash/?nogood", software="env1"
        )
    assert error_info.value.args[0].startswith("Invalid name")


@pytest.mark.asyncio
async def test_can_create_config_using_foreign_environment(sample_user, three_clouds):
    my_cloud, jesss_cloud, _ = three_clouds
    await jesss_cloud.create_cluster_configuration(
        name="awesome_config", software=f"{sample_user.account.name}/env1"
    )

    configs = await jesss_cloud.list_cluster_configurations()
    c = configs["jess/awesome_config"]
    assert c["account"] == "jess"
    assert c["scheduler"]["software"] == f"{sample_user.account.name}/env1"
    assert c["worker"]["software"] == f"{sample_user.account.name}/env1"


@pytest.mark.asyncio
async def test_can_create_software_environment_using_full_name_or_short_name(
    three_clouds,
):
    _, _, fedex = three_clouds

    # First with fully qualified name
    await fedex.create_software_environment(
        name="fedex/goodstuff", container="daskdev/dask:latest"
    )
    configs = await fedex.list_software_environments()
    e = configs["fedex/goodstuff"]
    assert e["account"] == "fedex"

    # Then with short name
    await fedex.create_software_environment(
        name="goodstuff2", container="daskdev/dask:latest"
    )
    configs = await fedex.list_software_environments()
    e = configs["fedex/goodstuff2"]
    assert e["account"] == "fedex"


@pytest.mark.asyncio
async def test_can_create_cluster_configuration_using_full_name_or_short_name(
    sample_user,
    three_clouds,
):
    my_cloud, _, _ = three_clouds

    # First with fully qualified name
    await my_cloud.create_cluster_configuration(
        name=f"{sample_user.account.name}/goodstuff", software="env1"
    )
    configs = await my_cloud.list_cluster_configurations()
    c = configs[f"{sample_user.account.name}/goodstuff"]
    assert c["account"] == sample_user.account.name

    # Then with short name
    await my_cloud.create_cluster_configuration(name="goodstuff2", software="env1")
    configs = await my_cloud.list_cluster_configurations()
    c = configs[f"{sample_user.account.name}/goodstuff2"]
    assert c["account"] == sample_user.account.name


@pytest.mark.asyncio
async def test_can_create_config_in_different_account_when_member(three_clouds):
    _, jesss_cloud, fedex = three_clouds
    # jess is a member of fedex, so she should be allowed to create in that account
    await jesss_cloud.create_cluster_configuration(
        name="fedex/goodstuff", software="env1"
    )
    jess_configs = await jesss_cloud.list_cluster_configurations()
    fedex_configs = await fedex.list_cluster_configurations()
    assert "jess/goodstuff" not in jess_configs
    assert "fedex/goodstuff" in fedex_configs
    c = fedex_configs["fedex/goodstuff"]
    assert c["account"] == "fedex"
    for prop in ["scheduler", "worker"]:
        assert c[prop]["software"] == "env1"


@pytest.mark.asyncio
async def test_can_create_software_environment_in_different_account_when_member(
    three_clouds,
):
    _, jesss_cloud, fedex = three_clouds
    # jess is a member of fedex, so she should be allowed to create in that account
    await jesss_cloud.create_software_environment(
        name="fedex/goodenv", container="daskdev/dask:latest"
    )
    jess_envs = await jesss_cloud.list_software_environments()
    fedex_envs = await fedex.list_software_environments()
    assert "fedex/goodenv" not in jess_envs
    assert "fedex/goodenv" in fedex_envs
    e = fedex_envs["fedex/goodenv"]
    assert e["account"] == "fedex"


@pytest.mark.asyncio
async def test_cannot_create_software_environment_in_foreign_account(three_clouds):
    # "coiled" is not a member of fedex or jesss
    my_cloud, jesss_cloud, _ = three_clouds

    with pytest.raises(ValueError) as error_info:
        await my_cloud.create_software_environment(
            name="fedex/invasive_env", container="daskdev/dask:latest"
        )
    error_message = error_info.value.args[0]
    # Error message says something like unable to connect, do you have
    # permissions for the fedex account
    assert "permissions" in error_message
    assert "fedex" in error_message


@pytest.mark.asyncio
async def test_cannot_create_cluster_configuration_in_foreign_account(three_clouds):
    # "coiled" is not a member of fedex or jesss
    my_cloud, jesss_cloud, _ = three_clouds

    with pytest.raises(Exception) as error_info:
        await my_cloud.create_cluster_configuration(
            name="jess/coolconfig", software="jess/env1"
        )
    error_message = error_info.value.args[0]
    assert "not a member" in str(error_message)


@pytest.mark.test_group("slow")
@pytest.mark.asyncio
async def test_can_create_cluster_using_foreign_config(three_clouds):
    async with coiled.Cluster(
        cloud=three_clouds[0],
        configuration=f"{three_clouds[1].default_account}/conf1",
    ):
        # Nothing blew up
        pass


@pytest.mark.asyncio
async def test_non_existend_software_env_raises(
    three_clouds: Tuple[Cloud[Async], Cloud[Async], Cloud[Async]]
):
    # If jess wants to use fedex env, the account name
    # needs to be included.
    my_cloud, jess_cloud, fedex_cloud = three_clouds

    with pytest.raises(
        ValueError, match="Software environment with the name 'env5' not found"
    ):

        await coiled.Cluster(
            cloud=jess_cloud,
            software="env5",
            configuration=f"{jess_cloud.default_account}/conf1",
        )
