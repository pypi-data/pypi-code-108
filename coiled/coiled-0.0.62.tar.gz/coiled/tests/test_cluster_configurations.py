import pytest

SOFTWARE_ENV_NAME_ALT = "myenv2"
CLUSTER_CONFIG_NAME = "my_config"


@pytest.mark.asyncio
async def test_can_create(
    cloud, sample_user, software_env, cleanup, backend, docker_prune
):
    account_name = sample_user.account.name
    full_cluster_config_name = f"{account_name}/{CLUSTER_CONFIG_NAME}"

    await cloud.create_cluster_configuration(
        name=CLUSTER_CONFIG_NAME,
        software=software_env,
    )
    config_list = await cloud.list_cluster_configurations(account=account_name)
    config = config_list.get(full_cluster_config_name)
    assert config
    assert config["worker"]["software"] == software_env
    assert config["scheduler"]["software"] == software_env


@pytest.mark.asyncio
async def test_can_update(
    cloud, sample_user, software_env, cleanup, backend, docker_prune
):
    account_name = sample_user.account.name
    full_cluster_config_name = f"{account_name}/{CLUSTER_CONFIG_NAME}"

    await cloud.create_cluster_configuration(
        name=CLUSTER_CONFIG_NAME,
        software=software_env,
    )

    await cloud.create_software_environment(
        name=SOFTWARE_ENV_NAME_ALT, container="daskdev/dask-notebook"
    )

    await cloud.create_cluster_configuration(
        name=CLUSTER_CONFIG_NAME,
        software=SOFTWARE_ENV_NAME_ALT,
    )

    # cluster config should have new senv
    config_list = await cloud.list_cluster_configurations(account=account_name)
    config = config_list.get(full_cluster_config_name)
    new_worker_senv = config["worker"]["software"]
    new_scheduler_senv = config["scheduler"]["software"]

    assert new_worker_senv == SOFTWARE_ENV_NAME_ALT
    assert new_scheduler_senv == SOFTWARE_ENV_NAME_ALT


@pytest.mark.asyncio
async def test_can_delete(
    cloud, sample_user, software_env, cleanup, backend, docker_prune
):
    account_name = sample_user.account.name
    full_cluster_config_name = f"{account_name}/{CLUSTER_CONFIG_NAME}"

    await cloud.create_cluster_configuration(
        name=CLUSTER_CONFIG_NAME,
        software=software_env,
    )

    config_list = await cloud.list_cluster_configurations(account=account_name)
    assert full_cluster_config_name in config_list

    await cloud.delete_cluster_configuration(CLUSTER_CONFIG_NAME)
    config_list = await cloud.list_cluster_configurations(account=account_name)
    assert full_cluster_config_name not in config_list


@pytest.mark.asyncio
async def test_error_when_deleting_nonexisting_cluster_config(
    cloud, cleanup, backend, docker_prune
):
    bad_cluster_config_name = "not_a_real_config"
    with pytest.raises(Exception, match="detail=Not found"):
        await cloud.delete_cluster_configuration(
            name=bad_cluster_config_name,
        )


@pytest.mark.asyncio
async def test_throw_error_if_senv_does_not_exist_on_create(
    cloud, sample_user, cleanup, backend, docker_prune
):
    bad_senv_name = "not_a_real_software_environment"
    with pytest.raises(
        Exception,
        match=f"Software environment '{bad_senv_name}' not found",
    ):
        await cloud.create_cluster_configuration(
            name=CLUSTER_CONFIG_NAME,
            software=bad_senv_name,
        )


@pytest.mark.asyncio
async def test_throw_error_if_senv_does_not_exist_on_update(
    cloud, sample_user, cluster_configuration, cleanup, backend, docker_prune
):
    bad_senv_name = "not_a_real_software_environment"
    with pytest.raises(
        Exception,
        match=f"Software environment '{bad_senv_name}' not found",
    ):
        await cloud.create_cluster_configuration(
            name=cluster_configuration,
            software=bad_senv_name,
        )


@pytest.mark.asyncio
async def test_create_using_older_revision_of_senv(
    cloud, sample_user, software_env, cleanup, backend, docker_prune
):
    account_name = sample_user.account.name
    full_cluster_config_name = f"{account_name}/{CLUSTER_CONFIG_NAME}"

    await cloud.create_software_environment(
        name=software_env, container="daskdev/dask-notebook"
    )

    envs_list = await cloud.list_software_environments(account=account_name)
    env = envs_list.get(software_env)
    identifier = env.get("identifier")

    await cloud.create_cluster_configuration(
        name=full_cluster_config_name,
        software=f"{software_env}:{identifier}",
    )

    config_list = await cloud.list_cluster_configurations(account=account_name)
    config = config_list.get(full_cluster_config_name)
    worker_senv = config["worker"]["software"]
    scheduler_senv = config["scheduler"]["software"]
    assert worker_senv == f"{software_env}:{identifier}"
    assert scheduler_senv == f"{software_env}:{identifier}"


@pytest.mark.asyncio
async def test_update_to_use_older_revision_of_senv(
    cloud, sample_user, software_env, cleanup, backend, docker_prune
):
    account_name = sample_user.account.name
    full_cluster_config_name = f"{account_name}/{CLUSTER_CONFIG_NAME}"

    await cloud.create_software_environment(
        name=software_env, container="daskdev/dask-notebook"
    )

    await cloud.create_cluster_configuration(
        name=full_cluster_config_name,
        software=software_env,
    )

    config_list = await cloud.list_cluster_configurations(account=account_name)
    config = config_list.get(full_cluster_config_name)
    assert config["worker"]["software"] == software_env
    assert config["scheduler"]["software"] == software_env

    envs_list = await cloud.list_software_environments(account=account_name)
    env = envs_list.get(software_env)
    identifier = env.get("identifier")

    await cloud.create_cluster_configuration(
        name=full_cluster_config_name,
        software=f"{software_env}:{identifier}",
    )

    config_list = await cloud.list_cluster_configurations(account=account_name)
    config = config_list.get(full_cluster_config_name)
    worker_senv = config["worker"]["software"]
    scheduler_senv = config["scheduler"]["software"]
    assert worker_senv == f"{software_env}:{identifier}"
    assert scheduler_senv == f"{software_env}:{identifier}"


@pytest.mark.asyncio
async def test_error_using_deleted_senv(
    cloud, sample_user, software_env, cleanup, backend, docker_prune
):
    account_name = sample_user.account.name
    alt_software_env = f"{account_name}/{SOFTWARE_ENV_NAME_ALT}"
    full_cluster_config_name = f"{account_name}/{CLUSTER_CONFIG_NAME}"

    await cloud.create_software_environment(
        name=alt_software_env, container="daskdev/dask"
    )

    await cloud.delete_software_environment(name=f"{alt_software_env}")

    with pytest.raises(
        Exception, match=f"Software environment '{alt_software_env}' not found"
    ):
        await cloud.create_cluster_configuration(
            name=full_cluster_config_name,
            software=alt_software_env,
        )


@pytest.mark.asyncio
async def test_deleting_senv_revision_deletes_certain_cluster_configs(
    cloud, sample_user, cleanup, backend, docker_prune
):
    account_name = sample_user.account.name
    alt_software_env = f"{account_name}/{SOFTWARE_ENV_NAME_ALT}"
    full_cluster_config_name = f"{account_name}/{CLUSTER_CONFIG_NAME}"
    alt_cluster_config_name = f"{account_name}/myconfig2"

    await cloud.create_software_environment(
        name=alt_software_env, container="daskdev/dask"
    )

    await cloud.create_software_environment(
        name=alt_software_env, container="daskdev/dask-notebook"
    )

    envs_list = await cloud.list_software_environments(account=account_name)
    env = envs_list.get(alt_software_env)
    latest = env.get("identifier")

    await cloud.create_cluster_configuration(
        name=full_cluster_config_name,
        software=alt_software_env,
    )

    await cloud.create_cluster_configuration(
        name=alt_cluster_config_name,
        software=f"{alt_software_env}:{latest}",
    )

    config_list = await cloud.list_cluster_configurations(account=account_name)
    assert full_cluster_config_name in config_list
    assert alt_cluster_config_name in config_list
    assert len(config_list) == 2

    # should still have one cluster config left
    await cloud.delete_software_environment(name=f"{alt_software_env}:{latest}")

    config_list = await cloud.list_cluster_configurations(account=account_name)
    assert full_cluster_config_name in config_list
    assert len(config_list) == 1


@pytest.mark.asyncio
async def test_deleting_senv_deletes_all_cluster_configs(
    cloud, sample_user, cleanup, backend, docker_prune
):
    account_name = sample_user.account.name
    alt_software_env = f"{account_name}/{SOFTWARE_ENV_NAME_ALT}"
    full_cluster_config_name = f"{account_name}/{CLUSTER_CONFIG_NAME}"
    alt_cluster_config_name = f"{account_name}/myconfig2"

    await cloud.create_software_environment(
        name=alt_software_env, container="daskdev/dask"
    )

    await cloud.create_software_environment(
        name=alt_software_env, container="daskdev/dask-notebook"
    )

    envs_list = await cloud.list_software_environments(account=account_name)
    env = envs_list.get(alt_software_env)
    latest = env.get("identifier")

    await cloud.create_cluster_configuration(
        name=full_cluster_config_name,
        software=alt_software_env,
    )

    await cloud.create_cluster_configuration(
        name=alt_cluster_config_name,
        software=f"{alt_software_env}:{latest}",
    )

    config_list = await cloud.list_cluster_configurations(account=account_name)
    assert full_cluster_config_name in config_list
    assert alt_cluster_config_name in config_list
    assert len(config_list) == 2

    # should delete both cluster configurations
    await cloud.delete_software_environment(name=f"{alt_software_env}")

    config_list = await cloud.list_cluster_configurations(account=account_name)
    assert config_list == {}
