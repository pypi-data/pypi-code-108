#!/usr/bin/env python3
#
# Copyright (c) 2021 by Delphix. All rights reserved.
#

"""
Link a MSSQL dSource
"""
from delphixpy.v1_10_2 import exceptions
from delphixpy.v1_10_2.web import database
from delphixpy.v1_10_2.web import environment
from delphixpy.v1_10_2.web import vo
from dxi._lib import dlpx_exceptions
from dxi._lib import get_references
from dxi._lib import dx_logging
from .dsource_link import DsourceLink


class DsourceLinkMssql(DsourceLink):
    """
    Derived class implementing linking of a MSSQL dSource
    """

    def __init__(
        self,
        dlpx_obj,
        dsource_name,
        db_passwd,
        db_user,
        dx_group,
        logsync,
        env_name,
        validated_sync_mode,
        initial_load_type,
        delphix_managed=True,
    ):
        """
        Constructor method
        :param dlpx_obj: A Delphix DDP session object
        :type dlpx_obj: lib.get_session.GetSession
        :param dsource_name: Name of the dsource
        :type dsource_name: str
        :param dx_group: Group name of where the dSource will reside
        :type dx_group: str
        :param db_passwd: Password of the db_user
        :type db_passwd: str
        :param db_user: Username of the dSource
        :type db_user: str
        :param db_type: dSource type. mssql, sybase or oracle
        :type db_type: str
        """
        super().__init__(dsource_name, db_passwd, db_user, dx_group, logsync, dlpx_obj, 'mssql')
        self.env_name = env_name
        self.validated_sync_mode = validated_sync_mode
        self.initial_load_type = initial_load_type
        self.delphix_managed = delphix_managed
        if delphix_managed:
            self.initial_load_type = "COPY_ONLY"

    def link_mssql_dsource(
        self,
        source_env,
        stage_env,
        stage_instance,
        backup_path,
        backup_loc_passwd,
        backup_loc_user,
        uuid,
    ):
        """
        Link an MSSQL dSource
        :param stage_env: Name of the staging environment
        :type stage_env: str
        :param stage_instance: Name if the staging database instance
        :type stage_instance: str
        :param backup_path: Directory of where the backup is located
        :type backup_path: str
        :param backup_loc_passwd: Password of the shared backup path
        :type backup_loc_passwd: str
        :param backup_loc_user: Username for the shared backup path
        :type backup_loc_user: str
        """
        link_params = super().dsource_prepare_link(source_env_name=source_env)
        if self.delphix_managed:
            link_params.link_data.ingestion_strategy = (
                vo.DelphixManagedBackupIngestionStrategy()
            )
            link_params.link_data.ingestion_strategy.backup_policy = "PRIMARY"
            link_params.link_data.ingestion_strategy.compression_enabled = (
                False
            )
        else:
            link_params.link_data.ingestion_strategy = (
                vo.ExternalBackupIngestionStrategy()
            )
            link_params.link_data.ingestion_strategy.validated_sync_mode = (
                self.validated_sync_mode
            )
        link_params.link_data.sourcing_policy = vo.SourcingPolicy()
        link_params.link_data.sourcing_policy.logsync_enabled = False
        if (
            self.validated_sync_mode
            and self.validated_sync_mode == "TRANSACTION_LOG"
        ):
            link_params.link_data.sourcing_policy.logsync_enabled = (
                self.logsync
            )
        try:
            env_obj_ref = get_references.find_obj_by_name(
                self.dlpx_obj.server_session, environment, stage_env
            ).reference
            ppt_repo_ref = get_references.find_db_repo(
                self.dlpx_obj.server_session,
                "MSSqlInstance",
                env_obj_ref,
                stage_instance,
            )
            link_params.link_data.ppt_repository = ppt_repo_ref
        except dlpx_exceptions.DlpxException as err:
            raise dlpx_exceptions.DlpxException(
                f"Could not link {self.dsource_name}:\n{err}"
            )
        # specifying backup locations
        link_params.link_data.shared_backup_locations = []
        if backup_path and backup_path != "auto":
            link_params.link_data.shared_backup_locations = backup_path.split(
                ":"
            )
        if backup_loc_passwd:
            link_params.link_data.backup_location_credentials = (
                vo.PasswordCredential()
            )
            link_params.link_data.backup_location_credentials.password = (
                backup_loc_passwd
            )
            link_params.link_data.backup_location_user = backup_loc_user
        # specify the initial sync Parameters
        if self.initial_load_type and self.initial_load_type == "SPECIFIC":
            link_params.link_data.sync_parameters = (
                vo.MSSqlExistingSpecificBackupSyncParameters()
            )
            link_params.link_data.sync_parameters.backup_uuid = uuid
        elif self.initial_load_type and self.initial_load_type == "COPY_ONLY":
            link_params.link_data.sync_parameters = (
                vo.MSSqlNewCopyOnlyFullBackupSyncParameters()
            )
            link_params.link_data.sync_parameters.backup_policy = "PRIMARY"
            link_params.link_data.sync_parameters.compression_enabled = False
        else:
            link_params.link_data.sync_parameters = (
                vo.MSSqlExistingMostRecentBackupSyncParameters()
            )
        try:
            database.link(self.dlpx_obj.server_session, link_params)
        except (
            exceptions.HttpError,
            exceptions.RequestError,
            exceptions.JobError,
        ) as err:
            dlpx_exceptions.DlpxException(
                f"Database link failed for {self.dsource_name}:{err}"
            )

