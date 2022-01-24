#
# Copyright (c) 2021 by Delphix. All rights reserved.
#
"""
This module includes classes to work on Delphix Groups.
"""
from delphixpy.v1_10_2.web.vo import Group
from delphixpy.v1_10_2.web import group
from dxi._lib import dx_logging as log
from dxi._lib import dxi_constants as const
from dxi._lib import get_references
from dxi._lib import run_job
from dxi._lib.dlpx_exceptions import DXIException
from dxi._lib.dlpx_exceptions import DlpxObjectNotFound
from dxi._lib.run_async import run_async
from dxi._lib.util import DXIConfigConstantsHelper
from dxi.dxi_tool_base import DXIBase
from tabulate import tabulate
from os.path import basename
from dxi._lib.util import format_err_msg



class DXIGroupConstants(object):
    """
    Define constants for Delphix Group Opertions.
    """
    SINGLE_THREAD = False
    POLL = 20
    CONFIG = DXIConfigConstantsHelper().get_config()
    LOG_FILE_PATH = DXIConfigConstantsHelper().get_logdir()
    ENGINE_ID = "default"
    GROUP = None

class DXIGroup(DXIBase):
    """
    Class to operate on Delphix Group objects.
    """
    header = [
        "Engine",
        "Group Name",
        "Group Description",
        "Group Reference"
    ]

    def __init__(
        self,
        engine=DXIGroupConstants.ENGINE_ID,
        single_thread=DXIGroupConstants.SINGLE_THREAD,
        config=DXIGroupConstants.CONFIG,
        log_file_path=DXIGroupConstants.LOG_FILE_PATH,
        poll=DXIGroupConstants.POLL,
        debug=False,
    ):
        """
        Constructor for DXIGroups
        Args:
            engine: Name of the engine in dxtools.conf
            single_thread: Sync/Async mode of operation
            config: Config file full path inclufing filename
            log_file_path: log file path using filename
            poll(int): Polling frequency for jobs in seconds
            debug (bool): Enable debug logging.
        """
        super().__init__(
            config=config,
            log_file_path=log_file_path,
            single_thread=single_thread,
            engine=engine,
            poll=poll,
            module_name=basename(__file__).split(".")[0],
            debug=debug,
        )
        self.group_name = ""

    def list(self):
        """
        Lists all groups on an engine.
        Returns:
            groups_list: A list of group objects
        """
        self.groups_list = []
        try:
            log.print_info(f"Running dxi group list.")
            self._execute_operation(self.__list_group_helper)
            return self.groups_list
        except Exception as err:
            print(err)
            return False

    @run_async
    def __list_group_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        Helper method for groups list
        engine_ref (DelphixEngine): The DelphixEngine object
        dlpx_obj: Dictionary of Delphix Engines.
        single_thread: Run as synchronous/asynchronous operations.
        """
        try:
            dlpx_obj = self._initialize_session()
            self._setup_dlpx_session(dlpx_obj, engine_ref)
            engine_session = dlpx_obj.server_session
            print_list = []
            log.print_debug(self.header)
            dxgroups = group.get_all(engine_session)
            for dxgroup in dxgroups:
                print_list.append(
                    [
                        engine_ref["hostname"],
                        dxgroup.name,
                        dxgroup.description,
                        dxgroup.reference
                    ]
                )
                self.groups_list.append(
                    dict(
                        zip(
                            self.header,
                            [
                                engine_ref["hostname"],
                                dxgroup.name,
                                dxgroup.description,
                                dxgroup.reference
                            ],
                        )
                    )
                )
            print(tabulate(print_list, headers=self.header, tablefmt="github"))
        except Exception as err:
            log.print_exception(
                f"ERROR: An error occurred while listing "
                f"Groups.\n {err}"
            )
            self.failures[0] = True

    def create(self, group_name, description):
        """
        Create a group in an Engine.
        Args:
            group_name: Current group name
            description: Description for the group
        Returns:
            boolean value to indicate success/failure.
        """
        self.group_name = group_name
        self.group_desc = description
        try:
            log.print_info(f"Running dxi group create.")
            self._execute_operation(self.__create_group_helper)
            return True
        except Exception as err:
            print(err)
            return False

    @run_async
    def __create_group_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        Helper method for groups create
        engine_ref (DelphixEngine): The DelphixEngine object
        dlpx_obj: Dictionary of Delphix Engines.
        single_thread: Run as synchronous/asynchronous operations.
        """
        try:
            dlpx_obj = self._initialize_session()
            self._setup_dlpx_session(dlpx_obj, engine_ref)
            engine_session = dlpx_obj.server_session
            with dlpx_obj.job_mode(single_thread):
                grp_object = Group()
                grp_object.name = self.group_name
                if self.group_desc:
                    grp_object.description = self.group_desc
                else:
                    grp_object.description = ""
                group.create(engine_session, grp_object)
            log.print_info(f"group creted.")
        except DXIException as err:
            log.print_exception(err)
            self.failures[0] = True
        except (Exception, BaseException) as err:
            err_msg = format_err_msg(
                err,
                engine_name=engine_ref["hostname"],
                object_name=self.group_name,
                operation="GROUP_CREATE"
            )
            log.print_exception(err)
            self.failures[0] = True

    def delete(self, group_name):
        """
        Delete a group in an Engine.
        Args:
            group_name: Current group name
        Returns:
            boolean value to indicate success/failure.
        """
        self.group_name = group_name
        try:
            log.print_info(f"Running dxi group delete.")
            self._execute_operation(self.__delete_group_helper)
            return True
        except Exception as err:
            print(err)
            return False

    @run_async
    def __delete_group_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        Helper method for groups delete
        engine_ref (DelphixEngine): The DelphixEngine object
        dlpx_obj: Dictionary of Delphix Engines.
        single_thread: Run as synchronous/asynchronous operations.
        """
        try:
            dlpx_obj = self._initialize_session()
            self._setup_dlpx_session(dlpx_obj, engine_ref)
            engine_session = dlpx_obj.server_session
            with dlpx_obj.job_mode(single_thread):
                grp_ref = get_references.find_obj_by_name_v2(
                    engine_session,
                    group,
                    obj_name=self.group_name
                )
                group.delete(engine_session, grp_ref.reference)
            log.print_info(f"group deleted.")
        except DlpxObjectNotFound as err:
            err_msg = format_err_msg(
                f"Unable to find group {self.group_name}.",
                engine_name=engine_ref["hostname"],
                operation="GROUP_DELETE",
                err_code=const.ERR_OBJ_NOTFOUND,
                object_name=self.group_name
            )
            log.print_exception(err_msg)
            #raise DXIException(err_msg, const.ERR_OBJ_NOTFOUND)
            self.failures[0] = True
        except (Exception, BaseException) as err:
            err_msg = format_err_msg(
                err,
                engine_name=engine_ref["hostname"],
                object_name=self.group_name,
                operation="GROUP_DELETE"
            )
            log.print_exception(err)
            self.failures[0] = True

    def update(self, group_name, new_name, new_description):
        """
        Update a group's name
        Args:
            group_name: Current group name
            new_name: New name for the group
        Returns:
            boolean value to indicate success/failure.
        """
        self.group_name = group_name
        self.new_name = new_name
        self.new_description = new_description
        try:
            log.print_info(f"Running dxi group update.")
            self._execute_operation(self.__update_group_helper)
            return True
        except Exception as err:
            print(err)
            return False

    @run_async
    def __update_group_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        Helper method for groups update
        engine_ref (DelphixEngine): The DelphixEngine object
        dlpx_obj: Dictionary of Delphix Engines.
        single_thread: Run as synchronous/asynchronous operations.
        """
        try:
            dlpx_obj = self._initialize_session()
            self._setup_dlpx_session(dlpx_obj, engine_ref)
            engine_session = dlpx_obj.server_session
            with dlpx_obj.job_mode(single_thread):
                grp_ref = get_references.find_obj_by_name_v2(
                    engine_session,
                    group,
                    obj_name=self.group_name
                )
                # Creating new group object
                grp_object = Group()
                grp_object.name = self.new_name
                if self.new_description:
                    grp_object.description = self.new_description
                group.update(engine_session, grp_ref.reference, grp_object)
            log.print_info(f"group updated.")
        except DlpxObjectNotFound as err:
            err_msg = format_err_msg(
                f"Unable to find group {self.group_name}.",
                engine_name=engine_ref["hostname"],
                operation="GROUP_DELETE",
                err_code=const.ERR_OBJ_NOTFOUND,
                object_name=self.group_name
            )
            log.print_exception(err_msg)
            #raise DXIException(err_msg, const.ERR_OBJ_NOTFOUND)
            self.failures[0] = True
        except (Exception, BaseException) as err:
            err_msg = format_err_msg(
                err,
                engine_name=engine_ref["hostname"],
                object_name=self.group_name,
                operation="GROUP_DELETE"
            )
            log.print_exception(err)
            self.failures[0] = True