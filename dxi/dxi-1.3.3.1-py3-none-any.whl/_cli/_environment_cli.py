#
# Copyright (c) 2021 by Delphix. All rights reserved.
#

import click
from dxi._lib.util import boolean_based_system_exit
from dxi.environment.dxi_environment import DXIEnvironment
from dxi.environment.dxi_environment import EnvironmentConstants


@click.group(
    short_help="\b\nPerform Environment Operations.\n"
               "[add | refresh | enable | disable | "
               "updatehost \ndelete | list]"
)
def environment():
    """
    Linux/Unix & Windows Environment operations
    """
    pass


@environment.command()
@click.option(
    "--old-host", required=True, help="Old IP or HostName of the environment"
)
@click.option(
    "--new-host", required=True, help="New IP or HostName of the environment"
)
@click.option(
    "--engine",
    default=EnvironmentConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
    "[Default: {}]".format(EnvironmentConstants.SINGLE_THREAD),
    default=EnvironmentConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(EnvironmentConstants.POLL),
    default=EnvironmentConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=EnvironmentConstants.PARALLEL,
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file (including filename).",
    default=EnvironmentConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path of the logs folder.",
    default=EnvironmentConstants.LOG_FILE_PATH,
)
def updatehost(
    engine,
    single_thread,
    parallel,
    poll,
    config,
    log_file_path,
    old_host,
    new_host,
):
    """
    Update an environment's IP address
    """
    env_obj = DXIEnvironment(
        engine=engine,
        parallel=parallel,
        poll=poll,
        config_file=config,
        log_file_path=log_file_path,
        single_thread=single_thread,
    )
    boolean_based_system_exit(
        env_obj.updatehost(old_host=old_host, new_host=new_host)
    )


@environment.command()
@click.option("--env-name", required=True, help="Name of the environment.")
@click.option(
    "--engine",
    default=EnvironmentConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
    "[Default: {}]".format(EnvironmentConstants.SINGLE_THREAD),
    default=EnvironmentConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(EnvironmentConstants.POLL),
    default=EnvironmentConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=EnvironmentConstants.PARALLEL,
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file (including filename).",
    default=EnvironmentConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path of the logs folder.",
    default=EnvironmentConstants.LOG_FILE_PATH,
)
def delete(
    engine, single_thread, parallel, poll, config, log_file_path, env_name
):
    """
    Delete an environment.
    """
    env_obj = DXIEnvironment(
        engine=engine,
        parallel=parallel,
        poll=poll,
        config_file=config,
        log_file_path=log_file_path,
        single_thread=single_thread,
    )
    boolean_based_system_exit(env_obj.delete(env_name=env_name))


@environment.command()
@click.option("--env-name", required=True, help="Name of the environment.")
@click.option(
    "--engine",
    default=EnvironmentConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
    "[Default: {}]".format(EnvironmentConstants.SINGLE_THREAD),
    default=EnvironmentConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(EnvironmentConstants.POLL),
    default=EnvironmentConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=EnvironmentConstants.PARALLEL,
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file (including filename).",
    default=EnvironmentConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path of the logs folder.",
    default=EnvironmentConstants.LOG_FILE_PATH,
)
def enable(
    engine, single_thread, parallel, poll, config, log_file_path, env_name
):
    """
    Enable an environment.
    """
    env_obj = DXIEnvironment(
        engine=engine,
        parallel=parallel,
        poll=poll,
        config_file=config,
        log_file_path=log_file_path,
        single_thread=single_thread,
    )
    boolean_based_system_exit(env_obj.enable(env_name=env_name))


@environment.command()
@click.option(
    "--engine",
    default=EnvironmentConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
    "[Default: {}]".format(EnvironmentConstants.SINGLE_THREAD),
    default=EnvironmentConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(EnvironmentConstants.POLL),
    default=EnvironmentConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=EnvironmentConstants.PARALLEL,
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file (including filename).",
    default=EnvironmentConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path of the logs folder.",
    default=EnvironmentConstants.LOG_FILE_PATH,
)
@click.option("--env-name", required=True, help="Name of the environment.")
def disable(
    engine, single_thread, parallel, poll, config, log_file_path, env_name
):
    """
    Disable an environment.
    """
    env_obj = DXIEnvironment(
        engine=engine,
        parallel=parallel,
        poll=poll,
        config_file=config,
        log_file_path=log_file_path,
        single_thread=single_thread,
    )
    boolean_based_system_exit(env_obj.disable(env_name=env_name))


@environment.command()
@click.option("--env-name", required=True, help="Name of the environment.")
@click.option(
    "--engine",
    default=EnvironmentConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
    "[Default: {}]".format(EnvironmentConstants.SINGLE_THREAD),
    default=EnvironmentConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(EnvironmentConstants.POLL),
    default=EnvironmentConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=EnvironmentConstants.PARALLEL,
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file (including filename).",
    default=EnvironmentConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path of the logs folder.",
    default=EnvironmentConstants.LOG_FILE_PATH,
)
def refresh(
    engine, single_thread, parallel, poll, config, log_file_path, env_name
):
    """
    Refresh an environment.
    """
    env_obj = DXIEnvironment(
        engine=engine,
        parallel=parallel,
        poll=poll,
        config_file=config,
        log_file_path=log_file_path,
        single_thread=single_thread,
    )
    boolean_based_system_exit(env_obj.refresh(env_name=env_name))


@environment.command()
@click.option(
    "--engine",
    default=EnvironmentConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
    "[Default: {}]".format(EnvironmentConstants.SINGLE_THREAD),
    default=EnvironmentConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(EnvironmentConstants.POLL),
    default=EnvironmentConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=EnvironmentConstants.PARALLEL,
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file (including filename).",
    default=EnvironmentConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path of the logs folder.",
    default=EnvironmentConstants.LOG_FILE_PATH,
)
def list(engine, single_thread, parallel, poll, config, log_file_path):
    """
    List all environments on an engine
    """
    env_obj = DXIEnvironment(
        engine=engine,
        parallel=parallel,
        poll=poll,
        config_file=config,
        log_file_path=log_file_path,
        single_thread=single_thread,
    )
    boolean_based_system_exit(env_obj.list())


@environment.command()
@click.option("--env-name", required=True, help="Name of the environment.")
@click.option(
    "--env-type",
    required=True,
    default=EnvironmentConstants.TYPE,
    help="\b\nType of the environment. \n" "[ unix | windows ]",
)
@click.option(
    "--host-ip",
    required=True,
    help="IP address or Hostname of the environment.",
    default=EnvironmentConstants.HOSTIP,
)
@click.option(
    "--toolkit-dir",
    help="\b\nDirectory on the UNIX/LINUX environment\n"
    "to download Delphix Toolkit.\n"
    "[Required if adding a UNIX/LINUX environment]",
    default=None,
)
@click.option(
    "--os-user",
    required=True,
    help="Delphix OS user on the environment.",
    default=None,
)
@click.option(
    "--os-user-pwd",
    required=True,
    help="Delphix OS user password",
    default=None,
)
@click.option(
    "--connector-env-name",
    help="\b\nName of the environment on which \n"
    " Windows connector is installed and running.\n"
    "[Required if adding a Windows Source environment]",
    default=None,
)
@click.option(
    "--ase-db-user",
    help="\b\nDatabase username for ASE.\n"
    "[Required if adding an environment for ASE Database]",
    default=None,
)
@click.option(
    "--ase-db-user-pwd",
    help="\b\nDatabase user password for ASE.\n"
    "[Required if adding an environment for ASE Database]",
    default=None,
)
@click.option(
    "--engine",
    default=EnvironmentConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
    "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread\n"
    "[Default: {}]".format(EnvironmentConstants.SINGLE_THREAD),
    default=EnvironmentConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
    "[Default: {}s]".format(EnvironmentConstants.POLL),
    default=EnvironmentConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=EnvironmentConstants.PARALLEL,
)
@click.option(
    "--config",
    help="Full path to the dxtools.conf file (including filename).",
    default=EnvironmentConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="Full path of the logs folder.",
    default=EnvironmentConstants.LOG_FILE_PATH,
)
def add(
    env_name,
    env_type,
    host_ip,
    toolkit_dir,
    connector_env_name,
    os_user,
    os_user_pwd,
    ase_db_user,
    ase_db_user_pwd,
    engine,
    single_thread,
    parallel,
    poll,
    config,
    log_file_path,
):
    """
    Add an environment.
    """
    env_obj = DXIEnvironment(
        engine=engine,
        parallel=parallel,
        poll=poll,
        config_file=config,
        log_file_path=log_file_path,
        single_thread=single_thread,
    )
    boolean_based_system_exit(
        env_obj.add(
            env_type=env_type,
            env_name=env_name,
            host_ip=host_ip,
            toolkit_dir=toolkit_dir,
            connector_env_name=connector_env_name,
            os_user=os_user,
            os_user_pwd=os_user_pwd,
            ase_db_user=ase_db_user,
            ase_db_user_pwd=ase_db_user_pwd,
        )
    )


if __name__ == "__main__":
    list()
