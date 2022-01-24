#!/usr/bin/env python3
#
# Copyright (c) 2021 by Delphix. All rights reserved.
#
"""
Link an ASE Sybase dSource
"""
from delphixpy.v1_10_2 import exceptions
from delphixpy.v1_10_2.web import database
from delphixpy.v1_10_2.web import environment
from delphixpy.v1_10_2.web import repository
from delphixpy.v1_10_2.web import vo
from dxi._lib import dlpx_exceptions
from dxi._lib import get_references
from .dsource_link import DsourceLink


class DsourceLinkASE(DsourceLink):
    """
    Derived class implementing linking of a ASE Sybase dSource
    """

    def __init__(
        self,
        dlpx_obj,
        dsource_name,
        db_passwd,
        db_user,
        dx_group,
        logsync,
        stage_repo,
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
        :param logsync: Enable logsync
        :type logsync: bool
        :param db_type: dSource type. mssql, sybase or oracle
        :type db_type: str
        """
        super().__init__(dsource_name, db_passwd, db_user, dx_group, logsync, dlpx_obj, 'sybase')
        self.stage_repo = stage_repo

    def link_ase_dsource(self, backup_path, bck_file, create_bckup, env_name, source_env):
        """
        Link an ASE dSource
        :param backup_path: Path to the ASE/MSSQL backups
        :type backup_path: str
        :param bck_file: Fully qualified name of backup file
        :type bck_file: str
        :param create_bckup: Create and ingest a new Sybase backup
        :type create_bckup: str
        :param env_name: Name of the environment where the dSource running
        :type env_name: str
        """
        link_params = super().dsource_prepare_link()
        link_params.link_data.load_backup_path = backup_path
        if bck_file:
            link_params.link_data.sync_parameters = (
                vo.ASESpecificBackupSyncParameters()
            )
            bck_files = bck_file.split(" ")
            link_params.link_data.sync_parameters.backup_files = bck_files
        elif create_bckup:
            link_params.link_data.sync_parameters = (
                vo.ASENewBackupSyncParameters()
            )
        else:
            link_params.link_data.sync_parameters = (
                vo.ASELatestBackupSyncParameters()
            )
        try:

            env_user_ref_staging = (
                link_params.link_data.stage_user
            ) = get_references.find_obj_by_name(
                self.dlpx_obj.server_session, environment, env_name
            ).primary_user
            env_ref = get_references.find_obj_by_name(
                self.dlpx_obj.server_session, environment, env_name)
            link_params.link_data.staging_host_user = env_user_ref_staging

            env_user_ref_source =  get_references.find_obj_by_name(
                self.dlpx_obj.server_session, environment, source_env
            ).primary_user

            link_params.link_data.source_host_user = env_user_ref_source
            link_params.link_data.staging_repository = get_references.find_obj_by_name(  # noqa
                self.dlpx_obj.server_session, repository, self.stage_repo, env_name=env_ref.reference
            ).reference

        except dlpx_exceptions.DlpxException as err:
            raise dlpx_exceptions.DlpxException(
                f"Could not link {self.dsource_name}:\n{err}"
            )
        try:
            dsource_ref = database.link(
                self.dlpx_obj.server_session, link_params
            )
            print(f"{dsource_ref} successfully linked {self.dsource_name}")
        except (exceptions.RequestError, exceptions.HttpError) as err:
            raise dlpx_exceptions.DlpxException(
                f"Database link failed for {self.dsource_name}:\n{err}"
            )
