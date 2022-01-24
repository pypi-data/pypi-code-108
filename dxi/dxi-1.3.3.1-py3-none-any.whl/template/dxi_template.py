#
# Copyright (c) 2021 by Delphix. All rights reserved.
#
"""
This module includes classes for
Delphix Self Service Template Operations

Examples:
  dxi_template.py --list_templates
  dxi_template.py --create_template jstemplate1 --database <name>
  dxi_template.py --create_template jstemplate2 --database <name:name:name>
  dxi_template.py --delete_template jstemplate1

"""

from delphixpy.v1_10_2 import exceptions
from delphixpy.v1_10_2.web import database
from delphixpy.v1_10_2.web import selfservice
from delphixpy.v1_10_2.web import vo
from dxi._lib import dlpx_exceptions as dxe
from dxi._lib import dx_logging as log
from dxi._lib import get_references as ref
from dxi._lib import run_job
from dxi._lib.dxi_constants import TemplateOps
from dxi._lib.run_async import run_async
from dxi._lib.util import DXIConfigConstantsHelper
from dxi.dxi_tool_base import DXIBase
from tabulate import tabulate


class DXITemplateConstants(object):
    """
    Define constants for Self Service Template Class & CLI
    """

    SINGLE_THREAD = False
    POLL = 20
    CONFIG = DXIConfigConstantsHelper().get_config()
    LOG_FILE_PATH = DXIConfigConstantsHelper().get_logdir()
    ENGINE_ID = "default"
    PARALLEL = 5
    ACTION = None
    MODULE_NAME = __name__
    LIST_HEADER = ["Name", "Reference", "Active Branch", "Last Updated"]


class DXITemplate(DXIBase):
    """
    Class for Self Service Template Operations
    """

    def __init__(
        self,
        engine=DXITemplateConstants.ENGINE_ID,
        single_thread=DXITemplateConstants.SINGLE_THREAD,
        config=DXITemplateConstants.CONFIG,
        log_file_path=DXITemplateConstants.LOG_FILE_PATH,
        poll=DXITemplateConstants.POLL,
        action=DXITemplateConstants.ACTION,
    ):
        """
        :param engine: Identifier for the engine in dxtools.conf
        :type engine: `str`

        :param single_thread: Run jobs synchronously on an engine
                              True forSync Mode| False for Async Mode
        :type single_thread: `bool`

        :param config: The path to the dxtools.conf file
        :type config: `str`

        :param log_file_path: The path to the logfile for this module
        :type log_file_path: `str`

        :param poll: Time in seconds to poll status of a job.
        :type log_file_path: `int
        """
        super().__init__(
            config=config,
            log_file_path=log_file_path,
            single_thread=single_thread,
            engine=engine,
            poll=poll,
            module_name=__name__,
        )
        self.action = action

    def __validate_input(self):
        pass

    def list(self):
        """
        List all templates on an engine
        """
        self.action = TemplateOps.LIST
        try:
            self._execute_operation(self._list_template_helper)
            return True
        except Exception:
            return False

    def create(self, template_name=None, dbnames=None):
        """
        Create a template on an engine

        :param template_name: Name of the template to create
        :type template_name: str

        :param dbnames: List of datasource names, separated by ":'
                        Sample oraclesrc1:sqlsrc1
        :type dbnames: str

        """
        self.action = TemplateOps.CREATE
        self.template_name = template_name
        self.dbnames = dbnames
        try:
            self._execute_operation(self._create_template_helper)
            return True
        except Exception:
            return False

    def delete(self, template_name=None):
        """
        Delete a template from an engine

        :param template_name: Name of the template to delete
        :type template_name: str
        """
        self.action = TemplateOps.DELETE
        self.template_name = template_name
        try:
            self._execute_operation(self._delete_template_helper)
            return True
        except Exception:
            return False

    @run_async
    def _list_template_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        Execution helper for template list operation

        :param engine_ref: Dictionary of engines
        :type engine_ref: `dict`

        :param dlpx_obj: DDP session object
        :type dlpx_obj: `lib.GetSession.GetSession`

        :return: List of all templtes on a given engine
        :rtype: `list`
        """
        dlpx_obj = self._initialize_session()
        self._setup_dlpx_session(dlpx_obj, engine_ref)
        try:
            print_list = []
            with dlpx_obj.job_mode(self.single_thread):
                container_list = []
                ss_templates = selfservice.template.get_all(
                    dlpx_obj.server_session
                )
                if not ss_templates:
                    log.print_info(f"No Self Service Template on engine")
                else:
                    for ss_template in ss_templates:
                        last_updated = ref.convert_timestamp(
                            dlpx_obj.server_session,
                            ss_template.last_updated[:-5],
                        )
                        print_list.append(
                            [
                                ss_template.name,
                                ss_template.reference,
                                ss_template.active_branch,
                                last_updated,
                            ]
                        )
                        container_list.append(
                            dict(
                                zip(
                                    DXITemplateConstants.LIST_HEADER,
                                    [
                                        ss_template.name,
                                        ss_template.reference,
                                        ss_template.active_branch,
                                        last_updated,
                                    ],
                                )
                            )
                        )
                    self._add_last_job_to_track(dlpx_obj)
                    run_job.track_running_jobs(
                        engine_ref,
                        dlpx_obj,
                        poll=self.poll,
                        failures=self.failures,
                    )
                    print(
                        tabulate(
                            print_list,
                            headers=DXITemplateConstants.LIST_HEADER,
                            tablefmt="grid",
                        )
                    )
            return container_list
        except (
            dxe.DlpxException,
            exceptions.HttpError,
            exceptions.RequestError,
        ) as err:
            log.print_exception(
                f"ERROR: The templates could not be listed: {err}"
            )
            # raise dxe.DlpxException(
            #     f"ERROR: The templates could not be listed: {err}"
            # )
            self.failures[0] = True

    @run_async
    def _create_template_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        Execution helper for template create operation

        :param engine_ref: Dictionary of engines
        :type engine_ref: `dict`

        :param dlpx_obj: DDP session object
        :type dlpx_obj: `lib.GetSession.GetSession`

        :return: created template reference
        :rtype: `str`
        """
        dlpx_obj = self._initialize_session()
        self._setup_dlpx_session(dlpx_obj, engine_ref)
        with dlpx_obj.job_mode(self.single_thread):
            try:
                ss_template_params = vo.JSDataTemplateCreateParameters()
                ss_template_params.name = self.template_name
                template_ds_lst = []
                template_ref = ""
                for dbname in self.dbnames.split(":"):
                    template_ds_lst.append(
                        ref.build_data_source_params(
                            dlpx_obj, database, dbname
                        )
                    )
                ss_template_params.data_sources = template_ds_lst
                template_ref = selfservice.template.create(
                    dlpx_obj.server_session, ss_template_params
                )
                self._add_last_job_to_track(dlpx_obj)
                run_job.track_running_jobs(
                    engine_ref,
                    dlpx_obj,
                    poll=self.poll,
                    failures=self.failures,
                )
                return template_ref
            except (
                dxe.DlpxException,
                exceptions.RequestError,
                exceptions.HttpError,
            ) as err:
                log.print_exception(
                    f"ERROR: The template "
                    f"{self.template_name} was not created: {err}"
                )
                # raise dxe.DlpxException(
                #     f"ERROR: The template "
                #     f"{self.template_name} was not created: {err}"
                # )
                self.failures[0] = True

    @run_async
    def _delete_template_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        Execution helper for template delete operation

        :param engine_ref: Dictionary of engines
        :type engine_ref: `dict`

        :param dlpx_obj: DDP session object
        :type dlpx_obj: `lib.GetSession.GetSession`
        """
        dlpx_obj = self._initialize_session()
        self._setup_dlpx_session(dlpx_obj, engine_ref)
        with dlpx_obj.job_mode(self.single_thread):
            try:
                template_ref = ref.find_obj_by_name(
                    dlpx_obj.server_session,
                    selfservice.template,
                    self.template_name,
                ).reference
                selfservice.template.delete(
                    dlpx_obj.server_session, template_ref
                )
                self._add_last_job_to_track(dlpx_obj)
                run_job.track_running_jobs(
                    engine_ref,
                    dlpx_obj,
                    poll=self.poll,
                    failures=self.failures,
                )
            except (Exception, BaseException) as err:
                log.print_exception(
                    f"Template {self.template_name} was not deleted. "
                    f"ERROR:{str(err)}"
                )
                # raise dxe.DlpxException(
                #     f"ERROR: The template "
                #     f"{self.template_name} was not deleted: {err}"
                # )
                self.failures[0] = True
