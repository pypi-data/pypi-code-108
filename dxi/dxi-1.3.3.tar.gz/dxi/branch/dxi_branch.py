#
# Copyright (c) 2021 by Delphix. All rights reserved.
#

"""Creates, updates, deletes, activates and lists branches

Examples:
  dxi_branch.py --list
  dxi_branch.py --create_branch jsbranch1 --container_name jscontainer \
  --template_name jstemplate1
  dxi_branch.py --activate_branch jsbranch1
  dxi_branch.py --delete_branch jsbranch1
  dxi_branch.py --create_branch tb4 --container_name dc1 \
    --timestamp "2021-02-07T04:34:48.952Z"
"""
import re

from delphixpy.v1_10_2 import exceptions
from delphixpy.v1_10_2.web import selfservice
from delphixpy.v1_10_2.web import vo
from dxi._lib import dlpx_exceptions
from dxi._lib import dx_logging
from dxi._lib import get_references
from dxi._lib import run_job
from dxi._lib.dxi_constants import BranchOps
from dxi._lib.run_async import run_async
from dxi._lib.util import DXIConfigConstantsHelper
from dxi.dxi_tool_base import DXIBase
from tabulate import tabulate


class DXIBranchConstants(object):
    """
    Define constants for SelfService Branch operations
    """

    SINGLE_THREAD = False
    POLL = 20
    CONFIG = DXIConfigConstantsHelper().get_config()
    LOG_FILE_PATH = DXIConfigConstantsHelper().get_logdir()
    ENGINE_ID = "default"
    PARALLEL = 5
    TYPE = None
    ACTION = None
    HOSTIP = None
    MODULE_NAME = __name__
    LIST_HEADER = [
        "Branch Name",
        "Data Layout",
        "Layout Type",
        "Branch Reference",
        "End Time",
    ]


class DXIBranch(DXIBase):
    """
    All Self Service Branch Operations
    """

    def __init__(
        self,
        engine=DXIBranchConstants.ENGINE_ID,
        log_file_path=DXIBranchConstants.LOG_FILE_PATH,
        config_file=DXIBranchConstants.CONFIG,
        poll=DXIBranchConstants.POLL,
        single_thread=DXIBranchConstants.SINGLE_THREAD,
        parallel=DXIBranchConstants.PARALLEL,
        action=DXIBranchConstants.ACTION,
        module_name=DXIBranchConstants.MODULE_NAME,
    ):
        """
        :param engine: Alt Identifier of Delphix engine in dxtools.conf.
        :type engine: `str`
        :param config: The path to the dxtools.conf file
        :type config: `str`
        :param log_file_path: The path to the logfile you want to use.
        :type log_file_path: `str`
        :param poll: The number of seconds to wait between job polls
        :type poll: `int`
        :param single_thread: Run as a single thread.
                              False if running multiple threads.
        :type single_thread: `bool`
        :param module_name: Name of the current module
        :type poll: `str`
        """
        super().__init__(
            parallel=parallel,
            poll=poll,
            config=config_file,
            log_file_path=log_file_path,
            single_thread=single_thread,
            module_name=module_name,
            engine=engine,
        )
        self.action = action
        self.branch_name = ""
        self.container_name = ""
        self.bookmark_name = ""
        self.template_name = ""
        self.timestamp = ""

    def list(self):
        """
        List all existing branches
        """
        self.action = BranchOps.LIST
        self.branch_list = []
        try:
            dx_logging.print_debug("Listing Branches")
            self._execute_operation(self._list_branch_helper)
            return self.branch_list
        except Exception:
            return False

    def create(
        self,
        branch_name,
        container_name=None,
        template_name=None,
        bookmark_name=None,
        timestamp=None,
    ):
        """
        Creates a self service branch
        :param branch_name: Name of the branch to create
        :type password: `str`
        :param container_name: Name of the SS container
        :type password: `str`
        :param template_name: Name of the SS template
        :type password: `str`
        :param bookmark_name: Bookmark to create branch
        :type password: `str`
        :param timestamp: Timestamp to create branch
        :type password: `str`
        """
        self.action = BranchOps.CREATE
        self.branch_name = branch_name
        self.container_name = container_name
        self.bookmark_name = bookmark_name
        self.template_name = template_name
        self.timestamp = timestamp
        try:
            dx_logging.print_debug(f"Creating Branch {self.branch_name}")
            self._execute_operation(self._create_branch_helper)
            return True
        except Exception:
            return False

    def delete(self, branch_name):
        """
        Deletes a self service branch
        :param branch_name: Name of the branch to create
        :type password: `str`
        """
        self.action = BranchOps.DELETE
        self.branch_name = branch_name
        try:
            dx_logging.print_debug(f"Deleting Branch {self.branch_name}")
            self._execute_operation(self._delete_branch_helper)
            return True
        except Exception:
            return False

    def activate(self, branch_name, container_name=None):
        """
        Activates a self service branch
        :param branch_name: Name of the branch to create
        :type password: `str`
        """
        self.action = BranchOps.ACTIVATE
        self.branch_name = branch_name
        self.container_name = container_name
        try:
            dx_logging.print_debug(f"Activating Branch {self.branch_name}")
            self._execute_operation(self._activate_branch_helper)
            return True
        except Exception:
            return False

    @run_async
    def _create_branch_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        Create a Self-Service Branch

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
                if not self.container_name:
                    raise dlpx_exceptions.DlpxObjectNotFound(
                        "A containername is required to create branch"
                    )
                ss_branch = vo.JSBranchCreateParameters()
                ss_branch.name = self.branch_name
                data_container_obj = get_references.find_obj_by_name(
                    dlpx_obj.server_session,
                    selfservice.container,
                    self.container_name,
                )
                ss_branch.data_container = data_container_obj.reference
                if self.timestamp:
                    ss_branch.timeline_point_parameters = (
                        vo.JSTimelinePointTimeInput()
                    )
                    ss_branch.timeline_point_parameters.time = get_references.convert_timestamp_toiso(  # noqa
                        dlpx_obj.server_session, self.timestamp
                    )
                    ss_branch.timeline_point_parameters.branch = (
                        data_container_obj.active_branch
                    )
                elif self.bookmark_name:
                    ss_branch.timeline_point_parameters = (
                        vo.JSTimelinePointBookmarkInput()
                    )
                    ss_branch.timeline_point_parameters.bookmark = get_references.find_obj_by_name(  # noqa
                        dlpx_obj.server_session,
                        selfservice.bookmark,
                        self.bookmark_name,
                    ).reference
                elif self.template_name or self.container_name:
                    if self.template_name:
                        source_layout_ref = get_references.find_obj_by_name(
                            dlpx_obj.server_session,
                            selfservice.template,
                            self.template_name,
                        ).reference
                    else:
                        source_layout_ref = get_references.find_obj_by_name(
                            dlpx_obj.server_session,
                            selfservice.container,
                            self.container_name,
                        ).reference
                    ss_branch.timeline_point_parameters = (
                        vo.JSTimelinePointLatestTimeInput()
                    )
                    ss_branch.timeline_point_parameters.source_data_layout = (
                        source_layout_ref
                    )

                selfservice.branch.create(dlpx_obj.server_session, ss_branch)
                self._add_last_job_to_track(dlpx_obj)
                run_job.track_running_jobs(
                    engine_ref,
                    dlpx_obj,
                    poll=self.poll,
                    failures=self.failures,
                )
                dx_logging.print_debug(
                    f"Self Service Branch {self.branch_name} has been created"
                )
            except (exceptions.RequestError, exceptions.HttpError) as err:
                dx_logging.print_exception(
                    f"There was an error while creating the branch: {err}"
                )
                # raise dlpx_exceptions.DlpxException(
                #     f"There was an error while creating the branch: {err}"
                # )
                self.failures[0] = True
            except (dlpx_exceptions.DlpxObjectNotFound) as err:
                dx_logging.print_exception(
                    f"ERROR Could not find a required object reference"
                    f" to create the branch: \nRoot cause: {err}"
                    f"\nPlease verify if the provided containername "
                    f"/ bookmarkname / timestamp exist on the engine "
                )
                # raise dlpx_exceptions.DlpxException(
                #     f"ERROR Could not find a required object reference"
                #     f" to create the branch: {err}"
                # )
                self.failures[0] = True
            except (Exception) as err:
                dx_logging.print_exception(
                    f"ERROR: Unable to create branch: {err}"
                )
                # raise dlpx_exceptions.DlpxException(
                #     f"ERROR Could not find a required object reference"
                #     f" to create the branch: {err}"
                # )
                self.failures[0] = True

    @run_async
    def _list_branch_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        List all branches on a given engine

        :param engine_ref: Dictionary of engines
        :type engine_ref: `dict`

        :param dlpx_obj: DDP session object
        :type dlpx_obj: `lib.GetSession.GetSession`

        :return: created template reference
        :rtype: `str`
        """
        dlpx_obj = self._initialize_session()
        self._setup_dlpx_session(dlpx_obj, engine_ref)
        try:
            print_list = []
            js_data_layout = ""
            with dlpx_obj.job_mode(self.single_thread):
                branch_list = []
                ss_branches = selfservice.branch.get_all(
                    dlpx_obj.server_session
                )
                if ss_branches:
                    for ss_branch in ss_branches:
                        js_end_time = selfservice.operation.get(
                            dlpx_obj.server_session, ss_branch.first_operation
                        ).end_time
                        js_obj_type = "CONTAINER"
                        if re.search("TEMPLATE", ss_branch.data_layout):
                            js_data_layout = get_references.find_obj_name(
                                dlpx_obj.server_session,
                                selfservice.template,
                                ss_branch.data_layout,
                            )
                            js_obj_type = "TEMPLATE"
                        elif re.search("CONTAINER", ss_branch.data_layout):
                            js_data_layout = get_references.find_obj_name(
                                dlpx_obj.server_session,
                                selfservice.container,
                                ss_branch.data_layout,
                            )
                        print_list.append(
                            [
                                ss_branch._name[0],
                                js_data_layout,
                                js_obj_type,
                                ss_branch.reference,
                                js_end_time,
                            ]
                        )
                        branch_list.append(
                            dict(
                                zip(
                                    DXIBranchConstants.LIST_HEADER,
                                    [
                                        ss_branch._name[0],
                                        js_data_layout,
                                        js_obj_type,
                                        ss_branch.reference,
                                        js_end_time,
                                    ],
                                )
                            )
                        )
                else:
                    dx_logging.print_info(f"No branches found on engine.")
                self._add_last_job_to_track(dlpx_obj)
                run_job.track_running_jobs(
                    engine_ref,
                    dlpx_obj,
                    poll=self.poll,
                    failures=self.failures,
                )
                self.branch_list = print_list
                print("\n")
                print(
                    tabulate(
                        print_list,
                        headers=DXIBranchConstants.LIST_HEADER,
                        tablefmt="grid",
                    )
                )
                return branch_list
        except dlpx_exceptions.DlpxException as err:
            dx_logging.print_exception(
                f"ERROR: Could not list self service branches:{err} "
            )
            # raise (f"ERROR: Could not list self service branches:{err} ")
            self.failures[0] = True
        except Exception as err:
            dx_logging.print_exception(
                f"ERROR: Could not list self service branches:{err} "
            )
            # raise (f"ERROR: Could not list self service branches:{err} ")
            self.failures[0] = True

    @run_async
    def _activate_branch_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        Activates a branch

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
            with dlpx_obj.job_mode(self.single_thread):
                data_container_obj = get_references.find_obj_by_name(
                    dlpx_obj.server_session,
                    selfservice.container,
                    self.container_name,
                )
                branch_obj = get_references.find_branch_by_name_and_container_ref(  # noqa
                    dlpx_obj.server_session,
                    self.branch_name,
                    data_container_obj.reference,
                )
                # branch_obj = get_references.find_obj_by_name(
                #     dlpx_obj.server_session,
                #     selfservice.branch,
                #     self.branch_name,
                # )
                selfservice.branch.activate(
                    dlpx_obj.server_session, branch_obj.reference
                )
                self._add_last_job_to_track(dlpx_obj)
                run_job.track_running_jobs(
                    engine_ref,
                    dlpx_obj,
                    poll=self.poll,
                    failures=self.failures,
                )
                dx_logging.print_info(
                    f"The branch {self.branch_name} activated"
                )
        except (
            exceptions.RequestError,
            dlpx_exceptions.DlpxObjectNotFound,
            Exception,
        ) as err:
            dx_logging.print_exception(
                f"ERROR: An error occurred activating "
                f"the {self.branch_name}:{err}"
            )
            # raise dlpx_exceptions.DlpxException(
            #     f"ERROR: An error occurred activating "
            #     f"the {self.branch_name}:{err}"
            # )
            self.failures[0] = True

    @run_async
    def _delete_branch_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        Deletes a branch

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
            with dlpx_obj.job_mode(self.single_thread):
                branch_obj = get_references.find_obj_by_name(
                    dlpx_obj.server_session,
                    selfservice.branch,
                    self.branch_name,
                )
                selfservice.branch.delete(
                    dlpx_obj.server_session, branch_obj.reference
                )
                self._add_last_job_to_track(dlpx_obj)
                run_job.track_running_jobs(
                    engine_ref,
                    dlpx_obj,
                    poll=self.poll,
                    failures=self.failures,
                )
        except (
            dlpx_exceptions.DlpxException,
            exceptions.HttpError,
            exceptions.RequestError,
        ) as err:
            dx_logging.print_exception(
                f"The branch could not be deleted: {err}"
            )
            # raise dlpx_exceptions.DlpxException(
            #     f"ERROR: The branch was not deleted : {err}"
            # )
            self.failures[0] = True
        except Exception as err:
            dx_logging.print_exception(
                f"The branch could not be deleted: {err}"
            )
            # raise dlpx_exceptions.DlpxException(
            #     f"ERROR: The branch was not deleted : {err}"
            # )
            self.failures[0] = True
