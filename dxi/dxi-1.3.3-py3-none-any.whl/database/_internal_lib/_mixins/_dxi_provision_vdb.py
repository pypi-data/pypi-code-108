#
# Copyright (c) 2021 by Delphix. All rights reserved.
#

"""
Provision Delphix Virtual Databases
"""
import random
import string

from delphixpy.v1_10_2 import exceptions
from delphixpy.v1_10_2.web import database
from delphixpy.v1_10_2.web import environment
from delphixpy.v1_10_2.web import group
from delphixpy.v1_10_2.web import repository
from delphixpy.v1_10_2.web import sourceconfig
from delphixpy.v1_10_2.web import vo
from delphixpy.v1_10_2.web.environment.oracle import clusternode
from delphixpy.v1_10_2.web.source.operationTemplate import operationTemplate
from dxi._lib import dlpx_exceptions as dxe
from dxi._lib import dx_logging as log
from dxi._lib import dx_timeflow as dxtf
from dxi._lib import get_references as ref


def _add_hook(hooks_name, dlpx_obj):
    hook_references = []
    if hooks_name:
        for hook in hooks_name.split(","):
            template = ref.find_obj_by_name(
                dlpx_obj.server_session, operationTemplate, hook.strip()
            )
            hook_references.append(
                template.operation
            )  # Searching for operation object
    return hook_references


class _ProvisionVDBMixin(object):
    def _provision_ase_vdb(self, dlpx_obj):
        """
        Create a Sybase ASE VDB
        :param dlpx_obj: DDP session object
        :type dlpx_obj: lib.GetSession.GetSession object
        :param no_truncate_log: Don't truncate log on checkpoint
        :type no_truncate_log: bool
        :return:
        """
        group_ref, environment_obj, source_obj = self._find_group_source_environment_data(  # noqa
            dlpx_obj
        )
        engine_name = list(dlpx_obj.dlpx_ddps)[0]
        dxtf_obj = dxtf.DxTimeflow(dlpx_obj.server_session)
        vdb_params = vo.ASEProvisionParameters()
        vdb_params.container = vo.ASEDBContainer()
        if self.no_truncate_log:
            vdb_params.truncate_log_on_checkpoint = True
        else:
            vdb_params.truncate_log_on_checkpoint = False
        vdb_params.container.group = group_ref
        vdb_params.container.name = self.name
        vdb_params.source = vo.ASEVirtualSource()
        vdb_params.source.allow_auto_vdb_restart_on_host_reboot = True
        vdb_params.source_config = vo.ASESIConfig()
        vdb_params.source_config.database_name = self.name
        vdb_params.source_config.repository = ref.find_obj_by_name(
            dlpx_obj.server_session, repository, self.envinst
        ).reference
        vdb_params.timeflow_point_parameters = dxtf_obj.set_timeflow_point(
            source_obj,
            self.timestamp_type,
            self.timestamp,
            engine_session_ref=dlpx_obj.server_session,
        )
        vdb_params.timeflow_point_parameters.container = source_obj.reference
        log.print_info(f"{engine_name} provisioning {self.name}")
        database.provision(dlpx_obj.server_session, vdb_params)
        # Add the job into the jobs dictionary so we can track its progress
        self._add_last_job_to_track(dlpx_obj)

    def _provision_mssql_vdb(self, dlpx_obj):
        """
        Create a MSSQL VDB
        :param dlpx_obj: DDP session object
        :type dlpx_obj: lib.GetSession.GetSession object
        """
        group_ref, environment_obj, source_obj = self._find_group_source_environment_data(  # noqa
            dlpx_obj
        )
        engine_name = list(dlpx_obj.dlpx_ddps)[0]
        timeflow_obj = dxtf.DxTimeflow(dlpx_obj.server_session)
        vdb_params = vo.MSSqlProvisionParameters()
        vdb_params.container = vo.MSSqlDatabaseContainer()
        vdb_params.container.group = group_ref
        vdb_params.container.name = self.name
        vdb_params.source = vo.MSSqlVirtualSource()
        vdb_params.source.allow_auto_vdb_restart_on_host_reboot = False
        vdb_params.source_config = vo.MSSqlSIConfig()
        vdb_params.source_config.database_name = self.name

        vdb_params.source.parameters = {}
        vdb_params.source.operations = vo.VirtualSourceOperations()
        vdb_params = self._set_vdb_params(vdb_params, dlpx_obj)

        vdb_params.source_config.repository = ref.find_obj_by_name(
            dlpx_obj.server_session, repository, self.envinst
        ).reference
        vdb_params.timeflow_point_parameters = timeflow_obj.set_timeflow_point(  # noqa
            source_obj,
            self.timestamp_type,
            self.timestamp,
            engine_session_ref=dlpx_obj.server_session,
        )
        vdb_params.timeflow_point_parameters.container = source_obj.reference
        log.print_info(f"{engine_name} provisioning {self.name}")
        database.provision(dlpx_obj.server_session, vdb_params)
        # Add the job into the jobs dictionary so we can track its progress
        self._add_last_job_to_track(dlpx_obj)

    def _provision_vfiles_vdb(self, dlpx_obj):
        """
        Create a vfiles VDB
        :param dlpx_obj: DDP session object
        :type dlpx_obj: lib.GetSession.GetSession object
        """
        engine_name = list(dlpx_obj.dlpx_ddps)[0]
        group_ref, environment_obj, source_obj = self._find_group_source_environment_data(  # noqa
            dlpx_obj
        )
        timeflow_obj = dxtf.DxTimeflow(dlpx_obj.server_session)
        vfiles_params = vo.AppDataProvisionParameters()
        vfiles_params.source = vo.AppDataVirtualSource()
        vfiles_params.source_config = vo.AppDataDirectSourceConfig()
        vfiles_params.source.allow_auto_vdb_restart_on_host_reboot = True
        vfiles_params.container = vo.AppDataContainer()
        vfiles_params.container.group = group_ref
        vfiles_params.container.name = self.name
        vfiles_params.source_config.name = self.name
        vfiles_params.source_config.path = f"{self.mntpoint}/{self.name}"
        vfiles_params.source_config.repository = ref.find_db_repo(
            dlpx_obj.server_session,
            "AppDataRepository",
            environment_obj.reference,
            "Unstructured Files",
        )
        vfiles_params.source.name = self.name
        vfiles_params.source.parameters = {}
        vfiles_params.source.operations = vo.VirtualSourceOperations()

        vfiles_params = self._set_vdb_params(vfiles_params)

        if self.timestamp_type is None:
            vfiles_params.timeflow_point_parameters = (
                vo.TimeflowPointSemantic()
            )
            vfiles_params.timeflow_point_parameters.container = (
                source_obj.reference
            )
            vfiles_params.timeflow_point_parameters.location = "LATEST_POINT"
        elif self.timestamp_type.upper() == "SNAPSHOT":
            try:
                dx_snap_params = timeflow_obj.set_timeflow_point(
                    source_obj,
                    self.timestamp_type,
                    self.timestamp,
                    engine_session_ref=dlpx_obj.server_session,
                )
            except exceptions.RequestError as err:
                raise dxe.DlpxException(
                    f"Could not set the timeflow point:\n{err}"
                )
            if dx_snap_params.type == "TimeflowPointSemantic":
                vfiles_params.timeflow_point_parameters = (
                    vo.TimeflowPointSemantic()
                )
                vfiles_params.timeflow_point_parameters.container = (
                    dx_snap_params.container
                )
                vfiles_params.timeflow_point_parameters.location = (
                    dx_snap_params.location
                )
            elif dx_snap_params.type == "TimeflowPointTimestamp":
                vfiles_params.timeflow_point_parameters = (
                    vo.TimeflowPointTimestamp()
                )
                vfiles_params.timeflow_point_parameters.timeflow = (
                    dx_snap_params.timeflow
                )
                vfiles_params.timeflow_point_parameters.timestamp = (
                    dx_snap_params.timestamp
                )
        log.print_info(f"{engine_name}: Provisioning {self.name}\n")
        try:
            database.provision(dlpx_obj.server_session, vfiles_params)
        except (exceptions.RequestError, exceptions.HttpError) as err:
            raise dxe.DlpxException(
                f"ERROR: Could not create vdb  {self.name}\n{err}"
            )
        # Add the job into the jobs dictionary so we can track its progress
        self._add_last_job_to_track(dlpx_obj)

    def _provision_oracle_si_vdb(self, dlpx_obj):
        """
        Create an Oracle SI VDB
        :param dlpx_obj: DDP session object
        :type dlpx_obj: lib.GetSession.GetSession object
        """
        group_ref, environment_obj, source_obj = self._find_group_source_environment_data(  # noqa
            dlpx_obj
        )
        engine_name = list(dlpx_obj.dlpx_ddps)[0]
        vdb_params = vo.OracleProvisionParameters()
        vdb_params.open_resetlogs = True
        vdb_params.container = vo.OracleDatabaseContainer()
        vdb_params.container.group = group_ref
        vdb_params.container.name = self.name
        vdb_params.source = vo.OracleVirtualSource()
        vdb_params.source.allow_auto_vdb_restart_on_host_reboot = True
        vdb_params.source.mount_base = self.mntpoint
        vdb_params.source_config = vo.OracleSIConfig()
        vdb_params.source_config.environment_user = (
            environment_obj.primary_user
        )
        vdb_params.source.operations = vo.VirtualSourceOperations()

        vdb_params = self._set_vdb_params(vdb_params, dlpx_obj)

        vdb_params.source_config.database_name = self.name
        vdb_params.source_config.unique_name = self.name
        vdb_params.source_config.instance = vo.OracleInstance()
        vdb_params.source_config.instance.instance_name = self.name
        vdb_params.source_config.instance.instance_number = 1
        vdb_params.source_config.repository = ref.find_db_repo(
            dlpx_obj.server_session,
            "OracleInstall",
            environment_obj.reference,
            self.envinst,
        )
        timeflow_obj = dxtf.DxTimeflow(dlpx_obj.server_session)
        vdb_params.timeflow_point_parameters = timeflow_obj.set_timeflow_point(  # noqa
            source_obj,
            self.timestamp_type,
            self.timestamp,
            engine_session_ref=dlpx_obj.server_session,
        )
        log.print_info(f"{engine_name}: Provisioning {self.name}")
        try:
            database.provision(dlpx_obj.server_session, vdb_params)
        except (exceptions.RequestError, exceptions.HttpError) as err:
            raise dxe.DlpxException(
                f"ERROR: Could not create vdb  {self.name}\n{err}"
            )
        # Add the job into the jobs dictionary so we can track its progress
        self._add_last_job_to_track(dlpx_obj)

    def _provision_oracle_mt_vdb(self, dlpx_obj):
        """
        Create an Oracle Multi Tenant VDB
        :param dlpx_obj: DDP session object
        :type dlpx_obj: lib.GetSession.GetSession object
        """
        group_ref, environment_obj, source_obj = self._find_group_source_environment_data(  # noqa
            dlpx_obj
        )
        vdb_name = self.name
        engine_name = list(dlpx_obj.dlpx_ddps)[0]
        vdb_params = vo.OracleMultitenantProvisionParameters()
        vdb_params.open_resetlogs = True
        vdb_params.container = vo.OracleDatabaseContainer()
        vdb_params.container.group = group_ref
        vdb_params.container.name = vdb_name
        vdb_params.source = vo.OracleVirtualPdbSource()
        vdb_params.source.allow_auto_vdb_restart_on_host_reboot = True
        vdb_params.source.name = vdb_name
        vdb_params.source.mount_base = self.mntpoint
        vdb_params.source_config = vo.OraclePDBConfig()
        vdb_params.source_config.database_name = vdb_name
        if self.cdb_name:
            vdb_params.virtual_cdb = self._create_vcdb(
                dlpx_obj,
                self.cdb_name,
                group_ref,
                self.logsync,
                environment_obj,
                vo.OracleSIConfig,
            )
        else:
            cdb_obj = ref.find_obj_by_name(
                dlpx_obj.server_session, sourceconfig, self.source_db
            )
            vdb_params.source_config.cdb_config = cdb_obj.cdb_config
        vdb_params.source.operations = vo.VirtualSourceOperations()

        vdb_params = self._set_vdb_params(vdb_params, dlpx_obj)

        timeflow_obj = dxtf.DxTimeflow(dlpx_obj.server_session)
        vdb_params.timeflow_point_parameters = timeflow_obj.set_timeflow_point(  # noqa
            source_obj,
            self.timestamp_type,
            self.timestamp,
            engine_session_ref=dlpx_obj.server_session,
        )
        log.print_info(f"{engine_name}: Provisioning {vdb_name}")
        try:
            database.provision(dlpx_obj.server_session, vdb_params)
        except (exceptions.RequestError, exceptions.HttpError) as err:
            raise dxe.DlpxException(
                f"ERROR: Could not create vdb  {vdb_name}\n{err}"
            )
        # Add the job into the jobs dictionary so we can track its progress
        self._add_last_job_to_track(dlpx_obj)

    def _rac_nodes(self, dlpx_obj):
        """
        :return:
        """
        number = 0
        instances = []
        for ora_node in self.nodes.split(":"):
            number += 1
            instances.append(
                {
                    "type": "OracleRACInstance",
                    "instanceName": f"{self.name}_{number}",
                    "instanceNumber": number,
                    "node": ref.find_obj_by_name(
                        dlpx_obj.server_session, clusternode, ora_node
                    ).reference,
                }
            )
        return instances

    def _create_vcdb(
        self,
        dlpx_obj,
        cdb_name,
        group_ref,
        logsync,
        env_obj,
        source_config_type,
    ):
        """

        :param dlpx_obj:
        :return:
        """
        random_str = "".join(random.choices(string.ascii_lowercase, k=4))
        unique_name = f"{self.name}_{random_str}"
        virtual_cdb = vo.OracleVirtualCdbProvisionParameters()
        virtual_cdb.container = vo.OracleDatabaseContainer()
        virtual_cdb.container.name = cdb_name
        virtual_cdb.container.group = group_ref
        virtual_cdb.container.sourcing_policy = vo.OracleSourcingPolicy()
        virtual_cdb.container.sourcing_policy.logsync_enabled = logsync
        virtual_cdb.container.sourcing_policy.logsync_mode = "UNDEFINED"
        virtual_cdb.container.sourcing_policy.logsync_interval = 5
        virtual_cdb.source = vo.OracleVirtualCdbSource()
        virtual_cdb.source.mount_base = self.mntpoint
        virtual_cdb.source.allow_auto_vdb_restart_on_host_reboot = True
        virtual_cdb.source.name = unique_name
        virtual_cdb.source_config = source_config_type()
        virtual_cdb.source_config.database_name = cdb_name
        virtual_cdb.source_config.unique_name = unique_name
        virtual_cdb.source_config.repository = ref.find_db_repo(
            dlpx_obj.server_session,
            "OracleInstall",
            env_obj.reference,
            self.envinst,
        )
        virtual_cdb.source_config.environment_user = env_obj.primary_user
        if self.nodes:
            virtual_cdb.source_config.instances = self._rac_nodes(dlpx_obj)
            return virtual_cdb
        else:
            virtual_cdb.source_config.instance = vo.OracleInstance()
            virtual_cdb.source_config.instance.instance_number = 1
            virtual_cdb.source_config.instance.instance_name = f"{self.name}_1"
            virtual_cdb.source_config.unique_name = unique_name
            return virtual_cdb

    def _provision_oracle_mt_rac_vdb(self, dlpx_obj):
        """
        Create an Oracle Multi Tenant RAC VDB
        :param dlpx_obj: DDP session object
        :type dlpx_obj: lib.GetSession.GetSession object
        """
        group_ref, environment_obj, source_obj = self._find_group_source_environment_data(  # noqa
            dlpx_obj
        )
        vdb_name = self.name
        engine_name = list(dlpx_obj.dlpx_ddps)[0]
        vdb_params = vo.OracleMultitenantProvisionParameters()
        vdb_params.open_resetlogs = True
        vdb_params.container = vo.OracleDatabaseContainer()
        vdb_params.container.group = group_ref
        vdb_params.container.name = vdb_name
        vdb_params.source = vo.OracleVirtualPdbSource()
        vdb_params.source.allow_auto_vdb_restart_on_host_reboot = True
        vdb_params.source.mount_base = self.mntpoint
        vdb_params.source_config = vo.OraclePDBConfig()
        vdb_params.source_config.database_name = vdb_name
        if self.cdb_name:
            vdb_params.virtual_cdb = self._create_vcdb(
                dlpx_obj,
                self.cdb_name,
                group_ref,
                self.logsync,
                environment_obj,
                vo.OracleRACConfig,
            )
        else:
            cdb_obj = ref.find_obj_by_name(
                dlpx_obj.server_session, sourceconfig, self.source_db
            )
            vdb_params.source_config.cdb_config = cdb_obj.cdb_config
        vdb_params.source.operations = vo.VirtualSourceOperations()
        vdb_params = self._set_vdb_params(vdb_params, dlpx_obj)
        timeflow_obj = dxtf.DxTimeflow(dlpx_obj.server_session)
        vdb_params.timeflow_point_parameters = timeflow_obj.set_timeflow_point(
            source_obj,
            self.timestamp_type,
            self.timestamp,
            engine_session_ref=dlpx_obj.server_session,
        )
        log.print_info(f"{engine_name}: Provisioning {vdb_name}")
        try:
            database.provision(dlpx_obj.server_session, vdb_params)
        except (exceptions.RequestError, exceptions.HttpError) as err:
            raise dxe.DlpxException(
                f"ERROR: Could not create vdb  {vdb_name}\n{err}"
            )
        # Add the job into the jobs dictionary so we can track its progress
        self._add_last_job_to_track(dlpx_obj)

    def _provision_oracle_rac_vdb(self, dlpx_obj):
        """
        Create an Oracle rac VDB
        :param dlpx_obj: DDP session object
        :type dlpx_obj: lib.GetSession.GetSession object
        """
        group_ref, environment_obj, source_obj = self._find_group_source_environment_data(  # noqa
            dlpx_obj
        )
        engine_name = list(dlpx_obj.dlpx_ddps)[0]
        vdb_params = vo.OracleProvisionParameters()
        vdb_params.open_resetlogs = True
        vdb_params.container = vo.OracleDatabaseContainer()
        vdb_params.container.group = group_ref
        vdb_params.container.name = self.name
        vdb_params.source = vo.OracleVirtualSource()
        vdb_params.source.allow_auto_vdb_restart_on_host_reboot = False
        vdb_params.source.mount_base = self.mntpoint
        vdb_params.source_config = vo.OracleRACConfig()
        vdb_params.source_config.environment_user = (
            environment_obj.primary_user
        )
        vdb_params.source.operations = vo.VirtualSourceOperations()

        vdb_params = self._set_vdb_params(vdb_params, dlpx_obj.server_session)

        vdb_params.source_config.database_name = self.name
        vdb_params.source_config.unique_name = self.name
        vdb_params.source_config.instances = self._rac_nodes(dlpx_obj)
        vdb_params.source_config.repository = ref.find_db_repo(
            dlpx_obj.server_session,
            "OracleInstall",
            environment_obj.reference,
            self.envinst,
        )
        timeflow_obj = dxtf.DxTimeflow(dlpx_obj.server_session)
        vdb_params.timeflow_point_parameters = timeflow_obj.set_timeflow_point(
            source_obj, self.timestamp_type, self.timestamp
        )
        log.print_info(f"{engine_name}: Provisioning {self.name}")
        try:
            database.provision(dlpx_obj.server_session, vdb_params)
        except (exceptions.RequestError, exceptions.HttpError) as err:
            raise dxe.DlpxException(
                f"ERROR: Could not create vdb  {self.name}\n{err}"
            )
        # Add the job into the jobs dictionary so we can track its progress
        self._add_last_job_to_track(dlpx_obj)

    def _provision_postgres_vdb(self, dlpx_obj):
        """
        Create a Postgres VDB
        :param dlpx_obj: DDP session object
        :type dlpx_obj: lib.GetSession.GetSession object
        """
        engine_name = list(dlpx_obj.dlpx_ddps)[0]

        group_ref, environment_obj, source_obj = self._find_group_source_environment_data(  # noqa
            dlpx_obj
        )
        vdb_params = vo.AppDataProvisionParameters()
        vdb_params.container = vo.AppDataContainer()
        vdb_params.container.group = group_ref
        vdb_params.container.name = self.name
        vdb_params.source = vo.AppDataVirtualSource()
        vdb_params.source.allow_auto_vdb_restart_on_host_reboot = False
        vdb_params.source.mount_base = self.mntpoint
        vdb_params.source.parameters = {"postgresPort": int(self.port_num)}
        vdb_params.source_config = vo.AppDataDirectSourceConfig()
        vdb_params.source_config.environment_user = (
            environment_obj.primary_user
        )
        vdb_params.source_config.path = self.mntpoint
        vdb_params.source_config.name = self.name
        vdb_params.source_config.repository = ref.find_db_repo(
            dlpx_obj.server_session,
            "AppDataRepository",
            environment_obj.reference,
            self.envinst,
            install_path_lookup_key="postgresInstallPath",
        )
        # "Unstructured Files",
        vdb_params.source.operations = vo.VirtualSourceOperations()

        vdb_params = self._set_vdb_params(vdb_params, dlpx_obj)

        timeflow_obj = dxtf.DxTimeflow(dlpx_obj.server_session)
        vdb_params.timeflow_point_parameters = timeflow_obj.set_timeflow_point(  # noqa
            source_obj,
            self.timestamp_type,
            self.timestamp,
            engine_session_ref=dlpx_obj.server_session,
        )
        log.print_info(f"{engine_name}: Provisioning {self.name}")
        try:
            database.provision(dlpx_obj.server_session, vdb_params)
        except (exceptions.RequestError, exceptions.HttpError) as err:
            raise dxe.DlpxException(
                f"ERROR: Could not create vdb  {self.name}\n{err}"
            )
        # Add the job into the jobs dictionary so we can track its progress
        self._add_last_job_to_track(dlpx_obj)

    def _find_group_source_environment_data(self, dlpx_obj):
        """
        :param dlpx_obj:
        :return:  group_ref (Group name where the VDB will be created),
        environment_obj (environment object where the VDB will be created),
        source_obj (Database object of the source)
        :rtype: tuple
        """
        group_ref = None
        environment_obj = None
        source_obj = None
        if self.group:
            group_ref = ref.find_obj_by_name(
                dlpx_obj.server_session, group, self.group
            ).reference
        if self.env_name:
            environment_obj = ref.find_obj_by_name(
                dlpx_obj.server_session, environment, self.env_name
            )
        if self.source_db:
            source_obj = ref.find_obj_by_name(
                dlpx_obj.server_session, database, self.source_db
            )
        return group_ref, environment_obj, source_obj

    def _set_vdb_params(self, vdb_params, dlpx_obj):

        vdb_params.source.operations.pre_refresh = _add_hook(
            self.pre_refresh, dlpx_obj
        )
        vdb_params.source.operations.post_refresh = _add_hook(
            self.post_refresh, dlpx_obj
        )
        vdb_params.source.operations.pre_rollback = _add_hook(
            self.pre_rollback, dlpx_obj
        )
        vdb_params.source.operations.post_rollback = _add_hook(
            self.post_rollback, dlpx_obj
        )
        vdb_params.source.operations.configure_clone = _add_hook(
            self.configure_clone, dlpx_obj
        )

        return vdb_params
