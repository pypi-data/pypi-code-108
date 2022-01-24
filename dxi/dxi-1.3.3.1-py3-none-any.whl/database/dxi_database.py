#
# Copyright (c) 2021 by Delphix. All rights reserved.
#

from dxi._lib.util import DXIConfigConstantsHelper
from dxi.database._internal_lib._dxi_db import DXIDb
from dxi.database._internal_lib._dxi_ingest import DXIDsource
from dxi.database._internal_lib._dxi_provision import DXIVdb


class DXIDatabaseConstants(object):
    """
    Class of common constants used by Provision dSource
    """

    SINGLE_THREAD = False
    POLL = 10
    CONFIG = DXIConfigConstantsHelper().get_config()
    LOG_FILE_PATH = DXIConfigConstantsHelper().get_logdir()
    ENGINE_ID = "default"
    PARALLEL = 5
    ACTION = None
    MODULE_NAME = __name__
    VDB_LIST_HEADER = []
    FORCE = False
    TYPE = "vdb"
    ORACLE_DEFAULT_PORT = "1521"


class DXIDatabase(object):
    """
    A class which use to perform all data set related operations:
    Refresh, Ingest, Provision, Start, Stop, Disable, Enable
    """

    def __init__(self, *args, **kwargs):
        """
        Args:
            engine: Name of the database.
            single_thread: Name of the group, if specifying one.
            config: The path to the dxtools.conf file
            log_file_path: The path to the logfile you want to use.
            poll: The number of seconds to wait between job polls .
        """
        kwargs.setdefault("engine", DXIDatabaseConstants.ENGINE_ID)
        kwargs.setdefault("log_file_path", DXIDatabaseConstants.LOG_FILE_PATH)
        kwargs.setdefault("config", DXIDatabaseConstants.CONFIG)
        kwargs.setdefault("poll", DXIDatabaseConstants.POLL)
        kwargs.setdefault("single_thread", DXIDatabaseConstants.SINGLE_THREAD)
        kwargs.setdefault("parallel", DXIDatabaseConstants.PARALLEL)
        kwargs.setdefault("module_name", DXIDatabaseConstants.MODULE_NAME)
        self._ingest = DXIDsource(**kwargs)
        self._provision = DXIVdb(**kwargs)
        self._db_common = DXIDb(**kwargs)

    # all methods related to common db operations
    def list(self):
        """
        List all data sets on a Delphix Engine.
        Raises:
            General Exception
        Returns:
            boolean: Indicates success or failure of the operation.
        """
        return self._db_common.list()

    def start(self, db_name, group=None):
        """
        Start a virtual dataset.

        Args:
            db_name: Name of the database.
            group: Name of the group, if specifying one.
        Raises:
            General Exception
        Returns:
            boolean: Indicates success or failure of the operation.
        """
        return self._db_common.start(db_name, group)

    def stop(self, db_name, group=None):
        """
        Stop a vitual dataset.
        Args:
            db_name: Name of the database.
            group: Name of the group, if specifying one.
        Raises:
            General Exception
        Returns:
            boolean: Indicates success or failure of the operation.
        """
        return self._db_common.stop(db_name, group)

    def enable(self, db_name, group=None):
        """
        Enable a virtual database.
        Args:
            db_name: Name of the database.
            group: Name of the group, if specifying one.
        Raises:
            General Exception
        Returns:
            boolean: Indicates success or failure of the operation.
        """
        return self._db_common.enable(db_name, group)

    def disable(self, db_name, group=None, force=False):
        """
        Disable a virtual database.
        Args:
            db_name: Name of the database.
            group: Name of the group, if specifying one.
        Raises:
            General Exception
        Returns:
            boolean: Indicates success or failure of the operation.
        """
        return self._db_common.disable(db_name, group, force)

    def refresh(
        self,
        db_name,
        timestamp_type="SNAPSHOT",
        timestamp="LATEST",
        timeflow="None",
    ):
        """
        Refresh a Delphix VDB or vFile.
        Args:
            db_name: Name of the database to refresh.
            timestamp_type: Type of timestamp to use for refresh.
                            SNAPSHOT | TIME
            timestamp: Timestamp reference for refresh.
            timeflow: Name of the timeflow for the refresh.
        Raises:
            General Exception
        Returns:
            boolean: Indicates success or failure of the operation.
        """
        return self._provision.refresh(
            db_name, timestamp_type, timestamp, timeflow
        )

    def delete(self, db_name, db_type="vdb", force=False):
        """
        Delete a virtual or physical dataset
        Args:
            db_name: Name of the database/databases.
            db_type: Type of database. vdb/dsource
            force: Whether to force delete the datasets.
        Raises:
            General Exception
        Returns:
            boolean: Indicates success or failure of the operation.
        """
        return self._provision.delete(db_name, db_type, force)

    def rewind(
        self,
        db_name,
        timestamp_type="SNAPSHOT",
        timestamp="LATEST",
        db_type=None,
    ):
        """
        Rewind a virtual dataset.
        Args:
            db_name: Name of the database/databases.
            timestamp_type: Type of timestamp to use for refresh.
                            SNAPSHOT | TIME
            timestamp: Timestamp reference for refresh.
            timeflow: Name of the timeflow for the refresh.
        Raises:
            General Exception
        Returns:
            boolean: Indicates success or failure of the operation.
        """
        return self._provision.rewind(
            db_name, timestamp_type, timestamp, db_type
        )

    def provision_postgres(
        self,
        group,
        source_name,
        db_name,
        env_name,
        prerefresh=False,
        postrefresh=False,
        prerollback=False,
        postrollback=False,
        configure_clone=False,
        port_num=5432,
        timestamp_type="SNAPSHOT",
        timestamp="LATEST",
        mntpoint="/mnt/ingest",
        env_inst=None,
    ):
        """
        Provision a Postgres VDB.
        Args:
            db_name           Name for the VDB/vFile.
            source_name       The source database.
            env_name         The name of the target environment in Delphix.
            port_num          The port number of the database instance.
            env_inst          Full path to database binary on target.
            group             The group into which Delphix will place the VDB.
            timestamp_type    The type of timestamp [TIME | SNAPSHOT]
            timestamp         The point in time on the source db or vfile
            mntpoint          Mount folder that Delphix can use on the target
            prerefresh        Hook name to run before a refresh only
            postrefresh       Hook name to run after a refresh only
            prerollback       Hook name to run before a rewind
            postrollback      Hook name to run after a rewind
            configure_clone   Hook name to run after provision/refresh.
        Raises:
            General Exception
        Returns:
            boolean: Indicates success or failure of the operation.
        """
        return self._provision.provision_postgres(
            group,
            source_name,
            db_name,
            env_name,
            prerefresh,
            postrefresh,
            prerollback,
            postrollback,
            configure_clone,
            port_num,
            timestamp_type,
            timestamp,
            mntpoint,
            env_inst,
        )

    def provision_ase(
        self,
        group,
        source_name,
        db_name,
        env_name,
        prerefresh=False,
        postrefresh=False,
        prerollback=False,
        postrollback=False,
        configure_clone=False,
        port_num=5432,
        timestamp_type="SNAPSHOT",
        timestamp="LATEST",
        mntpoint="/mnt/ingest",
        env_inst=None,
        no_truncate_log=False,
    ):
        """
        Provision a ASE VDB.
        Args:
            db_name           Name for the VDB/vFile.
            source_name       The source database.
            env_name         The name of the target environment in Delphix.
            port_num          The port number of the database instance.
            env_inst          Full path to database binary on target.
            group             The group into which Delphix will place the VDB.
            timestamp_type    The type of timestamp [TIME | SNAPSHOT]
            timestamp         The point in time on the source db or vfile
            mntpoint          Mount folder that Delphix can use on the target
            prerefresh        Hook name to run before a refresh only
            postrefresh       Hook name to run after a refresh only
            prerollback       Hook name to run before a rewind
            postrollback      Hook name to run after a rewind
            configure_clone   Hook name to run after provision/refresh.
            no_truncate_log   Set the trunc log on chkpt database option
        Raises:
            General Exception
        Returns:
            boolean: Indicates success or failure of the operation.
        """
        return self._provision.provision_ase(
            group,
            source_name,
            db_name,
            env_name,
            prerefresh,
            postrefresh,
            prerollback,
            postrollback,
            configure_clone,
            port_num,
            timestamp_type,
            timestamp,
            mntpoint,
            env_inst,
            no_truncate_log,
        )

    def provision_mssql(
        self,
        group,
        source_name,
        db_name,
        env_name,
        prerefresh=False,
        postrefresh=False,
        prerollback=False,
        postrollback=False,
        configure_clone=False,
        port_num=5432,
        timestamp_type="SNAPSHOT",
        timestamp="LATEST",
        mntpoint="/mnt/ingest",
        env_inst=None,
    ):
        """
        Provision a MSSQL VDB.
        Args:
            db_name           Name for the VDB/vFile.
            source_name       The source database.
            env_name         The name of the target environment in Delphix.
            port_num          The port number of the database instance.
            env_inst          Full path to database binary on target.
            group             The group into which Delphix will place the VDB.
            timestamp_type    The type of timestamp [TIME | SNAPSHOT]
            timestamp         The point in time on the source db or vfile
            mntpoint          Mount folder that Delphix can use on the target
            prerefresh        Hook name to run before a refresh only
            postrefresh       Hook name to run after a refresh only
            prerollback       Hook name to run before a rewind
            postrollback      Hook name to run after a rewind
            configure_clone   Hook name to run after provision/refresh.
        Raises:
            General Exception
        Returns:
            boolean: Indicates success or failure of the operation.
        """
        return self._provision.provision_mssql(
            group,
            source_name,
            db_name,
            env_name,
            prerefresh,
            postrefresh,
            prerollback,
            postrollback,
            configure_clone,
            port_num,
            timestamp_type,
            timestamp,
            mntpoint,
            env_inst,
        )

    def provision_vfiles(
        self,
        group,
        source_name,
        db_name,
        env_name,
        prerefresh=False,
        postrefresh=False,
        prerollback=False,
        postrollback=False,
        configure_clone=False,
        port_num=5432,
        timestamp_type="SNAPSHOT",
        timestamp="LATEST",
        mntpoint="/mnt/ingest",
        env_inst=None,
    ):
        """
        Create a vfiles VDB
        Args:
            db_name           Name for the VDB/vFile.
            source_name       The source database.
            env_name         The name of the target environment in Delphix.
            port_num          The port number of the database instance.
            env_inst          Full path to database binary on target.
            group             The group into which Delphix will place the VDB.
            timestamp_type    The type of timestamp [TIME | SNAPSHOT]
            timestamp         The point in time on the source db or vfile
            mntpoint          Mount folder that Delphix can use on the target
            prerefresh        Hook name to run before a refresh only
            postrefresh       Hook name to run after a refresh only
            prerollback       Hook name to run before a rewind
            postrollback      Hook name to run after a rewind
            configure_clone   Hook name to run after provision/refresh.
        Raises:
            General Exception
        Returns:
            boolean: Indicates success or failure of the operation.

        """
        return self._provision.provision_vfiles(
            group,
            source_name,
            db_name,
            env_name,
            prerefresh,
            postrefresh,
            prerollback,
            postrollback,
            configure_clone,
            port_num,
            timestamp_type,
            timestamp,
            mntpoint,
            env_inst,
        )

    def provision_oracle_si(
        self,
        group,
        source_name,
        db_name,
        env_name,
        prerefresh=False,
        postrefresh=False,
        prerollback=False,
        postrollback=False,
        configure_clone=False,
        port_num=5432,
        timestamp_type="SNAPSHOT",
        timestamp="LATEST",
        mntpoint="/mnt/ingest",
        env_inst=None,
    ):
        """
        Create an Oracle SI VDB
        Args:
            db_name           Name for the VDB/vFile.
            source_name       The source database.
            env_name         The name of the target environment in Delphix.
            port_num          The port number of the database instance.
            env_inst          Full path to database binary on target.
            group             The group into which Delphix will place the VDB.
            timestamp_type    The type of timestamp [TIME | SNAPSHOT]
            timestamp         The point in time on the source db or vfile
            mntpoint          Mount folder that Delphix can use on the target
            prerefresh        Hook name to run before a refresh only
            postrefresh       Hook name to run after a refresh only
            prerollback       Hook name to run before a rewind
            postrollback      Hook name to run after a rewind
            configure_clone   Hook name to run after provision/refresh.
        Raises:
            General Exception
        Returns:
            boolean: Indicates success or failure of the operation.

        """
        return self._provision.provision_oracle_si(
            group,
            source_name,
            db_name,
            env_name,
            prerefresh,
            postrefresh,
            prerollback,
            postrollback,
            configure_clone,
            port_num,
            timestamp_type,
            timestamp,
            mntpoint,
            env_inst,
        )

    def provision_oracle_mt(
        self,
        group,
        source_name,
        db_name,
        env_name,
        cdb_name,
        logsync,
        prerefresh=False,
        postrefresh=False,
        prerollback=False,
        postrollback=False,
        configure_clone=False,
        port_num=1521,
        timestamp_type="SNAPSHOT",
        timestamp="LATEST",
        mntpoint="/mnt/ingest",
        env_inst=None,
    ):
        """
        Create an Oracle Multi Tenant VDB
        Args:
            db_name           Name for the VDB/vFile.
            source_name       The source database.
            env_name         The name of the target environment in Delphix.
            port_num          The port number of the database instance.
            env_inst          Full path to database binary on target.
            group             The group into which Delphix will place the VDB.
            timestamp_type    The type of timestamp [TIME | SNAPSHOT]
            timestamp         The point in time on the source db or vfile
            mntpoint          Mount folder that Delphix can use on the target
            prerefresh        Hook name to run before a refresh only
            postrefresh       Hook name to run after a refresh only
            prerollback       Hook name to run before a rewind
            postrollback      Hook name to run after a rewind
            configure_clone   Hook name to run after provision/refresh.
            cdb_name          Creates a CDB along with PDB
        Raises:
            General Exception
        Returns:
            boolean: Indicates success or failure of the operation.

        """
        return self._provision.provision_oracle_mt(
            group,
            source_name,
            db_name,
            env_name,
            cdb_name,
            logsync,
            prerefresh,
            postrefresh,
            prerollback,
            postrollback,
            configure_clone,
            port_num,
            timestamp_type,
            timestamp,
            mntpoint,
            env_inst,
        )

    def provision_oracle_rac(
        self,
        group,
        source_name,
        db_name,
        env_name,
        nodes,
        prerefresh=False,
        postrefresh=False,
        prerollback=False,
        postrollback=False,
        configure_clone=False,
        port_num=1521,
        timestamp_type="SNAPSHOT",
        timestamp="LATEST",
        mntpoint="/mnt/provision",
        env_inst=None,
    ):
        """
        Create an Oracle RAC VDB
        Args:
            group             The group into which Delphix will place the VDB
            source-name       The source database.
            db-name           The name you want to give the database.
            env-name          The name of the Target environment in Delphix
            nodes             Colon separated list of nodes in RAC.
            port-num          The port number of the database instance
            prerefresh        Hook name to run before a refresh only
            postrefresh       Hook name to run after a refresh only
            prerollback       Hook name to run before a rewind
            postrollback      Hook name to run after a rewind
            configure_clone   Hook name to run after provision/refresh.
            env-inst          The identifier of the instance in Delphix.
            timestamp-type    The type of timestamp you are specifying. TIME or
            timestamp        The Delphix semantic for the point in time from
            mntpoint          The identifier of the instance in Delphix.
        Raises:
            General Exception
        Returns:
            boolean: Indicates success or failure of the operation.

        """
        return self._provision.provision_oracle_rac(
            group,
            source_name,
            db_name,
            env_name,
            nodes,
            prerefresh,
            postrefresh,
            prerollback,
            postrollback,
            configure_clone,
            port_num,
            timestamp_type,
            timestamp,
            mntpoint,
            env_inst,
        )

    def provision_oracle_mt_rac(
        self,
        group,
        source_name,
        db_name,
        env_name,
        cdb_name,
        nodes,
        logsync,
        prerefresh=False,
        postrefresh=False,
        prerollback=False,
        postrollback=False,
        configure_clone=False,
        port_num=1521,
        timestamp_type="SNAPSHOT",
        timestamp="LATEST",
        mntpoint="/mnt/provision",
        env_inst=None,
    ):
        """
        Create an Oracle MT RAC VDB
        Args:
            group             The group into which Delphix will place the VDB
            source-name       The source database.
            db-name           The name you want to give the database.
            env-name          The name of the Target environment in Delphix
            port-num          The port number of the database instance
            cdb-name          Name of the CDB to create with the PDB
            prerefresh        Hook name to run before a refresh only
            postrefresh       Hook name to run after a refresh only
            prerollback       Hook name to run before a rewind
            postrollback      Hook name to run after a rewind
            configure_clone   Hook name to run after provision/refresh.
            env-inst          The identifier of the instance in Delphix.
            timestamp-type    The type of timestamp you are specifying. TIME or
            timestamp        The Delphix semantic for the point in time from
            mntpoint          The identifier of the instance in Delphix.
        Raises:
            General Exception
        Returns:
            boolean: Indicates success or failure of the operation.

        """
        return self._provision.provision_oracle_mt_rac(
            group,
            source_name,
            db_name,
            env_name,
            cdb_name,
            nodes,
            logsync,
            prerefresh,
            postrefresh,
            prerollback,
            postrollback,
            configure_clone,
            port_num,
            timestamp_type,
            timestamp,
            mntpoint,
            env_inst,
        )

    # dSource methods
    def ingest_mssql(
        self,
        source_name,
        db_password,
        db_user,
        group,
        source_env,
        stage_env,
        stage_instance,
        logsync=True,
        validated_sync_mode="TRANSACTION_LOG",
        initial_load_type=None,
        delphix_managed=True,
        backup_path=None,
        backup_user_pwd=None,
        backup_user=None,
    ):
        """
        Link an MSSQL dSource
        Args:
            source_name           Name of the dSource to create.
            db_user               Dsource database username.
            db_passwd             Password for db_user.
            group                 Group name for this dSource.
            logsync               Enable or disable logsync
            source_env            Name of the source Db environment.
            stage_instance        Name of the staging instance for ingestion.
            stage_env             Name of the staging environment.
            backup_user_pwd       Password of the shared backup path.
            backup_user           User of the shared backup path
            validated_sync_mode   Validated Sync Mode to create the dsource.
            delphix_managed       If set, Delphix will manage the backups.
            initial_load_type     Initial load to create the MSSQL dsource.
            backup_path           Full path to the MS SQLServer backups
        Raises:
            General Exception
        Returns:
            boolean: Indicates success or failure of the operation.

        """
        return self._ingest.ingest_mssql(
            source_name,
            db_password,
            db_user,
            group,
            logsync,
            validated_sync_mode,
            initial_load_type,
            delphix_managed,
            stage_env,
            stage_instance,
            backup_path,
            backup_user_pwd,
            backup_user,
            source_env,
        )

    def ingest_sybase(
        self,
        source_name,
        db_user,
        db_password,
        group,
        source_env,
        stage_env,
        stage_instance,
        backup_path,
        backup_files=None,
        logsync=False,
        create_backup=None,
    ):
        """
        Link an Sybase dSource
        Args:
            source_name     Name of the dSource to create.
            db_user         Source database username.
            db_password     Password for db_user.
            group           Group name for this dSource
            env_name        Staging environment name
            source_env      Source environment name
            stage_instance  The sybase instance on the staging environment.
            backup_path     Path to the Sybase backups.
            logsync         Enable or disable logsync.
            backup_file     Backup file list (add space between multiple files)
            create_backup   The parameters to use as input to sync a SAP ASE
        Raises:
            General Exception
        Returns:
            boolean: Indicates success or failure of the operation.

        """
        return self._ingest.ingest_sybase(
            source_name,
            db_user,
            db_password,
            group,
            source_env,
            stage_env,
            stage_instance,
            backup_path,
            backup_files,
            logsync,
            create_backup,
        )

    def ingest_oracle(
        self,
        source_name,
        db_password,
        db_user,
        group,
        env_inst,
        logsync=True,
        env_name=None,
        ip_addr=None,
        port_num=None,
        rman_channels=2,
        files_per_set=5,
        num_connections=5,
    ):
        """
        Link an Oracle dSource
        Args:
            source_name     Name of the dSource to create.
            db_user         Dsource db username.
            db_password     Password for dsource db_user.
            group           Group name for the dsource.
            env_name        Name of the host environment for the dsource.
            env_inst        Path to oracle installation on the env.
            port_num        Port number for the oracle listener.
            logsync         Enable or disable logsync.
            ip_addr         IP Address of the dsource.
            rman_channels    Sets number of Oracle RMAN Channels.
            files_per_set    Sets number of files per set for Oracle.
            num_connections  Sets number of connections for Oracle RMAN.
        Raises:
            General Exception
        Returns:
            boolean: Indicates success or failure of the operation.

        """
        return self._ingest.ingest_oracle(
            source_name,
            db_password,
            db_user,
            group,
            logsync,
            env_name,
            env_inst,
            ip_addr,
            port_num,
            rman_channels,
            files_per_set,
            num_connections,
        )

    def ingest_oracle_mt_rac(
        self,
        source_name,
        db_password,
        db_user,
        group,
        env_inst,
        logsync=True,
        env_name=None,
        rman_channels=2,
        files_per_set=5,
        num_connections=5,
    ):
        """
        Link an Oracle MT RAC dSource
        Args:
            source_name     Name of the dSource to create.
            db_user         Dsource db username.
            db_password     Password for dsource db_user.
            group           Group name for the dsource.
            env_name        Name of the host environment for the dsource.
            env_inst        Path to oracle installation on the env.
            logsync         Enable or disable logsync.
            rman_channels    Sets number of Oracle RMAN Channels.
            files_per_set    Sets number of files per set for Oracle.
            num_connections  Sets number of connections for Oracle RMAN.
        Raises:
            General Exception
        Returns:
            boolean: Indicates success or failure of the operation.

        """
        return self._ingest.ingest_oracle_mt_rac(
            source_name,
            db_password,
            db_user,
            group,
            logsync,
            env_name,
            env_inst,
            rman_channels,
            files_per_set,
            num_connections,
        )
