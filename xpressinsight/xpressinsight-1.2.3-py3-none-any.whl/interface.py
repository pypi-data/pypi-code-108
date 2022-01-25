"""
    Xpress Insight Python package
    =============================

    This is an internal file of the 'xpressinsight' package. Do not import it directly.
    Interface base class.

    This material is the confidential, proprietary, unpublished property
    of Fair Isaac Corporation.  Receipt or possession of this material
    does not convey rights to divulge, reproduce, use, or allow others
    to use it without the specific written authorization of Fair Isaac
    Corporation and use must conform strictly to the license agreement.

    Copyright (c) 2020-2022 Fair Isaac Corporation. All rights reserved.
"""

import datetime
import os
from dataclasses import dataclass, field
from typing import List, Optional, Union
from abc import ABC, abstractmethod
from xpressinsight import ExecMode
from xpressinsight.types import XiEnum, check_instance_attribute_types
from xpressinsight.repository_path import RepositoryPath

#


class InterfaceError(Exception):
    """
    An exception that occurred during a call to certain `AppInterface` methods.

    Attributes
    ----------
    message: str
        The error message.

    Notes
    -----
    `InterfaceError` is only used by certain `AppInterface` functions. For each function that uses this exception,
    the documentation explicitly mentions that the function may raise an `InterfaceError`.

    `InterfaceError` defines __str__() so the error type and message can be printed directly.

    Examples
    --------

    Example of using :fct-ref:`AppInterface.get_item_info` with error handling to obtain info for the current scenario.

    >>> @xi.ExecModeLoad()
    >>> def load(self):
    >>>     try:
    >>>         info = self.insight.get_item_info(".")
    >>>         print(info)
    >>>     except xi.InterfaceError as ex:
    >>>         print(ex)  # Print error type and message.
    >>>         # print("ERROR:", ex.message)  # Print error message.

    See Also
    --------
    AppInterface.get_item_info
    AppInterface.get_item_infos
    """
    def __init__(self, message: str):
        self.message = message

    def __str__(self) -> str:
        """ Prints the error message and the cause, if the cause is not `None`. """
        msg = f"{type(self).__name__}: {self.message}"
        cause = f" Caused by {type(self.__cause__).__name__}: {self.__cause__}"\
            if self.__cause__ is not None else ""
        return msg + cause


#
def _raise_runtime_error(message: str, cause: Exception = None):
    """ Used when Insight AppInterface is in an invalid state. """
    raise RuntimeError(message) from cause


#
def _raise_io_error(message: str, cause: Exception = None):
    """ Used when Insight AppInterface runs into an IO error. """
    #
    raise IOError(message) from cause


#
def _raise_interface_error(message: str, cause: Exception = None):
    """ Used for AppInterface functions, as an alternative to returning status codes. """
    raise InterfaceError(message) from cause


class Metric(XiEnum):
    """
    Indicates the type of metric a progress update is providing.

    Attributes
    ----------
    GAP : float
        The gap to the optimal solution, as a percentage.
    OBJVAL : float
        The best solution value found so far.
    NUMSOLS : float
        The count of feasible solutions found so far.
    OBJSENSE : xi.ObjSense
        The direction of the solve.

    See Also
    --------
    AppInterface.update
    AppInterface.reset_progress

    Notes
    -----
    This enumeration is used in the Insight progress updates methods.
    """

    GAP = 1
    OBJVAL = 2
    NUMSOLS = 3
    OBJSENSE = 4


class ObjSense(XiEnum):
    """
    Indicates the direction of optimization.

    Attributes
    ----------
    MINIMIZE : int
        This is a minimization problem.
    MAXIMIZE : int
        This is a maximization problem.

    See Also
    --------
    AppInterface.update
    AppInterface.reset_progress

    Notes
    -----
    This enumeration is used in the Insight progress updates methods.
    """

    MINIMIZE = 1
    MAXIMIZE = -1


#
class AttachType(XiEnum):
    """
    Possible values for attachment type
    """

    APP = "APP"
    SCENARIO = "SCENARIO"


#
class AttachStatus(XiEnum):
    """
    Indicates the status of the most recent attempt to access or modify an attachment.

    Attributes
    ----------
    OK : int
        The operation completed successfully.
    NOT_FOUND : int
        The specified attachment does not exist.
    INVALID_FILENAME : int
        An attachment could not be created or renamed because the specified filename is invalid. It may be too long, too short, or contain invalid characters.
    INVALID_DESCRIPTION : int
        The specified description is invalid. The description can be a maximum of 2500 characters in length.
    ALREADY_EXISTS : int
        An attachment could not be created because another attachment with the same name already exists.
    TOO_LARGE : int
        An attachment could not be created because the attached file is too large. Attachments can be a maximum of 150Mb in size.
    TOO_MANY : int
        An attachment could not be created because the maximum number of attachments (250) has been reached for the app or scenario.
    INVALID_TAGS : int
        Invalid tags were provided.
    SEVERAL_FOUND : int
        Several attachments match the given tag but the proxpressinsight

    Notes
    -----
    After every call to an attachment-related function or procedure, you should check the value of `insight.attach_status` to see if your request succeeded.
    """

    OK = 0
    NOT_FOUND = 1
    INVALID_FILENAME = 2
    INVALID_DESCRIPTION = 3
    ALREADY_EXISTS = 4
    TOO_LARGE = 5
    TOO_MANY = 6
    INVALID_TAGS = 7
    SEVERAL_FOUND = 8
    IN_PROGRESS = 254
    RUNTIME_ERROR = 255


#
class AttachUpdateType(XiEnum):
    """
    Possible values for attachment update type.
    """

    CREATE = "CREATE"
    DELETE = "DELETE"

    CONTENT = "CONTENT"
    FILENAME = "FILENAME"
    DESCRIPTION = "DESCRIPTION"
    TAGS = "TAGS"
    HIDDEN = "HIDDEN"


#
class AttachTagUsage(XiEnum):
    """
    Possible values for attachment tag usage.

    Attributes
    ----------
    SINGLE_FILE: str
        This tag may only be assigned to at most one attachment file.
    MULTI_FILE: str
        This tag may only be assigned to any number of attachment files.
    """

    SINGLE_FILE = "single-file"
    MULTI_FILE = "multi-file"


#
@dataclass  #
class AttachTag:
    """
    A class containing information about a tag defined in the app's companion file.

    Attributes
    ----------
    name: str
        Name of the tag.
    description: str
        Description of the tag.
    mandatory: bool
        Whether the tag is mandatory.
    usage: AttachTagUsage
        Tag usage restrictions, either `AttachTagUsage.SINGLE_FILE` or `AttachTagUsage.MULTI_FILE`.

    See Also
    --------
    AppInterface.list_attach_tags

    Notes
    -----
    Modifying an `AttachTag` record will not modify the attachment tag information on the server.
    """

    name: str = field(default="")
    description: str = field(default="")
    mandatory: bool = field(default=False)
    usage: AttachTagUsage = field(default=AttachTagUsage.MULTI_FILE)


#
#
@dataclass
class Attachment:
    """
    An object containing information about a single attachment.

    Attributes
    ----------
    filename: str
        filename of the attachment
    description: str
        description of the attachment
    tags: List[str]
        collection of tags associated with the attachment
    size: int
        size of the attachment, in bytes
    last_modified_user: str
        name of the last Insight user to modify the attachment
    last_modified_date: datetime.datetime
        date and time of last modification to attachment
    hidden: bool
        whether the attachment is hidden from the UI
    """

    filename: str = field(default="")
    description: str = field(default="")
    tags: List[str] = field(default_factory=list)
    size: int = field(default=0)
    last_modified_user: str = field(default="")
    last_modified_date: Optional[datetime.datetime] = field(default=None)
    hidden: bool = field(default=False)


#
@dataclass
class AttachmentRules:
    """
    A class containing information about the rules used by Insight when verifying attachments.

    Attributes
    ----------
    max_size: int
        The maximum size, in bytes, that an attachment may have.
    max_attach_count: int
        The maximum number of attachments that can be attached to a single scenario.
    max_filename_len: int
        The maximum permitted length, in characters, of an attachment filename.
    invalid_filename_chars: List[str]
        A list of characters that are not permitted in attachment filenames.
        Must be a list of single-character string values.
    max_description_len: int
        The maximum permitted length, in characters, of an attachment description.

    See Also
    --------
    AppInterface.set_attach_rules
    AppInterface.test_mode

    Notes
    -----
    This object is used only in test mode.
    """

    max_size: int = field(default=0)
    max_attach_count: int = field(default=0)
    max_filename_len: int = field(default=0)

    #
    invalid_filename_chars: List[str] = field(default_factory=list)

    max_description_len: int = field(default=0)


#
@dataclass
class ItemInfo:
    """
    A class containing information for a repository item.

    Attributes
    ----------
    id: str
        Item id.
    type: str
        Item type (`"FOLDER"` or scenario type identifier). Default: 'SCENARIO'.
    name: str
        Item name.
    path: str
       Item path. Equivalent to `parent_path + xi.RepositoryPath.encode_element(name)`,
       except for application root folders.
    parent_path: str
        Item parent path. Begins and ends with a slash '/'.

    See Also
    --------
    AppInterface.get_item_info
    AppInterface.get_item_infos
    AppInterface.add_item_info
    AppInterface.clear_item_infos
    RepositoryPath
    """

    id: str = field()
    type: str = field(default="SCENARIO")
    name: str = field(default="")
    path: str = field(default="")
    parent_path: str = field(default="")

    def normalize(self):
        """ Validate the attribute values of the ItemInfo and normalize the path attributes. """
        check_instance_attribute_types(self)

        if self.id == '':
            #
            #
            raise ValueError("The ItemInfo id must not be the empty string.")

        if self.name in ['', '.', '..']:
            raise ValueError('The ItemInfo name cannot be equal to "", ".", or "..".')

        #
        for path_name in ['path', 'parent_path']:
            if not self.__dict__[path_name].startswith("/"):
                raise ValueError(f'The ItemInfo {path_name} must be absolute (start with "/"), '
                                 f'but it is: {self.__dict__[path_name]}')

        #
        norm_root = RepositoryPath('/')  #
        norm_path = RepositoryPath(self.path).abspath(norm_root)
        norm_parent_path = RepositoryPath(self.parent_path).abspath(norm_path)
        norm_path_len = len(norm_path.elements)
        norm_path_str = str(norm_path)
        norm_parent_path_str = str(norm_parent_path)

        if norm_path_len == 0:
            raise ValueError(f'The normalized ItemInfo path cannot be empty, but it is '
                             f'(before normalization): {self.path}')
        elif norm_path_len == 1:
            #
            if self.name != 'Root':
                raise ValueError(f'The ItemInfo name of the application root folder must '
                                 f"be 'Root', but it is '{self.name}'. Folder path: {norm_path_str}")

            if self.type != 'FOLDER':
                raise ValueError(f'The ItemInfo type of the application root folder must '
                                 f"be 'FOLDER', but it is '{self.type}'. Folder path: {norm_path_str}")

            if norm_parent_path_str != norm_path_str:
                raise ValueError(f'The ItemInfo parent_path of the application root folder must '
                                 f"be equal to its path '{norm_path_str}', but it is: {self.parent_path}")
        else:
            #
            norm_parent_path.append(self.name)
            norm_path_str_expected = str(norm_parent_path)

            if norm_path_str != norm_path_str_expected:
                raise ValueError(f"The ItemInfo path must be '{norm_path_str_expected}', but it is: {norm_path_str}")

        self.path = norm_path_str
        self.parent_path = norm_parent_path_str + '/'  #


class AppInterface(ABC):
    """
    This class represents the Xpress Insight application interface. Use this interface to access attachments
    and meta data like the scenario ID.
    """

    #
    def __init__(
            self,
            app_id: str = "",
            app_name: str = "",
            scenario_id: str = "",
            scenario_name: str = "",
            scenario_path: str = "",
            exec_mode: str = ExecMode.NONE,  #
            test_mode: bool = True,
            test_attach_dir: str = "",
            test_cfile_path: str = "",
            #
            force_wdir_to_temp: bool = False,  #
            #
            tmp_dir: str = "",  #
            work_dir: str = os.path.join("work_dir", "insight"),
    ) -> None:
        """
        Constructor of the Insight application interface.

        Parameters
        ----------
        app_id : str
            The globally unique identifier string for the application in the Xpress-Insight repository.
        app_name : str
            The name of the application in the Xpress-Insight repository.
        scenario_id : str
            The globally unique identifier string for the scenario in the Xpress-Insight repository.
        scenario_name : str
            The name of the scenario in the Xpress-Insight repository.
        scenario_path : str
            The repository path of the current scenario in the Xpress-Insight repository.
        exec_mode : str
            The Execution Mode to apply to the current scenario in the Xpress-Insight repository.
        test_mode : bool
            Whether the `xpressinsight` package is running in test mode.
        test_attach_dir : str
            Location to store mock attachments for app and scenario, when in test mode.
        test_cfile_path : str
            Location of the app companion file to parse, when in test mode.
        force_wdir_to_temp : bool
            Set to `True` to force insight to set the working directory.
        tmp_dir : str
            Mosel tmpdir parameter.
        work_dir : str
            Internal working directory of the `xpressinsight` package.
        """
        #
        self._app_id: str = app_id
        self._app_name: str = app_name
        self._scenario_id: str = scenario_id
        self._scenario_name: str = scenario_name
        self._scenario_path: str = scenario_path
        self._exec_mode: str = exec_mode
        self._test_mode: bool = test_mode
        self._test_attach_dir: str = test_attach_dir
        self._test_cfile_path: str = test_cfile_path
        self._force_wdir_to_temp: bool = force_wdir_to_temp
        self._tmp_dir: str = os.path.abspath(tmp_dir)
        self._work_dir: str = os.path.abspath(work_dir)

    @property
    @abstractmethod
    def work_dir(self) -> str:
        """
        Read-only property for the internal working directory of the `xpressinsight` package.

        Returns
        -------
        work_dir : str
            Absolute path to the internal working directory of the `xpressinsight` package.
        """

        pass

    @abstractmethod
    def delete_work_dir(self):
        """
        Delete the internal working directory of the `xpressinsight` package.

        See Also
        --------
        AppInterface.work_dir

        Notes
        -----
        In test mode, this function deletes the internal working directory. It is recommended to call this function
        at the beginning of a test, such that the test does not load data from the working directory of a previous
        test run.

        If the working directory does not exist, the function returns immediately. If the working
        directory cannot be deleted, e.g., because another application has a lock on a file, the function
        raises an exception.

        Setting this property when :param-ref:`insight.test_mode` is `False` will cause the model to abort with
        a runtime error.
        """

        pass

    @property
    @abstractmethod
    def test_mode(self) -> bool:
        """
        Read-only property to check whether the Insight application is running in test mode or in Insight.

        Returns
        -------
        test_mode : bool
            `True` if the application is executed in test mode and `False` if it is running in Insight.

        Notes
        -----
        When the application is running in Insight, then the value is `False`, otherwise the value is `True`.
        """

        pass

    #
    @property
    @abstractmethod
    def exec_mode(self) -> str:
        """
        Property for the execution mode in which Xpress Insight is running the model. :index-name:`run mode`

        Returns
        -------
        exec_mode : str
            The name of the current execution mode, as specified in the execution mode decorators.
            This can be a user-defined value, or can be one of these pre-defined standard values:
            `xi.ExecMode.LOAD` (when a scenario is being loaded),
            `xi.ExecMode.RUN`  (when a scenario is being run),
            `xi.ExecMode.NONE` (when the application is being executed outside of Xpress Insight
                                and no execution mode function is currently being executed).

        Examples
        --------
        Demonstration of setting the execution mode (test mode only).

        >>> insight.exec_mode = 'CALCULATE_STATS'

        Demonstration of getting the execution mode then outputting it.

        >>> print('execution mode = ', insight.exec_mode)
        execution mode = CALCULATE_STATS

        Notes
        -----
        The `exec_mode` property can only be set in test mode.

        In the `LOAD` execution mode function (or other user-defined execution modes with `clear_input=True`)
        your app should initialize its input data.
        In the `RUN` execution mode function (or user-defined execution modes with `clear_input=False`)
        it should then initialize its result data.

        Used to mock the execution mode that requested the scenario execution, when testing code outside of an Insight
        scenario. By default, :fct-ref:`insight.exec_mode` will be initialized automatically if you call an execution
        mode function. However, if you want to test another function, which is not an execution mode function,
        then it could make sense to set the `exec_mode` property manually.

        Modifying this property when :param-ref:`insight.test_mode` is `False` will cause the model to abort with a
        runtime error.
        """

        pass

    #
    @exec_mode.setter
    @abstractmethod
    def exec_mode(self, exec_mode: str):
        pass

    #
    @property
    @abstractmethod
    def app_id(self) -> str:
        """
        Property for the id of the Xpress Insight application which is the parent of the model.

        Returns
        -------
        app_id : str
            The UID of the Xpress Insight application.

        Examples
        --------
        Demonstration of setting the application ID (test mode only).

        >>> insight.app_id = 'xyzzy'

        Demonstration of getting the application ID then outputting it.

        >>> print('app id = ', insight.app_id)
        app id = xyzzy

        Notes
        -----
        The `app_id` property can only be set in test mode.

        In test mode can be used to mock the Insight application state when testing code outside of an Insight scenario.

        Modifying this property when `insight.test_mode` is `False` will cause the model to abort with a runtime error.
        """

        pass

    #
    @app_id.setter
    @abstractmethod
    def app_id(self, new_app_id: str):
        pass

    #
    @property
    @abstractmethod
    def app_name(self) -> str:
        """
        Property for the name of the Xpress Insight application which is the parent of the model.

        Returns
        -------
        app_name : str
            The name of the application.

        Examples
        --------
        Demonstration of setting the application name (test mode only).

        >>> insight.app_name = 'My App'

        Demonstration of getting the application name then outputting it.

        >>> print('app name = ', insight.app_name)
        app name = My App

        Notes
        -----
        The `app_name` property can only be set in test mode.

        The application name is not related to the name defined in the model's source code.

        Used to mock the Insight application state when testing code outside of an Insight scenario.

        Modifying this property when `insight.test_mode` is `False` will cause the model to abort with a runtime error.
        """

        pass

    #
    @app_name.setter
    @abstractmethod
    def app_name(self, new_app_name: str):
        pass

    #
    @property
    @abstractmethod
    def username(self) -> str:
        """
        Property for the username of the Insight user that initiated the current scenario execution. :index-name:`Insight user name`

        Returns
        -------
        username : str
            The user name.

        Examples
        --------
        Demonstration of setting the user name (test mode only).

        >>> insight.username = 'LouisXIV'

        Demonstration of getting the user name then outputting it.

        >>> print('user name = ', insight.username)
        user name = LouisXIV

        Notes
        -----
        The `username` property can only be set in test mode.

        When called while the model is not running within Insight, this returns `DEV`.

        The username returned will be the username suitable for human display - be aware that this is
        not a unique identifier for the user's account, as users can change their names.

        Used to mock the user who requested the scenario execution, when testing code outside of an Insight scenario.

        Modifying this property when :param-ref:`insight.test_mode` is `False` will cause the model to abort with a runtime error.
        """

        pass

    #
    @username.setter
    @abstractmethod
    def username(self, new_username: str):
        pass

    @property
    @abstractmethod
    def test_cfile_path(self) -> str:
        """
        Property for the location of the app companion file to parse, when in test mode.

        Returns
        -------
        cfile_path : str
            The path to the app companion file.

        Examples
        --------
        Demonstration of setting the companion file path (test mode only).

        >>> insight.test_cfile_path = 'C:/dev/app/application.xml'

        Demonstration of getting the companion file path (test mode only).

        >>> print(insight.test_cfile_path)
        """

        pass

    @test_cfile_path.setter
    @abstractmethod
    def test_cfile_path(self, cfile_path: str):
        pass

    @property
    @abstractmethod
    def test_attach_dir(self) -> str:
        """
        Property for the location to store mock attachments for app and scenario, when in test mode.

        Returns
        -------
        attach_dir : str
            The path to the attachments directory.

        See Also
        --------
        AppInterface.test_app_attach_dir
        AppInterface.test_scen_attach_dir

        Examples
        --------
        Demonstration of setting the attachment directory (test mode only).

        >>> insight.test_attach_dir = 'C:/dev/appattachments'

        Demonstration of getting the attachment directory (test mode only).

        >>> print(insight.test_attach_dir)
        """

        pass

    @test_attach_dir.setter
    @abstractmethod
    def test_attach_dir(self, attach_dir: str):
        pass

    #
    @property
    @abstractmethod
    def test_app_attach_dir(self) -> str:
        """
        Property for the path to use for the attachments directory of the current app, when in test mode.

        Returns
        -------
        app_attach_dir : str
            The path to the app attachments directory.

        See Also
        --------
        AppInterface.test_attach_dir
        AppInterface.test_scen_attach_dir

        Examples
        --------
        Demonstration of getting the app attachment directory (test mode only).

        >>> print(insight.test_app_attach_dir)

        Demonstration of setting the app attachment directory (test mode only).

        >>> insight.test_app_attach_dir = 'C:/dev/appattachments'

        Notes
        -----
        When you set a path using this function, it will be used instead of the `appattach` subdirectory of
        the directory specified by :param-ref:`insight.test_attach_dir` property.

        Setting this propery when :param-ref:`insight.test_mode` is `False` will cause the model to abort with a runtime error.
        """

        pass

    @test_app_attach_dir.setter
    @abstractmethod
    def test_app_attach_dir(self, app_attach_dir: str):
        pass

    #
    @property
    @abstractmethod
    def test_scen_attach_dir(self) -> str:
        """
        Property for the path to use for the scenario attachments directory of the current scenario.

        Returns
        -------
        scen_attach_dir : str
            The path to the scenario attachments directory.

        See Also
        --------
        AppInterface.test_attach_dir
        AppInterface.test_app_attach_dir

        Examples
        --------
        Demonstration of setting scenario attachment directory (test mode only).

        >>> insight.test_scen_attach_dir = 'C:/dev/scenattachments'

        Demonstration of getting scenario attachment directory (test mode only).

        >>> print(insight.test_scen_attach_dir)

        Notes
        -----
        When you set a path using this function, it will be used instead of the `scenattach` subdirectory of
        the directory specified by :param-ref:`insight.test_attach_dir` property.

        Setting this property when :param-ref:`insight.test_mode` is `False` will cause the model to abort with a runtime error.
        """

        pass

    @test_scen_attach_dir.setter
    @abstractmethod
    def test_scen_attach_dir(self, scen_attach_dir: str):
        pass

    #
    @abstractmethod
    def set_attach_tags(self, new_tags: List[AttachTag]):
        """
        Sets the list of tags that can be used in attachments

        Parameters
        ----------
        new_tags : List[AttachTag]
            List of populated `insightattachmenttag` records.

        See Also
        --------
        AppInterface.list_attach_tags
        AppInterface.set_attach_tags

        Examples
        --------
        Demonstration of setting the available tags

        >>> insight.set_attach_tags([
        ...     AttachTag(name='first', usage=AttachTagUsage.SINGLE_FILE),
        ...     AttachTag(name='test', usage=AttachTagUsage.MULTI_FILE),
        ... ])

        Notes
        -----
        Used to mock the available attachment tags when testing code outside of an Insight scenario.

        The `AttachTagUsage.SINGLE_FILE` usage constraint will only be applied during future calls to modify attachment tags.  It
        will not be applied to attachments that are already tagged when `insight.set_attach_tags` is called.

        Setting this property when :param-ref:`insight.test_mode` is `False` will cause the model to abort with a runtime error.
        """

        pass

    #
    @abstractmethod
    def set_attach_rules(self, new_rules: AttachmentRules):
        """
        Sets the 'rules' used to validate attachments and attachment meta-data.

        Parameters
        ----------
        new_rules : AttachmentRules
            Populated `insightattachmentrules` record

        Examples
        --------
        Demonstration of setting the example rules

        >>> insight.set_attach_rules(AttachmentRules(
        ...     max_size=1*1024*1024,
        ...     max_attach_count=25,
        ...     max_filename_len=32,
        ...     invalid_filename_chars=['/', r'\', ' '],
        ...     max_description_len=128,
        ... ))

        Notes
        -----
        Used to change the rules that are applied to new attachments - for example, if you want to test how your
        code responds to the `AttachStatus.TOO_MANY` error code without actually creating a lot of attachments, you can
        use this procedure to set a lower number of attachments per scenario.

        Setting this property when :param-ref:`insight.test_mode` is `False` will cause the model to abort with a runtime error.
        """

        pass

    #
    @property
    @abstractmethod
    def attach_status(self) -> AttachStatus:
        """
        Read-only property indicating the status of the most recent attempt to access or modify an attachment. :index-name:`attachment operation error codes`

        See Also
        --------
        AttachStatus
        AppInterface.get_scen_attach
        AppInterface.list_scen_attach
        AppInterface.list_scen_attach_by_tag
        AppInterface.put_scen_attach
        AppInterface.rename_scen_attach
        AppInterface.scen_attach_info
        AppInterface.set_scen_attach_desc
        AppInterface.set_scen_attach_hidden
        AppInterface.set_scen_attach_tags
        AppInterface.get_app_attach
        AppInterface.list_app_attach
        AppInterface.list_app_attach_by_tag
        AppInterface.app_attach_info

        Notes
        -----
        After every call to an attachment-related function or procedure, you should check the value of `insight.attach_status` to see if your request succeeded.
        """

        pass

    #
    #

    #
    @abstractmethod
    def list_attach_tags(self) -> List[AttachTag]:
        """
        Retrieves a list of the attachment tags defined in the companion file. :index-name:`list attachment tags`

        Returns
        -------
        attach_tags : List[AttachTag]
            A list of the defined tags.

        See Also
        --------
        AppInterface.set_scen_attach_tags

        Examples
        --------
        Example of outputting list of tags defined in companion file

        >>> tags = insight.list_attach_tags()
        ... if insight.attach_status == AttachStatus.OK:
        ...     print("Defined tags: ", tagslist)
        ... else:
        ...     print("Error retrieving tags list")

        Notes
        -----
        Check the attachment status code using :fct-ref:`insight.attach_status` to determine whether the attachment was successfully fetched.
        """

        pass

    #
    #
    @abstractmethod
    def get_scen_attach(self, filename: str, scenario_path: str = None) -> None:
        """
        Retrieves an attachment from the Insight server either for a given scenario, placing it in the Python working directory where it can be read by the model. :index-name:`get scenario attachment`

        Parameters
        ----------
        filename : str
            The filename of the attachment to be retrieved.
        scenario_path : str
            The path of a scenario. A scenario path is the full path to a scenario name starting from the repository root
            and including the app name. E.g. `/myapp/DirA/myscenario`
            If the scenario path is not specified, the attachment is retrieved for the current scenario.

        See Also
        --------
        AppInterface.attach_status
        AppInterface.put_scen_attach

        Examples
        --------
        Example of copying a scenario attachment called `my_attach.dat` to the working directory.

        >>> insight.get_scen_attach('my_attach.dat')
        ... if insight.attach_status == AttachStatus.OK:
        ...     with open('my_attach.dat') as f:
        ...         pass  # process the file
        ... else:
        ...     print("Error retrieving attachment")

        Getting an attachment for the current scenario.

        >>> insight.get_scen_attach('my_attach.dat', '/myapp/DirA/myscenario')
        ... if insight.attach_status == AttachStatus.OK:
        ...     with open('my_attach.dat') as f:
        ...         pass  # process the file
        ... else:
        ...     print("Error retrieving attachment")

        Getting an attachment for a scenario with path `/myapp/DirA/myscenario`.

        Notes
        -----
        Check the attachment status code using :fct-ref:`insight.attach_status` to determine whether the attachment was successfully fetched.

        Attempting to access attachments when the model is not being run through Xpress Insight will cause the model to abort with an error.
        """

        pass

    #
    #
    @abstractmethod
    def put_scen_attach(self, filename: str, overwrite: bool = True) -> None:
        """
        Uploads a scenario attachment to the Insight server, reading it from the Python working directory. :index-name:`put scenario attachment`

        Parameters
        ----------
        filename : str
            The filename of the attachment to be uploaded
        overwrite : bool
            If `True`, will overwrite attachment if it already exists.  If `False`
            and attachment already exists, will fail with insight.attach_status returning
            AttachStatus.ALREADY_EXISTS. Defaults to `True` if not given.

        See Also
        --------
        AppInterface.attach_status
        AppInterface.get_scen_attach

        Examples
        --------
        Example of taking a file `my_attach.dat` in the working directory, and saving it as a new scenario attachment called `my_attach.dat`.

        >>> insight.put_scen_attach('my_attach.dat', False)
        ... if insight.attach_status == AttachStatus.OK:
        ...     print("Attachment added ok")
        ... elif insight.attach_status == AttachStatus.ALREADY_EXISTS:
        ...     print("Attachment already exists")
        ... else:
        ...     print("Error adding attachment:", insight.attach_status)

        Notes
        -----
        Check the attachment status code using :fct-ref:`insight.attach_status` to determine whether the attachment was successfully added.

        The new attachment will not be available on the Insight server until the scenario completes.

        Attempting to access attachments when the model is not being run through Xpress Insight will cause the model to abort with an error.
        """

        pass

    #
    @abstractmethod
    def delete_scen_attach(self, filename: str) -> None:
        """
        Deletes a scenario attachment. :index-name:`delete scenario attachment`

        Parameters
        ----------
        filename : str
            The filename of the attachment to be deleted.

        See Also
        --------
        AppInterface.attach_status

        Examples
        --------
        Example of deleting an attachment called `my_attach.dat` from the current scenario.

        >>> insight.delete_scen_attach('my_attach.dat')
        ... if insight.attach_status == AttachStatus.OK:
        ...     print("Attachment deleted")
        ... else:
        ...     print("Error deleting attachment")

        Notes
        -----
        Check the attachment status code using :fct-ref:`insight.attach_status` to determine whether the attachment will be successfully deleted.

        The attachment will still be available on the Insight server until the scenario completes.

        Attempting to access attachments when the model is not being run through Xpress Insight will cause the model to abort with an error.
        """

        pass

    #
    @abstractmethod
    def rename_scen_attach(self, old_name: str, new_name: str) -> None:
        """
        Renames an existing scenario attachment.

        Parameters
        ----------
        old_name : str
            The existing filename of the attachment to be renamed
        new_name : str
            The new filename of the attachment.  Must not already be used for a scenario attachment. :index-name:`rename scenario attachment`

        See Also
        --------
        AppInterface.attach_status

        Examples
        --------
        Example of renaming an existing attachment of the current scenario from `my_attach.dat` to `my_attach-2015.dat`.

        >>> insight.rename_scen_attach('my_attach.dat', 'my_attach-2015.dat')
        ... if insight.attach_status == AttachStatus.OK:
        ...     print("Attachment renamed ok")
        ... else:
        ...     print("Error renaming attachment")

        Notes
        -----
        Check the attachment status code using :fct-ref:`insight.attach_status` to determine whether the new attachment name was accepted.

        The attachment will not be renamed on the Insight server until the scenario completes.

        Attempting to access attachments when the model is not being run through Xpress Insight will cause the model to abort with an error.
        """

        pass

    #
    @abstractmethod
    def set_scen_attach_desc(self, filename: str, description: str) -> None:
        """
        Update the description of an existing scenario attachment. :index-name:`set scenario attachment description`

        Parameters
        ----------
        filename : str
            The filename of the scenario attachment to update
        description : str
            The new description of the attachment

        See Also
        --------
        AppInterface.attach_status

        Examples
        --------
        Example of setting the description of a scenario attachment `my_attach.dat` to be "`This is my first attachment`"

        >>> insight.set_scen_attach_desc('my_attach.dat',
        ...                              'This is my attachment')
        ... if insight.attach_status == AttachStatus.OK:
        ...     print("Attachment description updated ok")
        ... else:
        ...     print("Error updating attachment")

        Notes
        -----
        Check the attachment status code using :fct-ref:`insight.attach_status` to determine whether the new attachment description was accepted.

        The attachment will not be updated on the Insight server until the scenario completes.

        Attempting to access attachments when the model is not being run through Xpress Insight will cause the model to abort with an error.
        """

        pass

    #
    @abstractmethod
    def set_scen_attach_tags(self, filename: str, tags: List[str]) -> None:
        """
        Update the tags of an existing scenario attachment. :index-name:`set scenario attachment tags`

        Parameters
        ----------
        filename : str
            The filename of the scenario attachment to update.
        tags : List[str]
            The new tags to apply to the attachment.  Any existing tags will be removed.

        See Also
        --------
        AppInterface.attach_status

        Examples
        --------
        Example of setting the tags of a scenario attachment `my_attach.dat` to be "mytag1" and "mytag2"

        >>> insight.set_scen_attach_tags('my_attach.dat',
        ...                              ['mytag1', 'mytag2'])
        ... if insight.attach_status == AttachStatus.OK:
        ...     print("Attachment tags updated ok")
        ... else:
        ...     print("Error updating attachment")

        Notes
        -----
        Check the attachment status code using :fct-ref:`insight.attach_status` to determine whether the new attachment tags were accepted.

        The attachment will not be updated on the Insight server until the scenario completes.

        Attempting to access attachments when the model is not being run through Xpress Insight will cause the model to abort with an error.

        If any of the specified tags are single-file tags, they will be removed from other scenarios as part of this operation.
        """

        pass

    #
    @abstractmethod
    def set_scen_attach_hidden(self, filename: str, hidden: bool) -> None:
        """
        Mark an existing scenario attachment as hidden or visible in the Xpress Insight UI. :index-name:`set scenario attachment hidden`

        Parameters
        ----------
        filename : str
            The filename of the scenario attachment to hide or show.
        hidden : bool
            If `True`, the attachment will be hidden in the Xpress Insight UI; if `False`, it will be visible.

        See Also
        --------
        AppInterface.attach_status

        Examples
        --------
        Example of hiding of a scenario attachment `my_attach.dat`

        >>> insight.set_scen_attach_hidden('my_attach.dat', True)
        ... if insight.attach_status == AttachStatus.OK:
        ...     print("Attachment hidden ok")
        ... else:
        ...     print("Error hiding attachment")

        Notes
        -----
        Check the attachment status code using :fct-ref:`insight.attach_status` to determine whether the update was successful.

        The attachment will not be updated on the Insight server until the scenario completes.

        Attempting to access attachments when the model is not being run through Xpress Insight will cause the model to abort with an error.
        """

        pass

    #
    #
    @abstractmethod
    def list_scen_attach(self, scenario_path: str = None) -> List[Attachment]:
        """
        Retrieves a list of all the files attached to a given scenario. :index-name:`list scenario attachments`

        Parameters
        ----------
        scenario_path : str, optional
            The path of a scenario. A scenario path is the full path to a scenario name starting from the repository root
            and including the app name. E.g. `/myapp/DirA/myscenario`
            If the scenario path is not specified, the attachment is retrieved for the current scenario

        Returns
        -------
        attachments : List[Attachment]
            A list of the scenario attachments.

        See Also
        --------
        AppInterface.attach_status
        AppInterface.get_scen_attach
        AppInterface.list_scen_attach_by_tag

        Examples
        --------
        Example of fetching information about all attachments of a scenario into a list called `atts`

        >>> atts = insight.list_scen_attach()
        ... if insight.attach_status == AttachStatus.OK:
        ...     print("Attachments: ", atts)
        ... else:
        ...     print("Error listing attachments")

        Getting the list of attachments for the current scenario

        >>> atts = insight.list_scen_attach('/myapp/DirA/myscenario')
        ... if insight.attach_status == AttachStatus.OK:
        ...     print("Attachments: ", atts)
        ... else:
        ...     print("Error listing attachments")

        Getting the list of attachments for a scenario with path `/myapp/DirA/myscenario`

        Notes
        -----
        Check the attachment status code using :fct-ref:`insight.attach_status` to determine whether the attachments list was successfully retrieved.
        Attempting to access attachments when the model is not being run through Xpress Insight will cause the model to abort with an error.
        """

        pass

    #
    #
    @abstractmethod
    def list_scen_attach_by_tag(
            self, tag: str, scenario_path: str = None
    ) -> List[Attachment]:
        """
        Retrieves a list of all the files attached to a scenario with the given tag. :index-name:`list scenario attachments by tag`

        Parameters
        ----------
        tag : str
            The tag to search for
        scenario_path : str
            The path of a scenario. A scenario path is the full path to a scenario name starting from the repository root
            and including the app name. E.g. `/myapp/DirA/myscenario`.
            If the scenario path is not specified, the attachment is retrieved for the current scenario.

        Returns
        -------
        attachments : List[Attachment]
            A list of the scenario attachments.

        See Also
        --------
        AppInterface.attach_status
        AppInterface.get_scen_attach
        AppInterface.list_scen_attach

        Examples
        --------
        Example of fetching information about all attachments on a scenario with the tag `tag1` into a list called `atts`

        >>> atts = insight.list_scen_attach_by_tag('mytag1')
        ... if insight.attach_status == AttachStatus.OK:
        ...     print("Attachments: ", atts)
        ... else:
        ...     print("Error listing attachments")

        Getting the list of attachments for the current scenario with the given tag.

        >>> atts = insight.list_scen_attach_by_tag('mytag1',
        ...                                        '/myapp/DirA/myscenario')
        ... if insight.attach_status == AttachStatus.OK:
        ...     print("Attachments: ", atts)
        ... else:
        ...     print("Error listing attachments")

        Getting the list of attachments with the given tag for a scenario with path `/myapp/DirA/myscenario`.

        Notes
        -----
        Check the attachment status code using :fct-ref:`insight.attach_status` to determine whether the attachments list was successfully retrieved.

        Attempting to access attachments when the model is not being run through Xpress Insight will cause the model to abort with an error.
        """

        pass

    #
    @abstractmethod
    def scen_attach_info(self, filename: str) -> Optional[Attachment]:
        """
        Retrieves information about a given scenario attachment. :index-name:`query scenario attachment`

        Parameters
        ----------
        filename : str
            The filename of the scenario attachment to request

        Returns
        -------
        attachment : Optional[Attachment]
            Information about the attachment.

        See Also
        --------
        AppInterface.attach_status
        AppInterface.set_scen_attach_desc

        Examples
        --------
        Example of copying information about the attachment `my_attach.dat` on the current scenario into a record called `my_attachment`

        >>> my_attachment = insight.scen_attach_info('my_attach.dat')
        ... if insight.attach_status == AttachStatus.OK:
        ...     print("Attachment description: ", my_attachment.description)
        ... else:
        ...     print("Error querying attachment")

        Notes
        -----
        Check the attachment status code using :fct-ref:`insight.attach_status` to determine whether the attachments information was successfully retrieved.
        Attempting to access attachments when the model is not being run through Xpress Insight will cause the model to abort with an error.
        """

        pass

    #
    @abstractmethod
    def get_app_attach(self, filename: str) -> None:
        """
        Retrieves an app attachment from the Insight server, placing it in the Python working directory where it can be read by the model. :index-name:`get app attachment`

        Parameters
        ----------
        filename : str
            The filename of the attachment to be retrieved.

        See Also
        --------
        AppInterface.attach_status

        Examples
        --------
        Example of copying an app attachment called `my_attach.dat` to the working directory.

        >>> insight.get_app_attach('my_attach.dat')
        ... if insight.attach_status == AttachStatus.OK:
        ...     with open('my_attach.dat') as f:
        ...         pass  # process the file
        ... else:
        ...     print("Error retrieving attachment")

        Notes
        -----
        Check the attachment status code using :fct-ref:`insight.attach_status` to determine whether the attachment was successfully fetched.

        Attempting to access attachments when the model is not being run through Xpress Insight will cause the model to abort with an error.
        """

        pass

    #
    @abstractmethod
    def list_app_attach(self) -> List[Attachment]:
        """
        Retrieves a list of all the files attached to the app. :index-name:`list app attachments`

        Returns
        -------
        attachments : List[Attachment]
            A list of the app attachments.

        See Also
        --------
        AppInterface.attach_status
        AppInterface.app_attach_info
        AppInterface.get_app_attach
        AppInterface.list_app_attach_by_tag

        Examples
        --------
        Example of fetching information about all attachments on the app containing the current scenario into a list called `atts`

        >>> atts = insight.list_app_attach()
        ... if insight.attach_status == AttachStatus.OK:
        ...     print("Attachments: ", atts)
        ... else:
        ...     print("Error listing attachments")

        Notes
        -----
        Check the attachment status code using :fct-ref:`insight.attach_status` to determine whether the attachments list was successfully retrieved.

        Attempting to access attachments when the model is not being run through Xpress Insight will cause the model to abort with an error.
        """

        pass

    #
    @abstractmethod
    def list_app_attach_by_tag(self, tag: str) -> List[Attachment]:
        """
        Retrieves a list of all the files attached to the app with the given tag. :index-name:`list app attachments by tag`

        Parameters
        ----------
        tag : str
            The tag to search for

        Returns
        -------
        attachments : List[Attachment]
            A list of the app attachments.

        See Also
        --------
        AppInterface.attach_status
        AppInterface.get_app_attach
        AppInterface.list_app_attach

        Examples
        --------
        Example of fetching information about all attachments on the app with the tag `tag1` into a list called `atts`

        >>> atts = insight_list_app_attach_by_tag('mytag1')
        ... if insight.attach_status == AttachStatus.OK:
        ...     print("Attachments: ", atts)
        ... else:
        ...     print("Error listing attachments")

        Notes
        -----
        Check the attachment status code using :fct-ref:`insight.attach_status` to determine whether the attachments list was successfully retrieved.

        Attempting to access attachments when the model is not being run through Xpress Insight will cause the model to abort with an error.
        """

        pass

    #
    @abstractmethod
    def app_attach_info(self, filename: str) -> Optional[Attachment]:
        """
        Retrieves information about a given app attachment. :index-name:`query app attachment`

        Parameters
        ----------
        filename : str
            The filename of the app attachment to request

        Returns
        -------
        attachment : Optional[Attachment]
            Information about the attachment.

        See Also
        --------
        AppInterface.attach_status

        Examples
        --------
        Example of copying information about the attachment `my_attach.dat` on the app containing the current scenario into a record called `my_attachment`

        >>> my_attachment = insight.app_attach_info('my_attach.dat')
        ... if insight.attach_status == AttachStatus.OK:
        ...     print("Attachment description: ", my_attachment.description)
        ... else:
        ...     print("Error querying attachment")

        Notes
        -----
        Check the attachment status code using :fct-ref:`insight.attach_status` to determine whether the attachments information was successfully retrieved.
        Attempting to access attachments when the model is not being run through Xpress Insight will cause the model to abort with an error.
        """

        pass

    #
    @abstractmethod
    def get_attachs_by_tag(self, tag: str) -> Optional[List[Attachment]]:
        """
        Gets Insight attachments by tag

        Searches the scenario and the containing app for an attachment or attachments with the given tag, and
        retrieves them from the Insight server, placing them in the Python working directory where they can be read by
        the model. If any scenario attachments with the given tag are found, these are retrieved without searching
        the app. If no scenario attachments with the given tag are found, then the search continues at the
        app level. :index-name:`get attachments by tag`

        Parameters
        ----------
        tag : str
            The tag to search for

        Returns
        -------
        attachments : Optional[List[Attachment]]
            A list which will be populated with the details of the attachments that were retrieved.

        See Also
        --------
        AppInterface.attach_status
        AppInterface.list_scen_attach
        AppInterface.list_app_attach
        AppInterface.get_app_attach
        AppInterface.get_scen_attach

        Examples
        --------
        Example of searching for and retrieving all attachments with the tag `tag1`

        >>> attachments = insight.get_attachs_by_tag('mytag1')
        ... if insight.attach_status != AttachStatus.OK:
        ...     print("Error searching for attachments")
        ... else:
        ...     for a in attachments:
        ...         print(a.filename)

        Notes
        -----
        Check the attachment status code using :fct-ref:`insight.attach_status` to determine whether the attachment(s) were successfully retrieved.

        Attempting to access attachments when the model is not being run through Xpress Insight will cause the model to abort with an error.
        """

        pass

    #
    @abstractmethod
    def get_attach_by_tag(self, tag: str) -> Optional[Attachment]:
        """
        Gets Insight attachments by tag

        Searches the scenario and the containing app for an attachment or attachments with the given tag, and
        retrieves them from the Insight server, placing them in the Python working directory where they can be read by
        the model. If any scenario attachments with the given tag are found, these are retrieved without searching
        the app. If no scenario attachments with the given tag are found, then the search continues at the
        app level. :index-name:`get attachments by tag`

        Parameters
        ----------
        tag : str
            The tag to search for

        Returns
        -------
        attachment : Optional[Attachment]
            An attachment object which will be populated with the details of the attachment that was retrieved.

        See Also
        --------
        AppInterface.attach_status
        AppInterface.list_scen_attach
        AppInterface.list_app_attach
        AppInterface.get_app_attach
        AppInterface.get_scen_attach

        Examples
        --------
        Example of searching for and retrieving an attachment with the tag `tag1`

        >>> attachment = insight.get_attach_by_tag('mytag1')
        ... if insight.attach_status != AttachStatus.OK:
        ...     print("Error searching for attachments")
        ... else:
        ...     with open(attachment.filename) as f:
        ...         pass  # process the file

        Notes
        -----
        Check the attachment status code using :fct-ref:`insight.attach_status` to determine whether the attachment(s) were successfully retrieved.

        Attempting to access attachments when the model is not being run through Xpress Insight will cause the model to abort with an error.
        """

        pass

    #
    @abstractmethod
    def get_attach_filenames_by_tag(self, tag: str) -> List[str]:
        """
        Gets Insight attachments by tag

        Searches the scenario and the containing app for an attachment or attachments with the given tag, and
        retrieves them from the Insight server, placing them in the Python working directory where they can be read by
        the model. If any scenario attachments with the given tag are found, these are retrieved without searching
        the app. If no scenario attachments with the given tag are found, then the search continues at the
        app level. :index-name:`get attachments by tag`

        Parameters
        ----------
        tag : str
            The tag to search for

        Returns
        -------
        filenames : List[str]
            A list which will be populated with the filenames of the attachments that were retrieved.

        See Also
        --------
        AppInterface.attach_status
        AppInterface.list_scen_attach
        AppInterface.list_app_attach
        AppInterface.get_app_attach
        AppInterface.get_scen_attach

        Examples
        --------
        Example of searching for and retrieving an attachment with the tag `tag1`

        >>> filenames = insight.get_attach_by_tag('mytag1')
        ... if insight.attach_status != AttachStatus.OK:
        ...     print("Error searching for attachments")
        ... else:
        ...     for f in filenames:
        ...         print(f)

        Notes
        -----
        Check the attachment status code using :fct-ref:`insight.attach_status` to determine whether the attachment(s) were successfully retrieved.

        Attempting to access attachments when the model is not being run through Xpress Insight will cause the model to abort with an error.
        """

        pass

    #
    @abstractmethod
    def get_attach_rules(self) -> AttachmentRules:
        """
        Retrieves the the 'rules' used to validate attachments and attachment meta-data.

        Returns
        -------
        rules : AttachmentRules
            The attachment rules.

        Examples
        --------
        Demonstration of getting the example rules

        >>> rules = insight.get_attach_rules()

        Notes
        -----
        Used to retrieve the rules that are used to validate new attachments - for example, maximum attachment size.

        This will only be necessary if you want to validate new attachments within the model, before they
        trigger Insight attachment errors for violating any of these rules.
        """

        pass

    @abstractmethod
    def get_item_info(self, path: str) -> ItemInfo:
        """
        Get information for a repository item with the supplied path.

        Parameters
        ----------
        path: str
            Path to the repository item.

        Returns
        -------
        item_info: ItemInfo
            Information about the repository item (scenario / folder).

        Examples
        --------
        Example of using `get_item_info` to obtain info for a scenario.

        >>> info = insight.get_item_info('/my_app/my_scenario')

        Example of using `get_item_info` with error handling to obtain info for the current scenario.

        >>> @xi.ExecModeLoad()
        ... def load(self):
        ...     try:
        ...         info = self.insight.get_item_info(".")
        ...         print(info)
        ...     except xi.InterfaceError as ex:
        ...         print(ex)

        Notes
        -----
        Raises :fct-ref:`InterfaceError` on failure.

        See Also
        --------
        ItemInfo
        InterfaceError
        AppInterface.get_item_infos
        AppInterface.add_item_info
        AppInterface.clear_item_infos
        """
        pass

    @abstractmethod
    def get_item_infos(self, folder_path: str) -> List[ItemInfo]:
        """
        Get information for items in the folder with the supplied path.

        Parameters
        ----------
        folder_path: str
            Path to the repository folder.

        Returns
        -------
        item_info: ItemInfo
            Information about the items (folders / scenarios) in the given folder.
            The function does not return information about Virtual Scenario Groups.

        Examples
        --------
        Example of using `get_item_infos` to obtain info for items in a folder.

        >>> info = insight.get_item_infos('/appname/my_folder')

        Example of using `get_item_infos` with error handling to obtain info for
        items in the same folder as the current scenario.

        >>> @xi.ExecModeLoad()
        ... def load(self):
        ...     try:
        ...         infos = self.insight.get_item_infos(".")
        ...         print(infos)
        ...     except xi.InterfaceError as ex:
        ...         print(ex)

        Notes
        -----
        Raises :fct-ref:`InterfaceError` on failure.

        See Also
        --------
        ItemInfo
        InterfaceError
        AppInterface.get_item_info
        AppInterface.add_item_info
        AppInterface.clear_item_infos
        """
        pass

    def add_item_info(self, item_info: ItemInfo) -> None:
        """
        Adds the given ItemInfo object to the repository of item infos that are used in test mode.

        Parameters
        ----------
        item_info: ItemInfo
            The item information object to add. All object attributes must be populated and the
            `path` and `parent_path` must both be absolute paths.

        Examples
        --------
        Demonstration of adding an item info and clearing the item info dictionary.

        >>> import sys
        ... import xpressinsight as xi
        ...
        ... @xi.AppConfig(name="Item Info Test", scen_types=["SIMULATION"])
        ... class InsightApp(xi.AppBase):
        ...     @staticmethod
        ...     def print_info(info: xi.ItemInfo):
        ...         print('  ItemInfo:')
        ...         print('    name:        ', info.name)
        ...         print('    type:        ', info.type)
        ...         print('    path:        ', info.path)
        ...         print('    parent_path: ', info.parent_path)
        ...
        ...     @xi.ExecModeLoad(descr="Loads input data.")
        ...     def load(self):
        ...         print('Current scenario item info:')
        ...         self.print_info(self.insight.get_item_info("."))
        ...         print('Item infos in application root folder:')
        ...         for item in self.insight.get_item_infos(
        ...                 str(xi.RepositoryPath.encode(
        ...                     [self.insight.app_name]))):
        ...             self.print_info(item)
        ...
        ...     @xi.ExecModeRun(descr="Takes input and computes results.")
        ...     def run(self):
        ...         print("Run mode finished.")
        ...
        ... if __name__ == "__main__":
        ...     # When the application is run in test mode, first initialize
        ...     # the test environment, then execute the load and run modes.
        ...     def add_default_app_folder_item(insight: xi.AppInterface):
        ...         insight.add_item_info(xi.ItemInfo(
        ...             id=insight.app_id,
        ...             name='Root',
        ...             type='FOLDER',
        ...             path=str(xi.RepositoryPath.encode(
        ...                  [insight.app_name])),
        ...             parent_path=str(xi.RepositoryPath.encode(
        ...                  [insight.app_name]))))
        ...
        ...     def add_default_scenario_item(insight: xi.AppInterface,
        ...                                   scen_type: str = 'SCENARIO'):
        ...         insight.add_item_info(xi.ItemInfo(
        ...             id=insight.scenario_id,
        ...             name=insight.scenario_name,
        ...             type=scen_type,
        ...             path=insight.scenario_path,
        ...             parent_path=insight.scenario_parent_path))
        ...
        ...     app = InsightApp()
        ...     add_default_app_folder_item(app.insight)
        ...     add_default_scenario_item(app.insight)
        ...     app.call_exec_mode('LOAD')
        ...
        ...     app.insight.clear_item_infos()
        ...     app.insight.app_name = 'app 1'
        ...     app.insight.scenario_name = 'my_simulation 2021/09'
        ...     app.insight.scenario_path = str(xi.RepositoryPath.encode(
        ...         [app.insight.app_name, 'my_folder',
        ...          app.insight.scenario_name]))
        ...
        ...     add_default_app_folder_item(app.insight)
        ...     app.insight.add_item_info(xi.ItemInfo(
        ...         id='00000000-0000-0000-0000-000000000001',
        ...         name='my_folder',
        ...         type='FOLDER',
        ...         path=str(xi.RepositoryPath.encode(
        ...             [app.insight.app_name, 'my_folder'])),
        ...         parent_path=str(xi.RepositoryPath.encode(
        ...             [app.insight.app_name]))))
        ...     add_default_scenario_item(app.insight, 'SIMULATION')
        ...     app.call_exec_mode('LOAD')

        Notes
        -----
        Used to mock the Insight repository item info when testing code in test mode.

        The model will abort with a runtime error if an item info with the given name or path already exists.

        Calling this procedure when :fct-ref:`AppInterface.test_mode` is <tt>False</tt> will
        cause the model to abort with a runtime error.

        See Also
        --------
        ItemInfo
        AppInterface.test_mode
        AppInterface.get_item_info
        AppInterface.get_item_infos
        AppInterface.clear_item_infos
        """
        pass

    def clear_item_infos(self) -> None:
        """
        Removes any ItemInfo objects previously added in test mode.

        Examples
        --------
        See :fct-ref:`AppInterface.add_item_info`.

        Notes
        -----
        Used to reset the list of mock ItemInfo objects that were added by :fct-ref:`AppInterface.add_item_info`.

        Calling this method when :fct-ref:`AppInterface.test_mode` is <tt>False</tt>
        will cause the model to abort with a runtime error.

        See Also
        --------
        ItemInfo
        AppInterface.get_item_info
        AppInterface.get_item_infos
        AppInterface.add_item_info
        """
        pass

    #

    #

    @property
    @abstractmethod
    def scenario_id(self) -> str:
        """
        Property for the id of the Xpress Insight scenario.

        Returns
        -------
        scenario_id : str
            The UID of the Xpress Insight scenario.

        Examples
        --------
        Demonstration of setting the scenario id (test mode only).

        >>> insight.scenario_id = 'xyzzy'

        Demonstration of getting the scenario id.

        >>> print('scenario id = ', insight.scenario_id)
        scenario id = xyzzy

        Notes
        -----
        The `scenario_id` property can only be set in test mode.

        In test mode can be used to mock the Insight scenario id.

        Modifying this property when `insight.test_mode` is `False` will cause the model to abort with a runtime error.
        """

        pass

    @scenario_id.setter
    @abstractmethod
    def scenario_id(self, scenario_id: str):
        pass

    @property
    @abstractmethod
    def scenario_name(self) -> str:
        """
        Property for the name of the Xpress Insight scenario.


        Returns
        -------
        scenario_name : str
            The name of the Xpress Insight scenario.

        Examples
        --------
        Demonstration of setting the scenario name (test mode only).

        >>> insight.scenario_name = 'Scenario B'

        Demonstration of getting the scenario name.

        >>> print('scenario name = ', insight.scenario_name)
        scenario name = Scenario B

        Notes
        -----
        The `scenario_name` property can only be set in test mode.

        In test mode can be used to mock the Insight scenario name.

        Modifying this property when `insight.test_mode` is `False` will cause the model to abort with a runtime error.
        """

        pass

    @scenario_name.setter
    @abstractmethod
    def scenario_name(self, scenario_name: str):
        pass

    @property
    @abstractmethod
    def scenario_path(self) -> str:
        """
        Property for the path of the Xpress Insight scenario.

        Returns
        -------
        scenario_path : str
            The path of the Xpress Insight scenario.

        Examples
        --------
        Demonstration of setting the scenario path (test mode only).

        >>> insight.scenario_path = '/myapp/DirA/myscenario'

        Demonstration of getting the scenario path.

        >>> print('scenario path = ', insight.scenario_path)
        scenario path = /myapp/DirA/myscenario

        Notes
        -----
        A scenario path is the full path to a scenario name starting from the repository root and including
        the app name. E.g. `/myapp/DirA/myscenario`.

        The `scenario_path` property can only be set in test mode.

        In test mode can be used to mock the Insight scenario path.

        Modifying this property when `insight.test_mode` is `False` will cause the model to abort with a runtime error.

        See Also
        --------
        AppInterface.scenario_parent_path
        """
        pass

    @scenario_path.setter
    @abstractmethod
    def scenario_path(self, scenario_path: str):
        pass

    @property
    def scenario_parent_path(self) -> str:
        """
        Property for getting the parent path of the Xpress Insight scenario.

        Returns
        -------
        scenario_parent_path : str
            The parent path of the Xpress Insight scenario.

        Examples
        --------
        Demonstration of getting the scenario parent path.

        >>> print('scenario parent path = ', insight.scenario_parent_path)
        scenario parent path = /myapp/DirA/

        Notes
        -----
        A scenario parent path is the full path to the parent folder of the scenario starting from the repository
        root and including the app name. E.g. `/myapp/DirA`.

        The `scenario_parent_path` property can only be read.
        The parent path is computed with the help of `scenario_path`.

        See Also
        --------
        AppInterface.scenario_path
        """
        scen_path = RepositoryPath(self.scenario_path)
        scen_path.pop()
        return str(scen_path) + '/'

    @abstractmethod
    def update(self, metric: Metric, value: Union[float, int, ObjSense]) -> None:
        """
        Sends a progress update notification for a single metric from the model to the Xpress Insight system.

        Parameters
        ----------
        metric : Metric
            The type of metric to update.
        value : Union[float, int, ObjSense]
            The value of the metric to update.

        See Also
        --------
        AppInterface.reset_progress
        Metric
        ObjSense

        Examples
        --------
        Notify Insight that the current best solution value is 51.9.

        >>> insight.update(Metric.OBJVAL, 51.9)

        Automatic updating of metrics during optimization can be achieved by calling the update function
        from within a suitable solver callback:

        >>> def on_gap_notify(prob, app):
        ...
        ...     num_sol = prob.attributes.mipsols
        ...     app.insight.update(xi.Metric.NUMSOLS, num_sol)
        ...
        ...     if num_sol == 0:
        ...         # Can only occur when mipabsgapnotifybound is used.
        ...         # Don't call gapnotify again.
        ...         return None, None, None, None
        ...
        ...     objective = prob.attributes.mipobjval
        ...     best_bound = prob.attributes.bestbound
        ...
        ...     if best_bound != 0 or objective != 0:
        ...         gap = abs(objective - best_bound) / \\
        ...               max(abs(best_bound), abs(objective))
        ...     else:
        ...         gap = 0
        ...
        ...     app.insight.update(xi.Metric.OBJVAL, objective)
        ...     app.insight.update(xi.Metric.GAP, gap)
        ...
        ...     if gap > 1e-6:
        ...         new_rel_gap_notify_target = gap - 1e-6
        ...     else:
        ...         # Don't call gapnotify again.
        ...         new_rel_gap_notify_target = -1
        ...
        ...     return new_rel_gap_notify_target, None, None, None

        The above callback can then be attached via the Xpress Python API:

        >>> prob = xp.problem()
        ...
        ... # TODO: Define the optimization problem
        ...
        ... # Optionally reset progress and set the objective sense
        ... self.insight.reset_progress()
        ... self.insight.update(xi.Metric.OBJSENSE, prob.attributes.objsense)
        ...
        ... prob.controls.miprelgapnotify = 1e20
        ... prob.addcbgapnotify(on_gap_notify, self, 0)
        ...
        ... prob.solve()

        Notes
        -----
        This function allows the model to report back progress to the system where it is accessible by a client for
        display.
        """

        pass

    @abstractmethod
    def reset_progress(self) -> None:
        """
        Resets the progress state for each progress metric back to zero.

        See Also
        --------
        AppInterface.update

        Examples
        --------
        Reset the progress state for each progress metric back to zero.

        >>> insight.reset_progress()

        Notes
        -----
        The :fct-ref:`insight.update` function can be used to report a number of optimization metrics to the
        Xpress Insight system. This method sends notifications to reset the value for each metric to zero.
        """

        pass
