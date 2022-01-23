#
# Copyright (c) 2021 by Delphix. All rights reserved.
#
"""
This module includes classes to work on Delphix Virtualization Users.
"""
from operator import xor
from os.path import basename

from delphixpy.v1_10_2.web import user
from delphixpy.v1_10_2.web.vo import CredentialUpdateParameters
from delphixpy.v1_10_2.web.vo import PasswordCredential
from delphixpy.v1_10_2.web.vo import User
from dxi._lib import dx_logging as log
from dxi._lib import dxi_constants as const
from dxi._lib import get_references as ref
from dxi._lib.dlpx_exceptions import DlpxObjectNotFound
from dxi._lib.dlpx_exceptions import DXIException
from dxi._lib.run_async import run_async
from dxi._lib.util import DXIConfigConstantsHelper
from dxi._lib.util import format_err_msg
from dxi.dxi_tool_base import DXIBase
from tabulate import tabulate


class DXIUserConstants(object):
    """
    Define constants for Delphix User Opertions.
    """

    SINGLE_THREAD = False
    POLL = 20
    CONFIG = DXIConfigConstantsHelper().get_config()
    LOG_FILE_PATH = DXIConfigConstantsHelper().get_logdir()
    ENGINE_ID = "default"
    REVOKE = "revoke"
    MODULE = "DXIUser"
    LIST_HEADER = [
        "Engine",
        "Username",
        "First Name",
        "Last Name",
        "Email",
        "Reference",
        "Type",
        "Active",
    ]

class DXIUser(DXIBase):
    """
    Class to operate on Delphix User objects.
    """

    def __init__(
        self,
        engine=DXIUserConstants.ENGINE_ID,
        single_thread=DXIUserConstants.SINGLE_THREAD,
        config=DXIUserConstants.CONFIG,
        log_file_path=DXIUserConstants.LOG_FILE_PATH,
        poll=DXIUserConstants.POLL,
        debug=False,
    ):
        """
        Constructor for DXIUser
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

    def list(self):
        """
        Lists all users on a Delphix Engine.
        Returns:
            users_list: A list of user objects
        Raises:
            Does not raise an exception. If an exception is encountered,
            returns a boolean False.
        """
        self.users_list = []
        self.print_list = []
        try:
            log.print_info(f"Running dxi user list.")
            self._execute_operation(self.__list_user_helper)
            self._display_list(self.print_list,DXIUserConstants.LIST_HEADER)
            return self.users_list
        except Exception as err:
            print(err)
            return False

    @run_async
    def __list_user_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        Helper method for users list
        engine_ref (DelphixEngine): The DelphixEngine object
        dlpx_obj: Dictionary of Delphix Engines.
        single_thread: Run as synchronous/asynchronous operations.
        """
        engine_session = None
        try:
            dlpx_obj = self._initialize_session()
            self._setup_dlpx_session(dlpx_obj, engine_ref)
            engine_session = dlpx_obj.server_session
            dxusers = user.get_all(engine_session)
            for dxuser in dxusers:
                self.print_list.append(
                    [
                        engine_ref["hostname"],
                        dxuser.name,
                        dxuser.first_name,
                        dxuser.last_name,
                        dxuser.email_address,
                        dxuser.reference,
                        dxuser.user_type,
                        dxuser.enabled,
                    ]
                )
                self.users_list.append(
                    dict(
                        zip(
                            DXIUserConstants.LIST_HEADER,
                            [
                                engine_ref["hostname"],
                                dxuser.name,
                                dxuser.first_name,
                                dxuser.last_name,
                                dxuser.email_address,
                                dxuser.reference,
                                dxuser.user_type,
                                dxuser.enabled,
                            ],
                        )
                    )
                )
        except Exception as err:
            log.print_exception(
                f"ERROR: An error occurred while listing " f"users.\n {err}"
            )
            self.failures[0] = True
        finally:
            self._remove_session(engine_session)

    def create(
        self, user_name, user_password, first_name, last_name, email_address
    ):
        """
        Create a user in a Delphix Engine..
        Args:
            user_name:  New user name to create
            user_password: Password for new user.
            first_name: First name of user
            last_name: Last name of user
            email: Email address for user

        Returns:
            boolean value to indicate success/failure.
        """
        self.user_name = user_name
        self.user_password = user_password
        self.first_name = first_name
        self.last_name = last_name
        self.email_address = email_address
        try:
            log.print_info(f"Running dxi user create.")
            self._execute_operation(self.__create_user_helper)
            return True
        except Exception as err:
            print(err)
            return False

    @run_async
    def __create_user_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        Helper method for delphix user create.
        engine_ref (DelphixEngine): The DelphixEngine object
        dlpx_obj: Dictionary of Delphix Engines.
        single_thread: Run as synchronous/asynchronous operations.
        """
        engine_session = None
        try:
            dlpx_obj = self._initialize_session()
            self._setup_dlpx_session(dlpx_obj, engine_ref)
            engine_session = dlpx_obj.server_session
            with dlpx_obj.job_mode(single_thread):
                user_object = User()
                user_object.name = self.user_name
                user_object.first_name = self.first_name
                user_object.last_name = self.last_name
                user_object.email_address = self.email_address
                user_object.user_type = "DOMAIN"
                user_object.credential = PasswordCredential()
                user_object.credential.password = self.user_password
                dx_user_ref = user.create(engine_session, user_object)
            log.print_info(
                f"Delphix user created with reference: {dx_user_ref}"
            )
        except DXIException as err:
            log.print_exception(err)
            self.failures[0] = True
        except (Exception, BaseException) as err:
            err_msg = format_err_msg(
                "Error while creating user.",
                msg2=err,
                engine_name=engine_ref["hostname"],
                object_name=self.user_name,
                operation="USER_CREATE",
            )
            log.print_exception(err_msg, DXIUserConstants.MODULE)
            self.failures[0] = True
        finally:
            self._remove_session(engine_session)

    def delete(self, user_name):
        """
        Delete a user from an Engine.
        Args:
            user_name: Current user name
        Returns:
            boolean value to indicate success/failure.
        """
        self.user_name = user_name
        try:
            log.print_info(f"Running dxi user delete.")
            self._execute_operation(self.__delete_user_helper)
            return True
        except Exception as err:
            print(err)
            return False

    @run_async
    def __delete_user_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        Helper method for user delete
        engine_ref (DelphixEngine): The DelphixEngine object
        dlpx_obj: Dictionary of Delphix Engines.
        single_thread: Run as synchronous/asynchronous operations.
        """
        engine_session = None
        try:
            dlpx_obj = self._initialize_session()
            self._setup_dlpx_session(dlpx_obj, engine_ref)
            engine_session = dlpx_obj.server_session
            with dlpx_obj.job_mode(single_thread):
                user_obj = ref.find_obj_by_name_v2(
                    engine_session, user, obj_name=self.user_name
                )
                user.delete(engine_session, user_obj.reference)
            log.print_info(f"User deleted.")
        except DlpxObjectNotFound as err:
            err_msg = format_err_msg(
                f"Unable to find user {self.user_name}.",
                msg2=err,
                engine_name=engine_ref["hostname"],
                operation="USER_DELETE",
                err_code=const.ERR_OBJ_NOTFOUND,
                object_name=self.user_name,
            )
            log.print_exception(err_msg, DXIUserConstants.MODULE)
            self.failures[0] = True
        except (Exception, BaseException) as err:
            err_msg = format_err_msg(
                f"Unable to find user {self.user_name}.",
                msg2=err,
                engine_name=engine_ref["hostname"],
                object_name=self.user_name,
                operation="USER_DELETE",
            )
            log.print_exception(err_msg, DXIUserConstants.MODULE)
            self.failures[0] = True
        finally:
            self._remove_session(engine_session)

    def update(
        self,
        user_name,
        first_name=None,
        last_name=None,
        email_address=None,
        current_password=None,
        new_password=None,
    ):
        """
        Update a user in Delphix Engine
        Args:
            user_name : Name of the user to update
            first_name: User's first name
            last_name: Users last name
            email_address: User's email address,
            current_password= User's current password if changing password.
            new_password=User's new password if changing password.
        Returns:
            boolean value to indicate success/failure.
        """
        self.user_name = user_name
        self.first_name = first_name
        self.last_name = last_name
        self.email_address = email_address
        self.current_password = current_password
        self.new_password = new_password
        try:
            log.print_info(f"Running dxi user update.")
            self.validate_inputs(const.UserOps.UPDATE)
            self._execute_operation(self.__update_user_helper)
            return True
        except DXIException as err:
            log.print_exception(err.message)
            return False
        except Exception as err:
            log.print_exception(err)
            return False

    @run_async
    def __update_user_helper(self, engine_ref, dlpx_obj, single_thread):
        """
        Helper method for user update
        engine_ref (DelphixEngine): The DelphixEngine object
        dlpx_obj: Dictionary of Delphix Engines.
        single_thread: Run as synchronous/asynchronous operations.
        """
        engine_session = None
        try:
            dlpx_obj = self._initialize_session()
            self._setup_dlpx_session(dlpx_obj, engine_ref)
            engine_session = dlpx_obj.server_session
            with dlpx_obj.job_mode(single_thread):
                dxuser_obj = ref.find_obj_by_name_v2(
                    engine_session, user, obj_name=self.user_name
                )
                log.print_debug(
                    "User reference {}".format(dxuser_obj.reference)
                )
                user_obj = User()
                if self.last_name:
                    user_obj.last_name = self.last_name
                if self.first_name:
                    user_obj.first_name = self.first_name
                if self.email_address:
                    user_obj.email_address = self.email_address
                user.update(engine_session, dxuser_obj.reference, user_obj)
                log.print_debug(
                    "User details updated. "
                    "Checking if passwords need to be udpated."
                )
                if self.current_password:
                    log.print_debug("Updating user password.")
                    credential = CredentialUpdateParameters()
                    credential.old_credential = PasswordCredential()
                    credential.old_credential.password = self.current_password
                    credential.new_credential = PasswordCredential()
                    credential.new_credential.password = self.new_password
                    user.update_credential(
                        engine_session, dxuser_obj.reference, credential
                    )
            log.print_info(
                f"User updated. "
                f"To verify password updates, "
                f"please login to Delphix using your new password."
            )
        except DlpxObjectNotFound as err:
            log.print_exception(err)
            err_msg = format_err_msg(
                f"Unable to find user {self.user_name}.",
                engine_name=engine_ref["hostname"],
                operation="USER_UPDATE",
                err_code=const.ERR_OBJ_NOTFOUND,
                object_name=self.user_name,
            )
            log.print_exception(err_msg)
            # raise DXIException(err_msg, const.ERR_OBJ_NOTFOUND)
            self.failures[0] = True
        except (Exception, BaseException) as err:
            err_msg = format_err_msg(
                err,
                engine_name=engine_ref["hostname"],
                object_name=self.user_name,
                operation="USER_UPDATE",
            )
            log.print_exception(err)
            self.failures[0] = True
        finally:
            self._remove_session(engine_session)

    def validate_inputs(self, operation):
        """
        Method to validate the inputs.
        Args:
            action: Type of the action performed by user.
        """
        log.print_debug("Validating inputs for dxi user operation.")
        log.print_debug("Action is {}".format(const.UserOps.UPDATE.name))
        if operation == const.UserOps.UPDATE:
            if xor(bool(self.current_password), bool(self.new_password)):
                err_msg = format_err_msg(
                    "Missing current_password or new_password in input.",
                    msg2="When changing password, both current and new passwords are required.",  # noqa
                    action="Provide current and new passwords.",
                    err_code=const.ERR_DXI_MISSINGINPUT,
                    operation="USER_UPDATE",
                )
                self.failures[0] = True
                log.print_exception(err_msg)
                raise DXIException(err_msg, const.ERR_DXI_MISSINGINPUT)
        elif operation == const.UserOps.UPDATEROLE:
            if self.action == "grant" and None in [
                self.target_type,
                self.target_name,
                self.user_role,
            ]:
                err_msg = format_err_msg(
                    "Missing required value in input.",
                    msg2="target_type, target_name and user_role are required inputs when action is 'grant'.",  # noqa
                    action="Provide inputs for target_type, target_name and user_role.",  # noqa
                    err_code=const.ERR_DXI_MISSINGINPUT,
                    operation="USER_UPDATEROLE",
                )
                self.failures[0] = True
                log.print_exception(err_msg)
                raise DXIException(err_msg, const.ERR_DXI_MISSINGINPUT)
