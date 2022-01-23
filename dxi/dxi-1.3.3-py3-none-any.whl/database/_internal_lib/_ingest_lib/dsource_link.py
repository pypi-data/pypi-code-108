#
# Copyright (c) 2021 by Delphix. All rights reserved.
#
"""
Create an object to link MS SQL or ASE dSources
"""
from delphixpy.v1_10_2.web import group
from delphixpy.v1_10_2.web import sourceconfig
from delphixpy.v1_10_2.web import vo
from delphixpy.v1_10_2.web.environment import environment

from dxi._lib import dlpx_exceptions as dxe, get_references
from dxi._lib import get_references as ref
from dxi._lib.util import DXIConfigConstantsHelper
from dxi.dxi_tool_base import DXIBase


class ProvisionDsourceConstants(object):
    """
    Class of common constants used by Provision VDB
    """

    SINGLE_THREAD = False
    POLL = 10
    CONFIG = DXIConfigConstantsHelper().get_config()
    LOG_FILE_PATH = DXIConfigConstantsHelper().get_logdir()+ "/dxi_provisiondsource.log"
    ENGINE_ID = "default"
    PARALLEL = 5
    ACTION = None
    MODULE_NAME = __name__
    VDB_LIST_HEADER = []
    FORCE = False


class DsourceLink:
    """
    Base class for linking dSources
    """

    def __init__(
        self,
        dsource_name,
        db_passwd,
        db_user,
        dx_group,
        logsync,
        dlpx_obj,
        db_type,
    ):
        """
        Attributes required for linking dSources
        :param engine: A Delphix DDP session object
        :type engine: lib.get_session.GetSession
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
        self.dx_group = dx_group
        self.db_passwd = db_passwd
        self.db_user = db_user
        self.dsource_name = dsource_name
        self.db_type = db_type
        self.dlpx_obj = dlpx_obj
        self.logsync = logsync
        self.link_params = vo.LinkParameters()
        self.srccfg_obj = self._get_source_config_type(self.db_type)

    def _get_source_config_type(self, db_type):
        return ""

    def dsource_prepare_link(self, source_env_name=None):
        """
        Prepare the dsource object for linking
        """
        self.link_params.name = self.dsource_name
        if self.db_type.lower() == "oracle":
            self.link_params.link_data = vo.OracleLinkData()
        elif self.db_type.lower() == "oraclemt":
            self.link_params.link_data = vo.OraclePDBLinkData()
        elif self.db_type.lower() == "sybase":
            self.link_params.link_data = vo.ASELinkData()
        elif self.db_type.lower() == "mssql":
            self.link_params.link_data = vo.MSSqlLinkData()
        self.link_params.group = ref.find_obj_by_name(
            self.dlpx_obj.server_session, group, self.dx_group
        ).reference
        self.link_params.link_data.db_credentials = vo.PasswordCredential()
        self.link_params.link_data.db_credentials.password = self.db_passwd
        self.link_params.link_data.db_user = self.db_user
        # Create blank sourcing policy
        self.link_params.link_data.sourcing_policy = vo.SourcingPolicy()
        self.link_params.link_data.sourcing_policy.logsync_enabled = self.logsync
        self.link_params.link_data.config = self.get_or_create_sourceconfig(
            self.srccfg_obj, source_env_name
        )
        return self.link_params

    def get_or_create_sourceconfig(self, sourceconfig_obj=None, source_env_name=None):
        """
        Get current sourceconfig or create it
        :param sourceconfig_obj:
        :return: link_params
        """
        try:
            if self.db_type.lower() == "mssql":
                env_ref = get_references.find_obj_by_name(
                    self.dlpx_obj.server_session, environment, source_env_name)
                return ref.find_obj_by_name_v2(
                    self.dlpx_obj.server_session, sourceconfig, self.dsource_name, environment=env_ref.reference
                ).reference
            else:
                return ref.find_obj_by_name(
                    self.dlpx_obj.server_session, sourceconfig, self.dsource_name
                ).reference
        except dxe.DlpxObjectNotFound:
            self.link_params.link_data.config = sourceconfig.create(
                self.dlpx_obj.server_session, sourceconfig_obj
            ).reference
