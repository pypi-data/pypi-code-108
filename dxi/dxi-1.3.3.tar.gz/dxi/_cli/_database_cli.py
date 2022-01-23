#
# Copyright (c) 2021 by Delphix. All rights reserved.
#

import click
from dxi._lib.util import boolean_based_system_exit
from dxi.database.dxi_database import DXIDatabase
from dxi.database.dxi_database import DXIDatabaseConstants


@click.group(
    short_help="\b\nPerform Database Operations "
               "on DSOURCE, VDB or VFILE.\n"
               "[ingest | provision | refresh | "
               "rewind | start | stop \nenable | disable | list]"
)
def database():
    """
    Perform Dsource, VDB and vFiles related operations.
    """
    pass


# Refresh command
@database.command()
@click.option(
    "--db-name",
    required=True,
    help="\b\nName of the virtual dataset to refresh.",
    default=None,
)
@click.option(
    "--timestamp-type",
    help="\b\nThe type of timestamp you are specifying for refresh.\n"
         "Options: [TIME | SNAPSHOT]\n"
         "[default: SNAPSHOT]",
    default="SNAPSHOT",
)
@click.option(
    "--timestamp",
    default="LATEST",
    help="""The Delphix semantic for the point in time on the source db or vfile 
    from which you want to refresh your VDB/vFile. \n
    Formats:                                                                      
    To use Latest Snapshot or Timepoint: LATEST                            
    To use a point in time: "YYYY-MM-DDTHH:MI:SS"                                           
    To use a snapshot name: "@YYYY-MM-DDTHH24:MI:SS.ZZZ"        
    To use snapshot time from GUI : "YYYY-MM-DDTHH:MI:SS"
    [default: LATEST]
    
    * A timestamp value should be in 24 hour format.     
    * Provided values should be enclosed in double quotes.                                                                
    """,
)
@click.option(
    "--timeflow",
    help="Name of the source database timeflow to refresh the virtual dataset.",
    default=None,
)
@click.option(
    "--engine",
    default=DXIDatabaseConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
         "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
         "[Default: {}]".format(DXIDatabaseConstants.SINGLE_THREAD),
    default=DXIDatabaseConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
         "[Default: {}s]".format(DXIDatabaseConstants.POLL),
    default=DXIDatabaseConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=DXIDatabaseConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=DXIDatabaseConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=DXIDatabaseConstants.LOG_FILE_PATH,
)
def refresh(
        db_name,
        timestamp_type,
        timestamp,
        engine,
        single_thread,
        timeflow,
        poll,
        config,
        log_file_path,
        parallel,
):
    """
    Refresh a Delphix VDB or vFile.
    """

    obj = DXIDatabase(
        engine=engine,
        single_thread=single_thread,
        poll=poll,
        config=config,
        log_file_path=log_file_path,
        parallel=parallel,
    )

    boolean_based_system_exit(
        obj.refresh(
            db_name=db_name,
            timestamp_type=timestamp_type,
            timestamp=timestamp,
            timeflow=timeflow,
        )
    )


# Rewind Command
@database.command()
@click.option(
    "--db-name",
    required=True,
    help="Name of the virtual dataset to rewind.",
    default=None,
)
@click.option(
    "--timestamp-type",
    help="\b\nThe type of timestamp you are specifying for refresh.\n"
         "Options: [TIME | SNAPSHOT]\n"
         "[default: SNAPSHOT]",
    default="SNAPSHOT",
)
@click.option(
    "--timestamp",
    default="LATEST",
    help="""The Delphix semantic for the point in time on the source db or vfile 
    from which you want to refresh your VDB/vFile. \n
    Formats:                                                                      
    To use Latest Snapshot or Timepoint: LATEST                            
    To use a point in time: "YYYY-MM-DDTHH:MI:SS"                                           
    To use a snapshot name: "@YYYY-MM-DDTHH24:MI:SS.ZZZ"        
    To use snapshot time from GUI : "YYYY-MM-DDTHH:MI:SS"
    [default: LATEST]
    
    * A timestamp value should be in 24 hour format.     
    * Provided values should be enclosed in double quotes.                                                                
    """,
)
@click.option(
    "--db-type",
    help="Type of database: oracle, mssql, ase, vfiles",
    default=None,
)
@click.option(
    "--engine",
    default=DXIDatabaseConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
         "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
         "[Default: {}]".format(DXIDatabaseConstants.SINGLE_THREAD),
    default=DXIDatabaseConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
         "[Default: {}s]".format(DXIDatabaseConstants.POLL),
    default=DXIDatabaseConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=DXIDatabaseConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=DXIDatabaseConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=DXIDatabaseConstants.LOG_FILE_PATH,
)
def rewind(
        db_name,
        timestamp_type,
        timestamp,
        engine,
        single_thread,
        db_type,
        poll,
        config,
        log_file_path,
        parallel,
):
    """
    Rewind a VDB or vFile.
    """

    obj = DXIDatabase(
        engine=engine,
        single_thread=single_thread,
        poll=poll,
        config=config,
        log_file_path=log_file_path,
        parallel=parallel,
    )
    boolean_based_system_exit(
        obj.rewind(
            db_name,
            timestamp_type=timestamp_type,
            timestamp=timestamp,
            db_type=db_type,
        )
    )


# Delete command
@database.command()
@click.option(
    "--db-name",
    default=None,
    required=True,
    help="\b\nName of datasets to delete.\n"
         "To delete multiple datasets, separate them with ':'.\n"
         "Usage: vdb1:vdb2",
)
@click.option(
    "--db-type",
    default=DXIDatabaseConstants.TYPE,
    help="\b\nType of the dataset to delete.\n"
         "[vdb | dsource]\n"
         "[default: vdb]",
)
@click.option(
    "--force",
    is_flag=True,
    default=DXIDatabaseConstants.FORCE,
    help="Force delete the dataset(s).",
)
@click.option(
    "--engine",
    default=DXIDatabaseConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
         "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
         "[Default: {}]".format(DXIDatabaseConstants.SINGLE_THREAD),
    default=DXIDatabaseConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
         "[Default: {}s]".format(DXIDatabaseConstants.POLL),
    default=DXIDatabaseConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=DXIDatabaseConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=DXIDatabaseConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=DXIDatabaseConstants.LOG_FILE_PATH,
)
def delete(
        db_name,
        db_type,
        engine,
        single_thread,
        parallel,
        poll,
        config,
        log_file_path,
        force,
):
    """
    Delete a Delphix dSource or VDB.
    """
    obj = DXIDatabase(
        engine=engine,
        single_thread=single_thread,
        poll=poll,
        config=config,
        log_file_path=log_file_path,
        parallel=parallel,
    )
    boolean_based_system_exit(
        obj.delete(db_name, db_type=db_type, force=force)
    )


#############################################
# DB Operations

# db-list
@database.command()
@click.option(
    "--engine",
    default=DXIDatabaseConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
         "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
         "[Default: {}]".format(DXIDatabaseConstants.SINGLE_THREAD),
    default=DXIDatabaseConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
         "[Default: {}s]".format(DXIDatabaseConstants.POLL),
    default=DXIDatabaseConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=DXIDatabaseConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=DXIDatabaseConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=DXIDatabaseConstants.LOG_FILE_PATH,
)
def list(engine, single_thread, parallel, poll, config, log_file_path):
    """
    List all datasets on an engine.
    """
    obj = DXIDatabase(
        engine=engine,
        single_thread=single_thread,
        poll=poll,
        config=config,
        log_file_path=log_file_path,
        parallel=parallel,
    )
    boolean_based_system_exit(obj.list())


# db-start
@database.command()
@click.option(
    "--db-name",
    help="Name of the virtual dataset to start.",
    default=None,
)
@click.option("--group", help="Group where the dataset resides.", default=None)
@click.option(
    "--engine",
    default=DXIDatabaseConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
         "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
         "[Default: {}]".format(DXIDatabaseConstants.SINGLE_THREAD),
    default=DXIDatabaseConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
         "[Default: {}s]".format(DXIDatabaseConstants.POLL),
    default=DXIDatabaseConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=DXIDatabaseConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=DXIDatabaseConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=DXIDatabaseConstants.LOG_FILE_PATH,
)
def start(
        db_name,
        group,
        engine,
        single_thread,
        parallel,
        poll,
        config,
        log_file_path,
):
    """
    Starts a virtual dataset by name and group
    """
    ops_obj = DXIDatabase(
        engine=engine,
        single_thread=single_thread,
        poll=poll,
        config=config,
        parallel=parallel,
        log_file_path=log_file_path,
    )
    boolean_based_system_exit(ops_obj.start(db_name=db_name, group=group))


# db-stop
@database.command()
@click.option(
    "--db-name",
    help="Name of the virtual dataset to stop.",
    default=None,
)
@click.option("--group", help="Group where the dataset resides", default=None)
@click.option(
    "--engine",
    default=DXIDatabaseConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
         "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
         "[Default: {}]".format(DXIDatabaseConstants.SINGLE_THREAD),
    default=DXIDatabaseConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
         "[Default: {}s]".format(DXIDatabaseConstants.POLL),
    default=DXIDatabaseConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=DXIDatabaseConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=DXIDatabaseConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=DXIDatabaseConstants.LOG_FILE_PATH,
)
def stop(
        db_name,
        group,
        engine,
        single_thread,
        parallel,
        poll,
        config,
        log_file_path,
):
    """
    Stop a virtual dataset by name and group (optional)
    """
    ops_obj = DXIDatabase(
        engine=engine,
        poll=poll,
        config=config,
        parallel=parallel,
        log_file_path=log_file_path,
        single_thread=single_thread,
    )
    boolean_based_system_exit(ops_obj.stop(db_name=db_name, group=group))


# db-enable
@database.command()
@click.option(
    "--db-name",
    help="Name of the virtual dataset to enable.",
    default=None,
)
@click.option("--group", help="Group where the dataset resides.", default=None)
@click.option(
    "--engine",
    default=DXIDatabaseConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
         "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
         "[Default: {}]".format(DXIDatabaseConstants.SINGLE_THREAD),
    default=DXIDatabaseConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
         "[Default: {}s]".format(DXIDatabaseConstants.POLL),
    default=DXIDatabaseConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=DXIDatabaseConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=DXIDatabaseConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=DXIDatabaseConstants.LOG_FILE_PATH,
)
def enable(
        db_name,
        group,
        engine,
        single_thread,
        parallel,
        poll,
        config,
        log_file_path,
):
    """
    Enable a virtual dataset by name and group(optional)
    """
    ops_obj = DXIDatabase(
        engine=engine,
        single_thread=single_thread,
        poll=poll,
        config=config,
        parallel=parallel,
        log_file_path=log_file_path,
    )
    boolean_based_system_exit(ops_obj.enable(db_name=db_name, group=group))


# db-disable
@database.command()
@click.option(
    "--db-name",
    help="Name of the virtual dataset to disable.",
    default=None,
)
@click.option("--group", help="Group where the dataset resides.", default=None)
@click.option(
    "--force",
    is_flag=True,
    help="Force disable a virtual dataset.",
    default=None,
)
@click.option(
    "--engine",
    default=DXIDatabaseConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
         "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
         "[Default: {}]".format(DXIDatabaseConstants.SINGLE_THREAD),
    default=DXIDatabaseConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
         "[Default: {}s]".format(DXIDatabaseConstants.POLL),
    default=DXIDatabaseConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=DXIDatabaseConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=DXIDatabaseConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=DXIDatabaseConstants.LOG_FILE_PATH,
)
def disable(
        db_name,
        group,
        force,
        engine,
        single_thread,
        parallel,
        poll,
        config,
        log_file_path,
):
    """
    Disable a virtual dataset by name and group(optional).
    """
    ops_obj = DXIDatabase(
        engine=engine,
        single_thread=single_thread,
        poll=poll,
        config=config,
        log_file_path=log_file_path,
        parallel=parallel,
    )
    boolean_based_system_exit(
        ops_obj.disable(db_name=db_name, group=group, force=force)
    )


# Create dSource
@click.group()
def ingest():
    """
    Ingest/Link a source database into Delphix.
    """
    pass


@ingest.command()
@click.option(
    "--source-name", required=True, help="Name of the dSource to create."
)
@click.option("--db-user", help="Source DB username.", required=True)
@click.option(
    "--db-password", help="Source DB user password.", required=True
)
@click.option("--group", help="Group name for the dsource.", required=True)
@click.option(
    "--env-name",
    help="Name of the host environment for the dsource.",
    required=True,
)
@click.option(
    "--env-inst",
    help="\b\nFull path of the database binary on the source host.\n"
         "For oracle, this is the path to Oracle db_home.",
    required=True,
)
@click.option(
    "--port-num",
    help="Port number for the oracle listener.",
    required=True,
    default=DXIDatabaseConstants.ORACLE_DEFAULT_PORT,
)
@click.option(
    "--logsync", help="Enable or disable logsync.", is_flag=True, default=True
)
@click.option("--ip-addr", help="IP Address of the dsource.")
@click.option(
    "--rman-channels",
    help="Configures the number of Oracle RMAN Channels.",
    default=2,
)
@click.option(
    "--files-per-set",
    help="Configures how many files per set for Oracle RMAN.",
    default=5,
)
@click.option(
    "--num-connections",
    help="Number of connections for Oracle RMAN.",
    default=5,
)
@click.option(
    "--engine",
    default=DXIDatabaseConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
         "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
         "[Default: {}]".format(DXIDatabaseConstants.SINGLE_THREAD),
    default=DXIDatabaseConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
         "[Default: {}s]".format(DXIDatabaseConstants.POLL),
    default=DXIDatabaseConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=DXIDatabaseConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=DXIDatabaseConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=DXIDatabaseConstants.LOG_FILE_PATH,
)
def oracle(
        engine,
        ip_addr,
        env_name,
        group,
        source_name,
        db_user,
        db_password,
        env_inst,
        num_connections,
        log_file_path,
        logsync,
        single_thread,
        files_per_set,
        rman_channels,
        port_num,
        parallel,
        poll,
        config,
):
    """
    Ingest/Link an Oracle dSource.
    """
    obj = DXIDatabase(
        engine=engine,
        single_thread=single_thread,
        parallel=parallel,
        poll=poll,
        config=config,
        log_file_path=log_file_path,
    )
    boolean_based_system_exit(
        obj.ingest_oracle(
            source_name,
            db_password,
            db_user,
            group,
            env_inst,
            ip_addr=ip_addr,
            env_name=env_name,
            num_connections=num_connections,
            logsync=logsync,
            files_per_set=files_per_set,
            rman_channels=rman_channels,
            port_num=port_num,
        )
    )

@ingest.command()
@click.option(
    "--source-name", required=True, help="Name of the dSource to create."
)
@click.option("--db-user", help="Source DB username.", required=True)
@click.option(
    "--db-password", help="Source DB user password.", required=True
)
@click.option("--group", help="Group name for the dsource.", required=True)
@click.option(
    "--env-name",
    help="Name of the host environment for the dsource.",
    required=True,
)
@click.option(
    "--env-inst",
    help="\b\nFull path of the database binary on the source host.\n"
         "For oracle, this is the path to Oracle db_home.",
    required=True,
)
@click.option(
    "--logsync", help="Enable or disable logsync.", is_flag=True, default=True
)
@click.option(
    "--rman-channels",
    help="Configures the number of Oracle RMAN Channels.",
    default=2,
)
@click.option(
    "--files-per-set",
    help="Configures how many files per set for Oracle RMAN.",
    default=5,
)
@click.option(
    "--num-connections",
    help="Number of connections for Oracle RMAN.",
    default=5,
)
@click.option(
    "--engine",
    default=DXIDatabaseConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
         "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
         "[Default: {}]".format(DXIDatabaseConstants.SINGLE_THREAD),
    default=DXIDatabaseConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
         "[Default: {}s]".format(DXIDatabaseConstants.POLL),
    default=DXIDatabaseConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=DXIDatabaseConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=DXIDatabaseConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=DXIDatabaseConstants.LOG_FILE_PATH,
)
def oracle_mt_rac(
        engine,
        env_name,
        group,
        source_name,
        db_user,
        db_password,
        env_inst,
        num_connections,
        log_file_path,
        logsync,
        single_thread,
        files_per_set,
        rman_channels,
        parallel,
        poll,
        config,
):
    """
    Ingest/Link an Oracle MT RAC dSource.
    """
    obj = DXIDatabase(
        engine=engine,
        single_thread=single_thread,
        parallel=parallel,
        poll=poll,
        config=config,
        log_file_path=log_file_path,
    )
    boolean_based_system_exit(
        obj.ingest_oracle_mt_rac(
            source_name,
            db_password,
            db_user,
            group,
            env_inst,
            logsync=logsync,
            env_name=env_name,
            num_connections=num_connections,
            files_per_set=files_per_set,
            rman_channels=rman_channels,
        )
    )

@ingest.command()
@click.option(
    "--source-name", required=True, help="Name of the dSource to create."
)
@click.option("--db-user", help="Source DB user.", required=True)
@click.option("--db-password", help="Source DB user password.", required=True)
@click.option("--group", help="Group name for this dSource.", required=True)
@click.option("--logsync", help="Enable or disable logsync", is_flag=True, default=False)
@click.option(
    "--source-env",
    help="Name of the environment to use as source.",
    required=True,
)
@click.option(
    "--stage-env",
    help="Name of the environment to use as staging.",
    required=True,
)
@click.option(
    "--stage-instance",
    help="Name of the staging instance for ingestion.",
    required=True,
)
@click.option(
    "--backup-user",
    help="User with access to the shared location for backups.",
    default=None
)
@click.option(
    "--backup-user-pwd",
    help="Password of the shared backup path.",
    default=None,
)
@click.option(
    "--validated-sync-mode",
    help="Delphix will try to load the most recent backup.",
    default="TRANSACTION_LOG",
)
@click.option(
    "--delphix-managed",
    help="If set, Delphix will manage the backups.",
    default=False,
    is_flag=True,
)
@click.option(
    "--initial-load-type",
    help="Delphix will try to load the most recent backup.",
    default=None,
)
@click.option(
    "--backup-path", help="Full path to the MS SQLServer backups", default=None
)
@click.option(
    "--engine",
    default=DXIDatabaseConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
         "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
         "[Default: {}]".format(DXIDatabaseConstants.SINGLE_THREAD),
    default=DXIDatabaseConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
         "[Default: {}s]".format(DXIDatabaseConstants.POLL),
    default=DXIDatabaseConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=DXIDatabaseConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=DXIDatabaseConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=DXIDatabaseConstants.LOG_FILE_PATH,
)
def mssql(
        engine,
        group,
        source_name,
        db_user,
        db_password,
        log_file_path,
        logsync,
        single_thread,
        parallel,
        poll,
        config,
        stage_instance,
        stage_env,
        backup_user_pwd,
        backup_user,
        initial_load_type,
        validated_sync_mode,
        delphix_managed,
        backup_path,
        source_env
):
    """
    Link an MSSQL dSource
    """
    obj = DXIDatabase(
        engine=engine,
        single_thread=single_thread,
        parallel=parallel,
        poll=poll,
        config=config,
        log_file_path=log_file_path,
    )
    boolean_based_system_exit(
        obj.ingest_mssql(
            group=group,
            source_name=source_name,
            db_user=db_user,
            db_password=db_password,
            logsync=logsync,
            stage_instance=stage_instance,
            source_env=source_env,
            stage_env=stage_env,
            backup_user_pwd=backup_user_pwd,
            backup_user=backup_user,
            initial_load_type=initial_load_type,
            validated_sync_mode=validated_sync_mode,
            delphix_managed=delphix_managed,
            backup_path=backup_path,
        )
    )


@ingest.command()
@click.option(
    "--source-name", required=True, help="Name of the dSource to create."
)
@click.option("--db-user", help="Source DB user.", required=True)
@click.option("--db-password", help="Sourde DB user password.", required=True)
@click.option("--group", help="Group name for this dSource.", required=True)
@click.option("--env-name", help="Staging environment name", required=True)
@click.option("--source-env", help="Source environment name", required=True)
@click.option(
    "--stage-instance",
    help="The SAP ASE instance on the staging environment to use for sync.",
    required=True,
)
@click.option(
    "--backup-path",
    help="Path to the Sybase backups.",
    default=None,
    required=True,
)
@click.option("--logsync", help="Enable or disable logsync.", is_flag=True, default=True)
@click.option(
    "--backup-files",
    help="Backup file list (add space between multiple files)",
    default=None,
)
@click.option(
    "--create-backup",
    help="The parameters to use as input to sync a SAP ASE database by taking a new full backup.",
    default=False,
    is_flag=True,
)
@click.option(
    "--engine",
    default=DXIDatabaseConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
         "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
         "[Default: {}]".format(DXIDatabaseConstants.SINGLE_THREAD),
    default=DXIDatabaseConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
         "[Default: {}s]".format(DXIDatabaseConstants.POLL),
    default=DXIDatabaseConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=DXIDatabaseConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=DXIDatabaseConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=DXIDatabaseConstants.LOG_FILE_PATH,
)
def sybase(
        engine,
        env_name,
        group,
        source_name,
        db_user,
        db_password,
        log_file_path,
        logsync,
        single_thread,
        parallel,
        poll,
        config,
        stage_instance,
        backup_path,
        backup_files,
        create_backup,
        source_env,
):
    """
    Ingest an ASE/Sybase dsource.
    """
    obj = DXIDatabase(
        engine=engine,
        single_thread=single_thread,
        parallel=parallel,
        poll=poll,
        config=config,
        log_file_path=log_file_path,
    )
    boolean_based_system_exit(
        obj.ingest_sybase(
            source_name=source_name,
            db_user=db_user,
            db_password=db_password,
            group=group,
            source_env=source_env,
            stage_env=env_name,
            stage_instance=stage_instance,
            backup_path=backup_path,
            logsync=logsync,
            backup_files=backup_files,
            create_backup=create_backup,
        )
    )


database.add_command(ingest)
"""
Methods to provision different database types.
"""


@click.group()
def provision():
    """
    Provision Delphix Virtual Databases.
    """
    pass


@provision.command()
@click.option("--db-name", required=True, help="Name of the VDB.")
@click.option("--source-name", required=True, help="The source database name.")
@click.option(
    "--group",
    required=True,
    help="The group into which Delphix will place the VDB.",
)
@click.option(
    "--port-num",
    help="The port number of the database instance.",
    required=True,
)
@click.option(
    "--env-name",
    required=True,
    help="The name of the Target environment in Delphix",
)
@click.option(
    "--env-inst",
    help="\b\nThe identifier for ASE instance on the target environment.\n"
         "This is the ASE instance where the VDB will be provisioned. ",
    required=True,
)
@click.option(
    "--mntpoint",
    help="Mount folder that Delphix can use on the target host.",
    required=True,
)
@click.option(
    "--timestamp-type",
    help="\b\nThe type of timestamp you are specifying.\n"
         "[TIME | SNAPSHOT]\n"
         "[Default: default]",
    default="SNAPSHOT",
)
@click.option(
    "--timestamp",
    help="""The Delphix semantic for the point in time on the source db or vfile 
    from which you want to refresh your VDB/vFile. \n
    Formats:                                                                      
    To use Latest Snapshot or Timepoint: LATEST                            
    To use a point in time:"YYYY-MM-DDTHH:MI:SS"                                           
    To use a snapshot name:"@YYYY-MM-DDTHH24:MI:SS.ZZZ"                                           
    To use snapshot time from GUI:"YYYY-MM-DDTHH:MI:SS"                                           
    [default: LATEST]                                           
    
    * A timestamp value should be in 24 hour format.     
    * Provided values should be enclosed in double quotes.                                                                
    """,
    default="LATEST",
)
@click.option(
    "--prerefresh",
    help="Hook name to run before a refresh only (not during initial provision). ",
    default=False,
)
@click.option(
    "--postrefresh",
    help="Hook name to run after a refresh only (runs after Configure Clone).",
    default=False,
)
@click.option(
    "--prerollback", help="Hook name to run before a rewind", default=False
)
@click.option(
    "--postrollback", help="Hook name to run after a rewind", default=False
)
@click.option(
    "--configure-clone", help="Configure Clone commands", default=False
)
@click.option(
    "--no-truncate-log",
    help="Set the trunc log on chkpt database option.",
    default=False,
    is_flag=True,
)
@click.option(
    "--engine",
    default=DXIDatabaseConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
         "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
         "[Default: {}]".format(DXIDatabaseConstants.SINGLE_THREAD),
    default=DXIDatabaseConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
         "[Default: {}s]".format(DXIDatabaseConstants.POLL),
    default=DXIDatabaseConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=DXIDatabaseConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=DXIDatabaseConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=DXIDatabaseConstants.LOG_FILE_PATH,
)
def sybase(
        engine,
        source_name,
        db_name,
        group,
        mntpoint,
        env_name,
        timestamp,
        timestamp_type,
        prerefresh,
        postrefresh,
        prerollback,
        postrollback,
        configure_clone,
        env_inst,
        single_thread,
        parallel,
        poll,
        config,
        log_file_path,
        port_num,
        no_truncate_log,
):
    """
    Create a Sybase ASE VDB
    """
    obj = DXIDatabase(
        engine=engine,
        single_thread=single_thread,
        poll=poll,
        config=config,
        log_file_path=log_file_path,
        parallel=parallel,
    )
    boolean_based_system_exit(
        obj.provision_ase(
            group,
            source_name,
            db_name,
            env_name,
            timestamp=timestamp,
            timestamp_type=timestamp_type,
            prerefresh=prerefresh,
            postrefresh=postrefresh,
            prerollback=prerollback,
            postrollback=postrollback,
            configure_clone=configure_clone,
            env_inst=env_inst,
            port_num=port_num,
            mntpoint=mntpoint,
            no_truncate_log=no_truncate_log,
        )
    )


@provision.command()
@click.option(
    "--source-name", required=True, help="Name of the source database."
)
@click.option("--db-name", required=True, help="Name for the VDB.")
@click.option(
    "--env-name",
    required=True,
    help="The name of the target environment in Delphix.",
)
@click.option(
    "--env-inst",
    help="\b\nThe identifier for MS SQLServer instance on the target environment.\n"
         "This is the SQLServer instance where the VDB will be provisioned. ",
    required=True,
)
@click.option(
    "--mntpoint",
    help="Mount folder that Delphix can use on the target host.",
    required=True,
)
@click.option(
    "--group",
    help="The group into which Delphix will place the VDB.",
    required=True,
)
@click.option("--port-num", help="The port number of the database instance.")
@click.option(
    "--timestamp-type",
    help="\b\nThe type of timestamp you are specifying.\n"
         "[TIME | SNAPSHOT]\n"
         "[Default: default]",
    default="SNAPSHOT",
)
@click.option(
    "--timestamp",
    help="""The Delphix semantic for the point in time on the source db or vfile 
    from which you want to refresh your VDB/vFile. \n
    Formats:                                                                      
    To use Latest Snapshot or Timepoint: LATEST                            
    To use a point in time:"YYYY-MM-DDTHH:MI:SS"                                           
    To use a snapshot name:"@YYYY-MM-DDTHH24:MI:SS.ZZZ"                                           
    To use snapshot time from GUI:"YYYY-MM-DDTHH:MI:SS"                                           
    [default: LATEST]      
    
    * A timestamp value should be in 24 hour format.     
    * Provided values should be enclosed in double quotes.                                                                
    """,
    default="LATEST",
)
@click.option(
    "--prerefresh",
    help="Hook name to run before a refresh only (not during initial provision). ",
    default=None,
)
@click.option(
    "--postrefresh",
    help="Hook name to run after a refresh only (runs after Configure Clone).",
    default=None,
)
@click.option(
    "--prerollback", help="Hook name to run before a rewind", default=None
)
@click.option(
    "--postrollback", help="Hook name to run after a rewind.", default=None
)
@click.option(
    "--configure-clone",
    help="Hook name to run after initial provision and after a refresh.",
    default=None,
)
@click.option(
    "--engine",
    default=DXIDatabaseConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
         "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
         "[Default: {}]".format(DXIDatabaseConstants.SINGLE_THREAD),
    default=DXIDatabaseConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
         "[Default: {}s]".format(DXIDatabaseConstants.POLL),
    default=DXIDatabaseConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=DXIDatabaseConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=DXIDatabaseConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=DXIDatabaseConstants.LOG_FILE_PATH,
)
def mssql(
        engine,
        source_name,
        db_name,
        group,
        mntpoint,
        env_name,
        timestamp,
        timestamp_type,
        prerefresh,
        postrefresh,
        prerollback,
        postrollback,
        configure_clone,
        env_inst,
        single_thread,
        parallel,
        poll,
        config,
        log_file_path,
        port_num,
):
    """
    Provision a MS SQLServer VDB.
    """
    obj = DXIDatabase(
        engine=engine,
        single_thread=single_thread,
        poll=poll,
        config=config,
        log_file_path=log_file_path,
        parallel=parallel,
    )
    boolean_based_system_exit(
        obj.provision_mssql(
            group,
            source_name,
            db_name,
            env_name,
            timestamp=timestamp,
            timestamp_type=timestamp_type,
            prerefresh=prerefresh,
            postrefresh=postrefresh,
            prerollback=prerollback,
            postrollback=postrollback,
            configure_clone=configure_clone,
            env_inst=env_inst,
            port_num=port_num,
            mntpoint=mntpoint,
        )
    )


@provision.command()
@click.option("--source-name", required=True, help="The source database name.")
@click.option("--db-name", required=True, help="Name for the VDB.")
@click.option(
    "--env-name",
    required=True,
    help="The name of the Target environment in Delphix",
)
@click.option(
    "--group",
    required=True,
    help="The group into which Delphix will place the VDB",
)
@click.option(
    "--env-inst",
    help="The identifier of the instance in Delphix.",
    required=True,
)
@click.option(
    "--mntpoint",
    help="Mount folder that Delphix can use on the target host.",
    required=True,
)
@click.option("--port-num", help="The port number of the database instance.")
@click.option(
    "--timestamp-type",
    help="\b\nThe type of timestamp you are specifying.\n" "[TIME | SNAPSHOT]",
    default="SNAPSHOT",
)
@click.option(
    "--timestamp",
    help="""The Delphix semantic for the point in time on the source db or vfile 
    from which you want to refresh your VDB/vFile. \n
    Formats:                                                                      
    To use Latest Snapshot or Timepoint: LATEST                            
    To use a point in time:"YYYY-MM-DDTHH:MI:SS"                                           
    To use a snapshot name:"@YYYY-MM-DDTHH24:MI:SS.ZZZ"                                           
    To use snapshot time from GUI:"YYYY-MM-DDTHH:MI:SS"                                           
    [default: LATEST]      
    
    * A timestamp value should be in 24 hour format.     
    * Provided values should be enclosed in double quotes.                                                                
    """,
    default="LATEST",
)
@click.option(
    "--cdb-name",
    help="\b\nIf creating a CDB, name of the CDB.\n",
    required=False,
)
@click.option(
    "--logsync", help="Enable or disable logsync.", is_flag=True, default=True
)
@click.option(
    "--prerefresh",
    help="Hook name to run before a refresh only (not during initial provision). ",
    default=None,
)
@click.option(
    "--postrefresh",
    help="Hook name to run after a refresh only (runs after Configure Clone).",
    default=None,
)
@click.option(
    "--prerollback", help="Hook name to run before a rewind", default=None
)
@click.option(
    "--postrollback", help="Hook name to run after a rewind", default=None
)
@click.option(
    "--configure-clone",
    help="Hook name to run after initial provision and after a refresh.",
    default=None,
)
@click.option(
    "--engine",
    default=DXIDatabaseConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
         "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
         "[Default: {}]".format(DXIDatabaseConstants.SINGLE_THREAD),
    default=DXIDatabaseConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
         "[Default: {}s]".format(DXIDatabaseConstants.POLL),
    default=DXIDatabaseConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=DXIDatabaseConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=DXIDatabaseConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=DXIDatabaseConstants.LOG_FILE_PATH,
)
def oracle_mt(
        engine,
        source_name,
        db_name,
        group,
        mntpoint,
        env_name,
        timestamp,
        timestamp_type,
        prerefresh,
        postrefresh,
        prerollback,
        postrollback,
        configure_clone,
        env_inst,
        single_thread,
        parallel,
        poll,
        config,
        log_file_path,
        port_num,
        cdb_name,
        logsync,
):
    """
    Create an Oracle Multi Tenant VDB
    """
    obj = DXIDatabase(
        engine=engine,
        single_thread=single_thread,
        poll=poll,
        config=config,
        log_file_path=log_file_path,
        parallel=parallel,
    )
    boolean_based_system_exit(
        obj.provision_oracle_mt(
            group,
            source_name,
            db_name,
            env_name,
            cdb_name,
            logsync,
            timestamp=timestamp,
            timestamp_type=timestamp_type,
            prerefresh=prerefresh,
            postrefresh=postrefresh,
            prerollback=prerollback,
            postrollback=postrollback,
            configure_clone=configure_clone,
            env_inst=env_inst,
            port_num=port_num,
            mntpoint=mntpoint,
        )
    )


@provision.command()
@click.option("--source-name", required=True, help="The source database name.")
@click.option("--db-name", required=True, help="Name for the VDB.")
@click.option(
    "--env-name",
    required=True,
    help="The name of the Target environment in Delphix",
)
@click.option(
    "--group",
    required=True,
    help="The group into which Delphix will place the VDB",
)
@click.option(
    "--env-inst",
    help="The identifier of the instance in Delphix.",
    required=True,
)
@click.option(
    "--mntpoint",
    help="Mount folder that Delphix can use on the target host.",
    required=True,
)
@click.option(
    "--cdb-name",
    help="\b\nIf creating a CDB, name of the CDB.\n",
    required=False,
)
@click.option(
    "--nodes", required=False,
    help="\b\nColon separated list of nodes in RAC.\n"
         "[Required only if a CDB is being created]",
)
@click.option("--port-num", help="The port number of the database instance.")
@click.option(
    "--timestamp-type",
    help="\b\nThe type of timestamp you are specifying.\n" "[TIME | SNAPSHOT]",
    default="SNAPSHOT",
)
@click.option(
    "--timestamp",
    help="""The Delphix semantic for the point in time on the source db or vfile 
    from which you want to refresh your VDB/vFile. \n
    Formats:                                                                      
    To use Latest Snapshot or Timepoint: LATEST                            
    To use a point in time:"YYYY-MM-DDTHH:MI:SS"                                           
    To use a snapshot name:"@YYYY-MM-DDTHH24:MI:SS.ZZZ"                                           
    To use snapshot time from GUI:"YYYY-MM-DDTHH:MI:SS"                                           
    [default: LATEST]      

    * A timestamp value should be in 24 hour format.     
    * Provided values should be enclosed in double quotes.                                                                
    """,
    default="LATEST",
)
@click.option(
    "--logsync", help="Enable or disable logsync.", is_flag=True, default=True
)
@click.option(
    "--prerefresh",
    help="Hook name to run before a refresh only (not during initial provision). ",
    default=None,
)
@click.option(
    "--postrefresh",
    help="Hook name to run after a refresh only (runs after Configure Clone).",
    default=None,
)
@click.option(
    "--prerollback", help="Hook name to run before a rewind", default=None
)
@click.option(
    "--postrollback", help="Hook name to run after a rewind", default=None
)
@click.option(
    "--configure-clone",
    help="Hook name to run after initial provision and after a refresh.",
    default=None,
)
@click.option(
    "--engine",
    default=DXIDatabaseConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
         "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
         "[Default: {}]".format(DXIDatabaseConstants.SINGLE_THREAD),
    default=DXIDatabaseConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
         "[Default: {}s]".format(DXIDatabaseConstants.POLL),
    default=DXIDatabaseConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=DXIDatabaseConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=DXIDatabaseConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=DXIDatabaseConstants.LOG_FILE_PATH,
)
def oracle_mt_rac(
        engine,
        source_name,
        db_name,
        group,
        mntpoint,
        env_name,
        cdb_name,
        nodes,
        timestamp,
        timestamp_type,
        prerefresh,
        postrefresh,
        prerollback,
        postrollback,
        configure_clone,
        env_inst,
        single_thread,
        parallel,
        poll,
        config,
        log_file_path,
        port_num,
        logsync,
):
    """
    Create an Oracle Multi Tenant RAC VDB
    """
    obj = DXIDatabase(
        engine=engine,
        single_thread=single_thread,
        poll=poll,
        config=config,
        log_file_path=log_file_path,
        parallel=parallel,
    )
    boolean_based_system_exit(
        obj.provision_oracle_mt_rac(
            group,
            source_name,
            db_name,
            env_name,
            cdb_name,
            nodes,
            logsync,
            timestamp=timestamp,
            timestamp_type=timestamp_type,
            prerefresh=prerefresh,
            postrefresh=postrefresh,
            prerollback=prerollback,
            postrollback=postrollback,
            configure_clone=configure_clone,
            env_inst=env_inst,
            port_num=port_num,
            mntpoint=mntpoint,
        )
    )


@provision.command()
@click.option("--source-name", required=True, help="The source database")
@click.option("--db-name", required=True, help="Name of the VDB.")
@click.option(
    "--group",
    required=True,
    help="The group into which Delphix will place the VDB",
)
@click.option(
    "--env-name",
    required=True,
    help="The name of the Target environment in Delphix",
)
@click.option(
    "--env-inst",
    help="\b\nFull path of the database binary on the target host.",
    required=True,
)
@click.option(
    "--mntpoint",
    help="Mount folder that Delphix can use on the target host.",
    required=True,
)
@click.option(
    "--port-num",
    help="\b\nThe port number of the database instance.\n" "[default: 1521]",
    default=DXIDatabaseConstants.ORACLE_DEFAULT_PORT,
)
@click.option(
    "--timestamp-type",
    help="\b\nThe type of timestamp you are specifying.\n" "[TIME | SNAPSHOT]",
    default="SNAPSHOT",
)
@click.option(
    "--timestamp",
    help="""The Delphix semantic for the point in time on the source db or vfile 
    from which you want to refresh your VDB/vFile. \n
    Formats:                                                                      
    To use Latest Snapshot or Timepoint: LATEST                            
    To use a point in time:"YYYY-MM-DDTHH:MI:SS"                                           
    To use a snapshot name:"@YYYY-MM-DDTHH24:MI:SS.ZZZ"                                           
    To use snapshot time from GUI:"YYYY-MM-DDTHH:MI:SS"                                           
    [default: LATEST]      
    
    * A timestamp value should be in 24 hour format.     
    * Provided values should be enclosed in double quotes.                                                                
    """,
    default="LATEST",
)
@click.option(
    "--prerefresh",
    help="Hook name to run before a refresh only (not during initial provision). ",
    default=None,
)
@click.option(
    "--postrefresh",
    help="Hook name to run after a refresh only (runs after Configure Clone).",
    default=None,
)
@click.option(
    "--prerollback", help="Hook name to run before a rewind", default=None
)
@click.option(
    "--postrollback", help="Hook name to run after a rewind", default=None
)
@click.option(
    "--configure-clone",
    help="Hook name to run after initial provision and after a refresh.",
    default=None,
)
@click.option(
    "--engine",
    default=DXIDatabaseConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
         "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
         "[Default: {}]".format(DXIDatabaseConstants.SINGLE_THREAD),
    default=DXIDatabaseConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
         "[Default: {}s]".format(DXIDatabaseConstants.POLL),
    default=DXIDatabaseConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=DXIDatabaseConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=DXIDatabaseConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=DXIDatabaseConstants.LOG_FILE_PATH,
)
def oracle_si(
        engine,
        source_name,
        db_name,
        group,
        mntpoint,
        env_name,
        timestamp,
        timestamp_type,
        prerefresh,
        postrefresh,
        prerollback,
        postrollback,
        configure_clone,
        env_inst,
        single_thread,
        parallel,
        poll,
        config,
        log_file_path,
        port_num,
):
    """
    Create an Oracle SI VDB
    """
    obj = DXIDatabase(
        engine=engine,
        single_thread=single_thread,
        poll=poll,
        config=config,
        log_file_path=log_file_path,
        parallel=parallel,
    )
    boolean_based_system_exit(
        obj.provision_oracle_si(
            group,
            source_name,
            db_name,
            env_name,
            timestamp=timestamp,
            timestamp_type=timestamp_type,
            prerefresh=prerefresh,
            postrefresh=postrefresh,
            prerollback=prerollback,
            postrollback=postrollback,
            configure_clone=configure_clone,
            env_inst=env_inst,
            port_num=port_num,
            mntpoint=mntpoint,
        )
    )


@provision.command()
@click.option("--db-name", required=True, help="Name for the VDB/vFile.")
@click.option("--source-name", required=True, help="The source database.")
@click.option(
    "--group",
    required=True,
    help="The group into which Delphix will place the VDB.",
)
@click.option(
    "--env-name",
    required=True,
    help="The name of the target environment in Delphix.",
)
@click.option(
    "--env-inst",
    help="\b\nFull path of the database binary on the target host.",
    required=True,
)
@click.option("--port-num", help="The port number of the database instance.")
@click.option(
    "--timestamp-type",
    help="The type of timestamp you are specifying. TIME or SNAPSHOT",
    default="SNAPSHOT",
)
@click.option(
    "--timestamp",
    help="""The Delphix semantic for the point in time on the source db or vfile 
    from which you want to refresh your VDB/vFile. \n
    Formats:                                                                      
    To use Latest Snapshot or Timepoint: LATEST                            
    To use a point in time:"YYYY-MM-DDTHH:MI:SS"                                           
    To use a snapshot name:"@YYYY-MM-DDTHH24:MI:SS.ZZZ"                                           
    To use snapshot time from GUI:"YYYY-MM-DDTHH:MI:SS"                                           
    [default: LATEST]      
    
    * A timestamp value should be in 24 hour format.     
    * Provided values should be enclosed in double quotes.                                                                
    """,
    default="LATEST",
)
@click.option(
    "--mntpoint",
    help="Mount folder that Delphix can use on the target host.",
    default="/mnt/ingest",
)
@click.option(
    "--prerefresh",
    help="Hook name to run before a refresh only (not during initial provision). ",
    default=None,
)
@click.option(
    "--postrefresh",
    help="Hook name to run after a refresh only (runs after Configure Clone).",
    default=None,
)
@click.option(
    "--prerollback", help="Hook name to run before a rewind", default=None
)
@click.option(
    "--postrollback", help="Hook name to run after a rewind", default=None
)
@click.option(
    "--configure-clone",
    help="Hook name to run after initial provision and after a refresh.",
    default=None,
)
@click.option(
    "--engine",
    default=DXIDatabaseConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
         "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
         "[Default: {}]".format(DXIDatabaseConstants.SINGLE_THREAD),
    default=DXIDatabaseConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
         "[Default: {}s]".format(DXIDatabaseConstants.POLL),
    default=DXIDatabaseConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=DXIDatabaseConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=DXIDatabaseConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=DXIDatabaseConstants.LOG_FILE_PATH,
)
def postgres(
        engine,
        source_name,
        db_name,
        group,
        mntpoint,
        env_name,
        timestamp,
        timestamp_type,
        prerefresh,
        postrefresh,
        prerollback,
        postrollback,
        configure_clone,
        env_inst,
        single_thread,
        parallel,
        poll,
        config,
        log_file_path,
        port_num,
):
    """
    Provision a Postgres VDB.
    """
    obj = DXIDatabase(
        engine=engine,
        single_thread=single_thread,
        poll=poll,
        config=config,
        log_file_path=log_file_path,
        parallel=parallel,
    )
    boolean_based_system_exit(
        obj.provision_postgres(
            group,
            source_name,
            db_name,
            env_name,
            timestamp=timestamp,
            timestamp_type=timestamp_type,
            prerefresh=prerefresh,
            postrefresh=postrefresh,
            prerollback=prerollback,
            postrollback=postrollback,
            configure_clone=configure_clone,
            env_inst=env_inst,
            port_num=port_num,
            mntpoint=mntpoint,
        )
    )


@provision.command()
@click.option("--db-name", required=True, help="Name for the VDB.")
@click.option("--source-name", required=True, help="The source database")
@click.option(
    "--env-name",
    required=True,
    help="The name of the target environment for the VDB.",
)
@click.option(
    "--env-inst",
    help="\b\nFull path of the database binary on the target host.",
    required=True,
)
@click.option(
    "--group",
    required=True,
    help="The group into which Delphix will place the VDB.",
)
@click.option("--port-num", help="The port number of the database instance.")
@click.option(
    "--timestamp-type",
    help="\b\nThe type of timestamp you are specifying.\n" "[TIME | SNAPSHOT]",
    default="SNAPSHOT",
)
@click.option(
    "--timestamp",
    help="""The Delphix semantic for the point in time on the source db or vfile 
    from which you want to refresh your VDB/vFile. \n
    Formats:                                                                      
    To use Latest Snapshot or Timepoint: LATEST                            
    To use a point in time:"YYYY-MM-DDTHH:MI:SS"                                           
    To use a snapshot name:"@YYYY-MM-DDTHH24:MI:SS.ZZZ"                                           
    To use snapshot time from GUI:"YYYY-MM-DDTHH:MI:SS"                                           
    [default: LATEST]      
    
    * A timestamp value should be in 24 hour format.     
    * Provided values should be enclosed in double quotes.                                                                
    """,
    default="LATEST",
)
@click.option(
    "--mntpoint",
    help="Mount folder that Delphix can use on the target host.",
    default="/mnt/ingest",
)
@click.option(
    "--prerefresh",
    help="Hook name to run before a refresh only (not during initial provision). ",
    default=None,
)
@click.option(
    "--postrefresh",
    help="Hook name to run after a refresh only (runs after Configure Clone).",
    default=None,
)
@click.option(
    "--prerollback", help="Hook name to run before a rewind", default=None
)
@click.option(
    "--postrollback", help="Hook name to run after a rewind", default=None
)
@click.option(
    "--configure-clone",
    help="Hook name to run after initial provision and after a refresh.",
    default=None,
)
@click.option(
    "--engine",
    default=DXIDatabaseConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
         "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
         "[Default: {}]".format(DXIDatabaseConstants.SINGLE_THREAD),
    default=DXIDatabaseConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
         "[Default: {}s]".format(DXIDatabaseConstants.POLL),
    default=DXIDatabaseConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=DXIDatabaseConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=DXIDatabaseConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=DXIDatabaseConstants.LOG_FILE_PATH,
)
def vfiles(
        engine,
        source_name,
        db_name,
        group,
        mntpoint,
        env_name,
        timestamp,
        timestamp_type,
        prerefresh,
        postrefresh,
        prerollback,
        postrollback,
        configure_clone,
        env_inst,
        single_thread,
        parallel,
        poll,
        config,
        log_file_path,
        port_num,
):
    """
    Create a vfiles VDB.
    """
    obj = DXIDatabase(
        engine=engine,
        single_thread=single_thread,
        poll=poll,
        config=config,
        log_file_path=log_file_path,
        parallel=parallel,
    )
    boolean_based_system_exit(
        obj.provision_vfiles(
            group,
            source_name,
            db_name,
            env_name,
            timestamp=timestamp,
            timestamp_type=timestamp_type,
            prerefresh=prerefresh,
            postrefresh=postrefresh,
            prerollback=prerollback,
            postrollback=postrollback,
            configure_clone=configure_clone,
            env_inst=env_inst,
            port_num=port_num,
            mntpoint=mntpoint,
        )
    )


# provision oracle rac
@provision.command()
@click.option(
    "--group",
    required=True,
    help="The group into which Delphix will place the VDB",
)
@click.option("--source-name", required=True, help="The source database")
@click.option(
    "--db-name", required=True, help="The name you want to give the database"
)
@click.option(
    "--env-name",
    required=True,
    help="The name of the Target environment in Delphix",
)
@click.option(
    "--nodes", required=True, help="Colon separated list of nodes in RAC"
)
@click.option("--port-num", help="The port number of the database instance")
@click.option(
    "--env-inst",
    help="The identifier of the instance in Delphix.",
    default=None,
)
@click.option(
    "--timestamp-type",
    help="The type of timestamp you are specifying. TIME or SNAPSHOT",
    default="SNAPSHOT",
)
@click.option(
    "--timestamp",
    help="\bThe Delphix semantic for the point in time\n "
         "from which you want to ingest your VDB.",
    default="LATEST",
)
@click.option(
    "--mntpoint",
    help="The identifier of the instance in Delphix.",
    default="/mnt/provision",
)
@click.option(
    "--prerefresh",
    help="Hook name to run before a refresh only (not during initial provision). ",
    default=None,
)
@click.option(
    "--postrefresh",
    help="Hook name to run after a refresh only (runs after Configure Clone).",
    default=None,
)
@click.option(
    "--prerollback", help="Hook name to run before a rewind", default=None
)
@click.option(
    "--postrollback", help="Hook name to run after a rewind", default=None
)
@click.option(
    "--configure-clone",
    help="Hook name to run after initial provision and after a refresh.",
    default=None,
)
@click.option(
    "--engine",
    default=DXIDatabaseConstants.ENGINE_ID,
    help="\b\nName of Delphix Engine in the config file.\n"
         "[Default: default]",
)
@click.option(
    "--single-thread",
    help="\b\nRun as a single thread.\n"
         "[Default: {}]".format(DXIDatabaseConstants.SINGLE_THREAD),
    default=DXIDatabaseConstants.SINGLE_THREAD,
    is_flag=True,
)
@click.option(
    "--poll",
    type=click.INT,
    help="\b\nThe number of seconds to wait between job polls.\n"
         "[Default: {}s]".format(DXIDatabaseConstants.POLL),
    default=DXIDatabaseConstants.POLL,
)
@click.option(
    "--parallel",
    type=click.INT,
    help="Limit number of jobs to maxjob.",
    default=DXIDatabaseConstants.PARALLEL,
)
@click.option(
    "--config",
    help="The path to the dxtools.conf file.",
    default=DXIDatabaseConstants.CONFIG,
)
@click.option(
    "--log-file-path",
    help="The path to the logfile you want to use.",
    default=DXIDatabaseConstants.LOG_FILE_PATH,
)
def oracle_rac(
        engine,
        source_name,
        db_name,
        group,
        mntpoint,
        env_name,
        nodes,
        timestamp,
        timestamp_type,
        prerefresh,
        postrefresh,
        prerollback,
        postrollback,
        configure_clone,
        env_inst,
        single_thread,
        parallel,
        poll,
        config,
        log_file_path,
        port_num,
):
    """
    Create an Oracle RAC VDB
    """
    obj = DXIDatabase(
        engine=engine,
        single_thread=single_thread,
        poll=poll,
        config=config,
        log_file_path=log_file_path,
        parallel=parallel,
    )
    obj.provision_oracle_rac(
        group,
        source_name,
        db_name,
        env_name,
        nodes=nodes,
        timestamp=timestamp,
        timestamp_type=timestamp_type,
        prerefresh=prerefresh,
        postrefresh=postrefresh,
        prerollback=prerollback,
        postrollback=postrollback,
        configure_clone=configure_clone,
        env_inst=env_inst,
        port_num=port_num,
        mntpoint=mntpoint,
    )


database.add_command(provision)

if __name__ == "__main__":
    print(oracle_mt_rac())
