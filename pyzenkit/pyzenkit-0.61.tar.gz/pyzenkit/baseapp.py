#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#-------------------------------------------------------------------------------
# This file is part of PyZenKit package.
#
# Copyright (C) since 2016 CESNET, z.s.p.o (http://www.ces.net/)
# Copyright (C) since 2015 Honza Mach <honza.mach.ml@gmail.com>
# Use of this package is governed by the MIT license, see LICENSE file.
#
# This project was initially written for personal use of the original author. Later
# it was developed much further and used for project of author`s employer.
#-------------------------------------------------------------------------------


"""
This module provides base implementation of generic console application represented
by the :py:class:`pyzenkit.baseapp.BaseApp` class with many usefull features including
(but not limited to) the following:

Application configuration service
    The base application provides tools for loading configurations from multiple
    sources and merging them all into single dictionary. This is then available
    to developers as public class attribute ``config``.

    Currently the following configuration sources are available:

    * Optional configuration via configuration directory. All JSON files in given
      directory are loaded and then merged together.
    * Optional configuration via single JSON configuration file.
    * Optional configuration via command line arguments and options.

Command line argument parsing service
    The base application preconfigures an instance of standard :py:class:`argparse.ArgumentParser`
    class for parsing command line arguments and prepopulates in with a set of built-in
    options and arguments. This instance can be then further modified and enhanced
    in subclass by the user.

Logging service
    The base application is capable of automated setup of :py:class:`logging.Logger`
    logging service. Logger parameters like threshold level, or target file name
    are fully configurable. Currently following destinations are supported:

    * Optional logging to console.
    * Optional logging to text file.

Persistent state service
    The base application contains optional persistent state feature, which is intended
    for storing or passing data between multiple executions of the same application.
    The feature is implemented as a simple dictionary, that is populated from simple
    JSON file on startup and written back on teardown.

Application runlog service
    The base application provides optional runlog service, which is a intended to
    provide storage for relevant data and results during the processing and enable
    further analysis later. The feature is implemented as simple dictionary, that
    is written into JSON file on teardown.

Plugin system
    The base application provides tools for writing and using plugins, that can be used
    to further enhance the functionality of application and improve code reusability
    by composing the application from smaller building blocks.

Application actions
    The base application provides tools for quick **actions**. These **actions** are
    intended to be used for global application management tasks such as vieving or
    validating configuration without executing the application itself, listing or
    evaluating runlogs and so on. There is a number of built-in actions and more
    can be implemented very easily.

The application is designed to provide all of these usefull features by default and
with as less as possible work, while also maintaining high customizability. This goal
is achived by following measures:

* Most of the hardcoded features are somehow customizable by configuration file
  keys or command line options.
* There are many callback hooks prepared for subclasses, that can be used to add
  the desired functionality.
* If you are more familiar with the code, you may override the default implementation
  of almost any method and provide your own functionality, or call the parent implementation
  at some point in the new method.

Please browse the source code, there is an example implementation in
:py:class:`pyzenkit.baseapp.DemoBaseApp` class.


Application usage modes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Applications created using this framework can be utilized in two work modes:

* **run**
* **plugin**

In the **run** mode all application features are initialized and configured and
desired action or application processing code is immediatelly executed.

In the **plugin** mode the application is only initialized and configured and any
other interactions must be performed manually by calling appropriate methods. This
approach enables users to plug one apllication into another one on a wider scope.
One example use case of this feature may be the implementation of an user command
line interface that controls multiple applications (for example like *git* executable
controls almost everything in Git universe).


Application actions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Applications created based on this framework come with built-in support for **actions**.
The **action** is a designation for some kind of support task, that does not relate
to actual purpose of the application. The **actions** however are executed within the same
environment and have access to the whole application, so they are perfect for simple
tasks like configuration validation. The **actions** are also much more simple and
when executing an action the application does not go through all life-cycle stages
(see below).

Currently following **actions** are built-in and supported:

**config-view**
    Display current configuration tree.

**runlog-dump**
    Simple dump of chosen application runlog.

**runlog-view**
    View chosen application runlog (nicer display with calculated statistics).

**runlogs-dump**
    Simple dump of all application runlogs.

**runlogs-list**
    View list of all application runlogs.

**runlogs-evaluate**
    View evaluated statistics of all application runlogs.

Actions may be executed by selecting desired action by command line argument::

    path/to/baseapp.py --action config-view
    path/to/baseapp.py --action=config-view

Action may be selected permanently inside configuration file under the dictionary
key ``action``.


Application life-cycle
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Depending on the mode of operation (**run** or **plugin**) the application code goes
through a different set of stages during its life span. See subsections below for
more details on each life-cycle stage. The life-cycle is implemented partly in the
:py:func:`pyzenkit.baseapp.BaseApp.__init__` method and mostly in
:py:func:`pyzenkit.baseapp.BaseApp.run` method.

In the **plugin** mode the following stages are performed:

* **__init__**
* **setup**

In the **run** mode the following stages are performed in case some **action** is
being handled:

* **__init__**
* **setup**
* **action**

In the **run** mode the following stages are performed in case of normal processing:

* **__init__**
* **setup**
* **process**
* **evaluate**
* **teardown**


Stage __init__
````````````````````````````````````````````````````````````````````````````````

The **__init__** stage is responsible for creating and basic default initialization of
application object. No exception should occur or be raised during the initialization
stage and the code should always work regardles of environment setup, so no files
should be opened, etc. Any exception during this stage will intentionally not get
handled in any way and will result in full traceback dump and immediate application
termination.

All more advanced setup tasks should be performed during the **setup** stage, which is
capable of intelligent catching and displaying/logging of any exceptions.

This stage is implemented in the :py:func:`BaseApp.__init__` method and there are
following substages in this stage:

* init command line argument parser: :py:func:`BaseApp._init_argparser`
* parse command line arguments: :py:func:`BaseApp._parse_cli_arguments`
* initialize application name: :py:func:`BaseApp._init_name`
* initialize filesystem paths: :py:func:`BaseApp._init_paths`
* initialize application runlog: :py:func:`BaseApp._init_runlog`
* initialize default configurations: :py:func:`BaseApp._init_config`
* subclass hook for additional initializations: :py:func:`BaseApp._sub_stage_init`

Any of the previous substages may be overriden in a subclass to enhance or alter
the functionality, but always be sure of what you are doing.


Stage *setup*
````````````````````````````````````````````````````````````````````````````````

The **setup** stage is responsible for bootstrapping and configuring of the whole
application. Any exception, that is the instance of :py:class:`ZenAppSetupException`
will be catched, only simple message will be displayed to the user and application
will terminate. This use case represents the case when the error is on the user`s side,
for example non-existent configuration file, etc. In any other case the application will
terminate with full traceback print.

This stage is implemented in the :py:func:`BaseApp._stage_setup` method and there
are following substages in this stage:

* setup configuration: :py:func:`BaseApp._stage_setup_configuration`
* setup user and group privileges: :py:func:`BaseApp._stage_setup_privileges`
* setup logging: :py:func:`BaseApp._stage_setup_logging`
* setup persistent state: :py:func:`BaseApp._stage_setup_pstate`
* setup plugins: :py:func:`BaseApp._stage_setup_plugins`
* subclass hook for additional setup: :py:func:`BaseApp._sub_stage_setup`
* setup dump: :py:func:`BaseApp._stage_setup_dump`

Any of the previous substages may be overriden in a subclass to enhance or alter
the functionality, but always be sure of what you are doing.


Stage *action*
````````````````````````````````````````````````````````````````````````````````

The **action** stage takes care of executing built-in actions. See appropriate
section above for list of all available built-in actions.

More actions can be implemented very easily. The action callback methods just
have to follow these requirements to be autodetected by the application engine:

* Action callback must be method without any mandatory arguments.
* Action callback method name must begin with ``cbk_action_`` prefix.
* Action name in the method name after the prefix must also be `snake_cased``.
* Action name will be calculated by replacing ``_`` with ``-``.

Following are examples of valid action callbacks::

    cbk_action_test(self):         # Will be mapped to 'test' action.
    cbk_action_another_test(self): # Will be mapped to 'another-test' action.

When a method is implemented according to these guidelines, it will be automatically
recognized and executable.

This stage is implemented in the :py:func:`BaseApp._stage_action` method.

Please see the implementation of existing built-in actions for examples.


Stage *process*
````````````````````````````````````````````````````````````````````````````````

The **process** stage is supposed to perform the required task(s). This stage is
implemented in the :py:func:`BaseApp._stage_process` method. It is a wrapper
method, that takes care of exception catching and the application must provide
its own implementation of template method :py:func:`BaseApp._sub_stage_process`,
which is being called from the wrapper and should contain actual processing code.


Stage *evaluate*
````````````````````````````````````````````````````````````````````````````````

The **evaluate** stage is supposed to perform any required evaluations of current
runlog. Currently, there are no built-in evaluations.


Stage *teardown*
````````````````````````````````````````````````````````````````````````````````

The **teardown** stage is supposed to perform any cleanup tasks before the application
exits.

This stage is implemented in the :py:func:`BaseApp._stage_teardown` method and there
are following substages in this stage:

* subclass hook for additional teardown actions: :py:func:`BaseApp._sub_stage_teardown`
* save persistent state: :py:func:`BaseApp._stage_teardown_pstate`
* save runlog: :py:func:`BaseApp._stage_teardown_runlog`


Module contents
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* :py:class:`ZenAppException`
    * :py:class:`ZenAppSetupException`
    * :py:class:`ZenAppProcessException`
    * :py:class:`ZenAppEvaluateException`
    * :py:class:`ZenAppTeardownException`
* :py:class:`ZenAppPlugin`
* :py:class:`BaseApp`
* :py:class:`DemoBaseApp`


Programming API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The application features mentioned in this document are available to the user/developer
either as public attributes of the :py:class:`pyzenkit.baseapp.BaseApp` class,
or as public methods:

* public attributes:

    * :py:attr:`BaseApp.name` - Name of the application.
    * :py:attr:`BaseApp.paths` - Paths to various locations, like config or temp directories.
    * :py:attr:`BaseApp.runlog` - Writable dictionary containing the application runlog.
    * :py:attr:`BaseApp.config` - Dictionary containing final merged application configuration.
    * :py:attr:`BaseApp.logger` - Configured instance of :py:mod:`logging.Logger` logger.
    * :py:attr:`BaseApp.pstate` - Writable dictionary containing the application persistent state.
    * :py:attr:`BaseApp.retc` - Exit status code as integer.

* public methods:

    * :py:func:`BaseApp.c` - Shortcut method for accessing the `self.config.get(key, default)`
    * :py:func:`BaseApp.cc` - Shortcut method for accessing the `self.config[self.CORE].get(key, default)`
    * :py:func:`BaseApp.p` - Method for printing to terminal honoring the ``verbose`` setting.
    * :py:func:`BaseApp.dbgout` - Method for printing additional debug messages honoring the ``debug`` setting.
    * :py:func:`BaseApp.excout` - Method for printing exception without traceback and terminating the application.
    * :py:func:`BaseApp.error` - Register given error into application.
    * :py:func:`BaseApp.json_dump` - Utility method for dumping data structure into JSON string.
    * :py:func:`BaseApp.json_load` - Utility method for loading JSON file.
    * :py:func:`BaseApp.json_save` - Utility method for writing data structure into JSON file.


Subclass extension hooks
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The base application provides following extension hooks, that can be used in subclasses
to enhance the base functionality. There is one hook for each application life-cycle
stage:

* :py:func:`BaseApp._sub_stage_init`
* :py:func:`BaseApp._sub_stage_setup`
* :py:func:`BaseApp._sub_stage_process`
* :py:func:`BaseApp._sub_stage_teardown`

There are also couple of methods for runlog analysis and evaluation, that can be
used to enhance the default output of ``runlog-*`` built-in actions:

* :py:func:`BaseApp._sub_runlog_analyze`
* :py:func:`BaseApp._sub_runlog_format_analysis`
* :py:func:`BaseApp._sub_runlogs_evaluate`
* :py:func:`BaseApp._sub_runlogs_format_evaluation`
"""

__author__  = "Honza Mach <honza.mach.ml@gmail.com>"


import os
import sys
import pwd
import grp
import re
import glob
import time
import argparse
import logging
import logging.handlers
import pprint
import subprocess
import datetime
import traceback

#
# Custom libraries.
#
import pydgets.widgets
import pyzenkit.utils
import pyzenkit.jsonconf


# Attempt to load local '.env.local' and '.env' files.
pyzenkit.utils.load_dotenv_cwd()


#-------------------------------------------------------------------------------


class ZenAppException(Exception):
    """
    Base class for all ZenApp custom exceptions.

    When appropriate, these exceptions will be catched, error will be displayed
    to the user and the application will attempt to gracefully terminate without
    dumping the traceback visibly to the user. These exceptions should be used
    for anticipated errors, which can occur during normal application execution and
    do not mean there is anything wrong with the code itself, for example missing
    configuration file, etc...
    """
    def __init__(self, description, **params):
        """
        Initialize new exception with given description and optional additional
        parameters.

        :param str description: Description of the problem.
        :param params: Optional additional parameters.
        """
        super().__init__()

        self.description = description
        self.params = params

    def __str__(self):
        """
        Operator override for automatic string output.
        """
        return repr(self.description)

class ZenAppSetupException(ZenAppException):
    """
    Describes problems or errors that occur during the **setup** phase.
    """

class ZenAppProcessException(ZenAppException):
    """
    Describes problems or errors that occur during the **process** phase.
    """

class ZenAppEvaluateException(ZenAppException):
    """
    Describes problems or errors that occur during the **evaluate** phase.
    """

class ZenAppTeardownException(ZenAppException):
    """
    Describes problems or errors that occur during the **teardown** phase.
    """


#-------------------------------------------------------------------------------


class ZenAppPlugin:
    """
    Base class for all ZenApp application plugins. Plugins can be used to further
    enhance the code reusability by composing the application from smaller building
    blocks.
    """

    def __str__(self):
        """
        Operator override for automatic string output.
        """
        return self.__class__.__name__

    def init_argparser(self, app, argparser, **kwargs):  # pylint: disable=locally-disabled,no-self-use,unused-argument
        """
        Callback to be called during argparser initialization phase.
        """
        return argparser

    def init_config(self, app, config, **kwargs):  # pylint: disable=locally-disabled,no-self-use,unused-argument
        """
        Callback to be called during default configuration initialization phase.
        """
        return config

    def init_runlog(self, app, runlog, **kwargs):  # pylint: disable=locally-disabled,no-self-use,unused-argument
        """
        Callback to be called during runlog initialization phase.
        """
        return runlog

    def configure(self, app):
        """
        Callback to be called during configuration phase (after initialization).
        """
        raise NotImplementedError('This method must be implemented in subclass')

    def setup(self, app):
        """
        Callback to be called during setup phase (after setup).
        """
        raise NotImplementedError('This method must be implemented in subclass')


#-------------------------------------------------------------------------------


class BaseApp:  # pylint: disable=locally-disabled,too-many-public-methods, too-many-instance-attributes
    """
    Base implementation of generic executable application. This class attempts to
    provide robust and stable framework, which can be used to writing all kinds
    of scripts or daemons. Although is is usable, this is however a low level framework
    and should not be used directly, use the :py:mod:`pyzenkit.zenscript` or
    :py:mod:`pyzenkit.zendaemon` modules for writing custom scripts or daemons
    respectively. That being said, the :py:class:`pyzenkit.baseapp.DemoBaseApp`
    class is an example implementation of using this class directly without any
    additional overhead.
    """

    #
    # Class constants.
    #

    # Global flag, that turns on additional debugging messages.
    FLAG_DEBUG = False

    # List of all possible return codes.
    RC_SUCCESS = os.EX_OK
    RC_FAILURE = 1

    # List of possible result codes.
    RESULT_SUCCESS = 'success'
    RESULT_FAILURE = 'failure'

    # String patterns.
    PTRN_ACTION_CBK  = 'cbk_action_'
    PTRN_APP_NAME    = '^[_a-zA-Z][-_a-zA-Z0-9.]*$'

    # Paths.
    PATH_BIN = 'bin'
    PATH_CFG = 'cfg'
    PATH_LOG = 'log'
    PATH_VAR = 'var'
    PATH_RUN = 'run'
    PATH_TMP = 'tmp'

    # List of core configuration keys.
    CORE                = '__core__'
    CORE_LOGGING        = 'logging'
    CORE_LOGGING_TOFILE = 'to_file'
    CORE_LOGGING_TOCONS = 'to_console'
    CORE_LOGGING_LEVEL  = 'level'
    CORE_LOGGING_LEVELF = 'level_file'
    CORE_LOGGING_LEVELC = 'level_console'
    CORE_PSTATE         = 'pstate'
    CORE_PSTATE_SAVE    = 'save'
    CORE_RUNLOG         = 'runlog'
    CORE_RUNLOG_SAVE    = 'save'

    # List of configuration keys.
    CONFIG_PLUGINS     = 'plugins'
    CONFIG_DEBUG       = 'debug'
    CONFIG_QUIET       = 'quiet'
    CONFIG_VERBOSITY   = 'verbosity'
    CONFIG_RUNLOG_DUMP = 'runlog_dump'
    CONFIG_PSTATE_DUMP = 'pstate_dump'
    CONFIG_RUNLOG_LOG  = 'runlog_log'
    CONFIG_PSTATE_LOG  = 'pstate_log'
    CONFIG_NAME        = 'name'
    CONFIG_ACTION      = 'action'
    CONFIG_INPUT       = 'input'
    CONFIG_LIMIT       = 'limit'
    CONFIG_USER        = 'user'
    CONFIG_GROUP       = 'group'
    CONFIG_CFG_FILE    = 'config_file'
    CONFIG_CFG_DIR     = 'config_dir'
    CONFIG_CFG_FILE_S  = 'config_file_silent'
    CONFIG_CFG_DIR_S   = 'config_dir_silent'
    CONFIG_LOG_FILE    = 'log_file'
    CONFIG_LOG_LEVEL   = 'log_level'
    CONFIG_PID_FILE    = 'pid_file'
    CONFIG_PSTATE_FILE = 'pstate_file'
    CONFIG_RUNLOG_DIR  = 'runlog_dir'

    # List of runlog keys.
    RLKEY_NAME    = 'name'          # Application name.
    RLKEY_PID     = 'pid'           # Application process PID.
    RLKEY_ARGV    = 'argv'          # Application command line arguments.
    RLKEY_TS      = 'ts'            # Timestamp as float.
    RLKEY_TSFSF   = 'ts_fsf'        # Timestamp as sortable string (usefull for generating sortable file names).
    RLKEY_TSSTR   = 'ts_str'        # Timestamp as readable string.
    RLKEY_RESULT  = 'result'        # Result as a string.
    RLKEY_RC      = 'rc'            # Result as numeric return code.
    RLKEY_ERRORS  = 'errors'        # List of arrors during execution.
    RLKEY_TMARKS  = 'time_marks'    # Time measuring marks.

    # List of runlog analysis keys.
    RLANKEY_LABEL       = 'label'
    RLANKEY_COMMAND     = 'command'
    RLANKEY_AGE         = 'age'
    RLANKEY_RESULT      = 'result'
    RLANKEY_RUNLOG      = 'runlog'
    RLANKEY_DURRUN      = 'dur_run'
    RLANKEY_DURPRE      = 'dur_pre'
    RLANKEY_DURPROC     = 'dur_proc'
    RLANKEY_DURPOST     = 'dur_post'
    RLANKEY_DURATIONS   = 'durations'
    RLANKEY_EFFECTIVITY = 'effectivity'

    # List of runlog evaluation keys.
    RLEVKEY_ANALYSES   = 'analyses'
    RLEVKEY_MINDURRUN  = 'min_dur_run'
    RLEVKEY_MAXDURRUN  = 'max_dur_run'
    RLEVKEY_AVGDURRUN  = 'avg_dur_run'
    RLEVKEY_MINDURPROC = 'min_dur_proc'
    RLEVKEY_MAXDURPROC = 'max_dur_proc'
    RLEVKEY_AVGDURPROC = 'avg_dur_proc'
    RLEVKEY_MINEFFECT  = 'min_effectivity'
    RLEVKEY_MAXEFFECT  = 'max_effectivity'
    RLEVKEY_AVGEFFECT  = 'avg_effectivity'


    @classmethod
    def get_resource_path(cls, fs_path, *more_chunks):
        """
        Return filesystem path to application resource with ``APP_ROOT_PATH`` taken
        into consideration. If ``fs_path`` is absolute the ``APP_ROOT_PATH`` will
        be ignored as usual.
        """
        return pyzenkit.utils.get_resource_path(fs_path, *more_chunks)

    @classmethod
    def get_resource_path_fr(cls, fs_path, *more_chunks):
        """
        Force given application filesystem path to be relative to ``APP_ROOT_PATH``.
        """
        return pyzenkit.utils.get_resource_path_fr(fs_path, *more_chunks)


    #---------------------------------------------------------------------------
    # "__INIT__" STAGE METHODS.
    #---------------------------------------------------------------------------


    def __init__(self, **kwargs):
        """
        Base application object constructor. Only defines core internal variables
        and setup default values. The actual object initialization, during which
        command line arguments and configuration files are parsed, is done during
        the **setup** stage of the application life-cycle. Do not do anything expensive
        in this stage, object instantination should be quick, cheap and always
        succeed (when reasonable), use the **setup** stage for that stuff.

        :param dict kwargs: Various additional parameters.
        """
        # Initialize list of desired plugins.
        self._plugins = kwargs.get(self.CONFIG_PLUGINS, [])

        self.paths  = self._init_paths(**kwargs)
        """[PUBLIC] Application paths that will be used to construct various absolute file paths."""

        self.description = kwargs.get('description', 'BaseApp - Generic application')
        """[PUBLIC] Default application help description."""

        self.argparser = self._init_argparser(**kwargs)
        """[PUBLIC] Initialize command line argument parser."""

        # Parse CLI arguments immediatelly, we need to check for a few priority
        # flags and switches, like ``--debug``
        self._config_cli  = self._parse_cli_arguments(self.argparser)
        self._config_file = None
        self._config_dir  = None

        self._process_serial = None

        self.name = self._init_name(**kwargs)
        """[PUBLIC] Name of the application, autodetected, or forced by object constructor arguments."""
        self.runlog = self._init_runlog(**kwargs)
        """[PUBLIC] Application processing runlog."""
        self.config = self._init_config((), **kwargs)
        """[PUBLIC] Application configuration dictionary."""
        self.logger = None
        """[PUBLIC] Preconfigured :py:class:`logging.Logger` object."""
        self.pstate = None
        """[PUBLIC] Persistent state dictionary."""
        self.retc   = self.RC_SUCCESS
        """[PUBLIC] Final return code as integer."""

        # Perform subinitializations on default configurations and argument parser.
        self._sub_stage_init(**kwargs)

    def _init_paths(self, **kwargs):
        """
        Initialize various application filesystem paths like temp directory, log
        directory etc. These values will when be used to autogenerate default paths
        to various files and directories, like log file, persistent state file etc.

        Gets called from main constructor :py:func:`~BaseApp.__init__`.

        :param kwargs: Various additional parameters passed down from constructor.
        :return: Configurations for various filesystem paths.
        :rtype: dict
        """
        result = {}
        for (path, default) in (
                (self.PATH_BIN, 'usr/local/bin'),
                (self.PATH_CFG, 'etc'),
                (self.PATH_VAR, 'var'),
                (self.PATH_LOG, 'var/log'),
                (self.PATH_RUN, 'var/run'),
                (self.PATH_TMP, 'var/tmp')
        ):
            result[path] = self.get_resource_path(
                kwargs.get('path_{}'.format(path), default)
            )
        return result

    def _init_argparser(self, **kwargs):
        """
        Initialize application command line argument parser. This method may be overriden
        in subclasses, however it must return valid :py:class:`argparse.ArgumentParser`
        object.

        Gets called from main constructor :py:func:`~BaseApp.__init__`.

        :param dict kwargs: Various additional parameters passed down from constructor.
        :return: Initialized argument parser object.
        :rtype: argparse.ArgumentParser
        """
        argparser = argparse.ArgumentParser(description = self.description)

        # Option flag indicating that application is running in debug mode. This option
        # will enable displaying of additional helpful debugging messages. The
        # messages will be printed directly to terminal, without the use of
        # logging framework.
        argparser.add_argument('--debug', help = 'run in debug mode (flag)', action = 'store_true', default = None)

        # Setup mutually exclusive group for quiet x verbose mode option.
        group_a = argparser.add_mutually_exclusive_group()

        # Option flag indicating that application is running in quiet mode. This option
        # will prevent application from displaying any information to console.
        group_a.add_argument('--quiet', help = 'run in quiet mode (flag)', action = 'store_true', default = None)

        # Option for setting the output verbosity level.
        group_a.add_argument('--verbose', help = 'increase output verbosity (flag, repeatable)', action = 'count', default = None, dest = 'verbosity')

        #
        # Create and populate options group for common application arguments.
        #
        arggroup_common = argparser.add_argument_group('common application arguments')

        arggroup_common.add_argument('--name',  help = 'name of the application', type = str, default = None)
        arggroup_common.add_argument('--user',  help = 'process UID or user name', default = None)
        arggroup_common.add_argument('--group', help = 'process GID or group name', default = None)

        arggroup_common.add_argument('--config-file-silent', help = 'silently ignore missing configuration file (flag)', action = 'store_true', default = None)
        arggroup_common.add_argument('--config-dir-silent',  help = 'silently ignore missing configuration directory (flag)', action = 'store_true', default = None)

        arggroup_common.add_argument('--config-file', help = 'path to the configuration file', type = str, default = None)
        arggroup_common.add_argument('--config-dir',  help = 'path to the configuration directory', type = str, default = None)
        arggroup_common.add_argument('--log-file',    help = 'path to the log file', type = str, default = None)
        arggroup_common.add_argument('--log-level',   help = 'set logging level', choices = ['debug', 'info', 'warning', 'error', 'critical'], type = str, default = None)

        arggroup_common.add_argument('--action', help = 'name of the quick action to be performed', choices = self._utils_detect_actions(), type = str, default = None)
        arggroup_common.add_argument('--input',  help = 'file to be used as source file in action', type = str, default = None)
        arggroup_common.add_argument('--limit',  help = 'apply given limit to the result', type = int, default = None)

        arggroup_common.add_argument('--pstate-file', help = 'path to the persistent state file', type = str, default = None)
        arggroup_common.add_argument('--pstate-dump', help = 'dump persistent state to stdout when done processing (flag)', action = 'store_true', default = None)
        arggroup_common.add_argument('--pstate-log',  help = 'write persistent state to logging service when done processing (flag)', action = 'store_true', default = None)

        arggroup_common.add_argument('--runlog-dir',  help = 'path to the runlog directory', type = str, default = None)
        arggroup_common.add_argument('--runlog-dump', help = 'dump runlog to stdout when done processing (flag)', action = 'store_true', default = None)
        arggroup_common.add_argument('--runlog-log',  help = 'write runlog to logging service when done processing (flag)', action = 'store_true', default = None)

        #argparser.add_argument('args', help = 'optional additional arguments', nargs='*')

        for plugin in self._plugins:
            argparser = plugin.init_argparser(self, argparser, **kwargs)

        return argparser

    def _parse_cli_arguments(self, argparser):
        """
        Load and initialize application configuration received as command line arguments.
        Use the previously configured :py:class:`argparse.ArgumentParser` object
        for parsing CLI arguments. Immediatelly perform dirty check for ``--debug``
        flag to turn on debug output as soon as possible.

        Gets called from main constructor :py:func:`~BaseApp.__init__`.

        :param argparse.ArgumentParser argparser: Argument parser object to use.
        :return: Parsed command line arguments.
        :rtype: dict
        """
        # Actually process command line arguments.
        cli_cfgs = vars(argparser.parse_args())

        # Immediatelly check for debug flag.
        if cli_cfgs.get(self.CONFIG_DEBUG, False):
            BaseApp.FLAG_DEBUG = True
            self.dbgout("FLAG_DEBUG set to 'True' via command line option")

        self.dbgout("Received command line arguments: '{}'".format(' '.join(sys.argv)))
        return cli_cfgs

    def _init_name(self, **kwargs):
        """
        Initialize application name. The application name will then be used to
        autogenerate default paths to various files and directories, like log
        file, persistent state file etc. The default value for application name
        is automagically detected from command line, or it may be explicitly set
        either using command line option ``--name``, or by using parameter ``name``
        of application object constructor.

        Gets called from main constructor :py:func:`~BaseApp.__init__`.

        :param kwargs: Various additional parameters passed down from constructor.
        :return: Name of the application.
        :rtype: str
        """
        cli_name = self._config_cli.get(self.CONFIG_NAME)
        if cli_name:
            if re.fullmatch(self.PTRN_APP_NAME, cli_name):
                self.dbgout("Using custom application name '{}' received as command line option".format(cli_name))
                return cli_name
            raise ZenAppException("Invalid application name '{}'. Valid pattern is '{}'".format(cli_name, self.PTRN_APP_NAME))

        if self.CONFIG_NAME in kwargs:
            if re.fullmatch(self.PTRN_APP_NAME, kwargs[self.CONFIG_NAME]):
                self.dbgout("Using custom application name '{}' received as constructor option".format(kwargs[self.CONFIG_NAME]))
                return kwargs[self.CONFIG_NAME]
            raise ZenAppException("Invalid application name '{}'. Valid pattern is '{}'".format(cli_name, self.PTRN_APP_NAME))

        app_name = os.path.basename(sys.argv[0])
        self.dbgout("Using default application name '{}".format(app_name))
        return app_name

    def _init_runlog(self, **kwargs):
        """
        Initialize application runlog. Runlog should contain vital information about
        application progress and it will be stored into file upon exit.

        Gets called from main constructor :py:func:`~BaseApp.__init__`.

        :param kwargs: Various additional parameters passed down from constructor.
        :return: Runlog structure.
        :rtype: dict
        """
        runlog = {
            self.RLKEY_NAME:   self.name,
            self.RLKEY_PID:    os.getpid(),
            self.RLKEY_ARGV:   sys.argv,
            self.RLKEY_TS:     time.time(),
            self.RLKEY_RESULT: self.RESULT_SUCCESS,
            self.RLKEY_ERRORS: [],
            self.RLKEY_TMARKS: [],
        }
        # Timestamp as one string (usefull for generating sortable file names).
        runlog[self.RLKEY_TSFSF] = time.strftime('%Y%m%d%H%M',  time.localtime(runlog[self.RLKEY_TS]))
        # Timestamp as readable string.
        runlog[self.RLKEY_TSSTR] = time.strftime('%Y-%m-%d %X', time.localtime(runlog[self.RLKEY_TS]))

        for plugin in self._plugins:
            runlog = plugin.init_runlog(self, runlog, **kwargs)

        return runlog

    def _init_config(self, cfgs, **kwargs):
        """
        Initialize default application configurations. This method may be used
        from subclasses by passing any additional configurations in ``cfgs``
        parameter. Configurations should be passed as list of two item tupples::

            (('key1', 'value'), ('key2', 42)

        Note, that these are only defaults for given configuration key and may
        get overwritten by merging values from configuration file, or command
        line arguments.

        Gets called from main constructor :py:func:`~BaseApp.__init__`.

        :param list cfgs: Additional set of configurations.
        :param kwargs: Various additional parameters passed down from constructor.
        :return: Default configuration structure.
        :rtype: dict
        """
        cfgs = (
            (self.CONFIG_DEBUG,       False),
            (self.CONFIG_QUIET,       False),
            (self.CONFIG_VERBOSITY,   0),
            (self.CONFIG_RUNLOG_DUMP, False),
            (self.CONFIG_PSTATE_DUMP, False),
            (self.CONFIG_RUNLOG_LOG,  False),
            (self.CONFIG_PSTATE_LOG,  False),
            (self.CONFIG_ACTION,      None),
            (self.CONFIG_INPUT,       None),
            (self.CONFIG_LIMIT,       None),
            (self.CONFIG_USER,        None),
            (self.CONFIG_GROUP,       None),
            (self.CONFIG_CFG_FILE,    os.path.join(self.paths[self.PATH_CFG], "{}.conf".format(self.name))),
            (self.CONFIG_CFG_DIR,     os.path.join(self.paths[self.PATH_CFG], "{}".format(self.name))),
            (self.CONFIG_CFG_FILE_S,  False),
            (self.CONFIG_CFG_DIR_S,   False),
            (self.CONFIG_LOG_FILE,    os.path.join(self.paths[self.PATH_LOG], "{}.log".format(self.name))),
            (self.CONFIG_LOG_LEVEL,   'info'),
            (self.CONFIG_PID_FILE,    os.path.join(self.paths[self.PATH_RUN], "{}.pid".format(self.name))),
            (self.CONFIG_PSTATE_FILE, os.path.join(self.paths[self.PATH_RUN], "{}.pstate".format(self.name))),
            (self.CONFIG_RUNLOG_DIR,  os.path.join(self.paths[self.PATH_RUN], "{}".format(self.name))),
        ) + cfgs
        config = {}
        for cfg in cfgs:
            config[cfg[0]] = kwargs.get('default_{}'.format(cfg[0]), cfg[1])

        for plugin in self._plugins:
            config = plugin.init_config(self, config, **kwargs)

        return config


    #---------------------------------------------------------------------------
    # TEMPLATE METHOD HOOKS (INTENDED TO BE USED BY SUBCLASSESS).
    #---------------------------------------------------------------------------


    def _sub_stage_init(self, **kwargs):
        """
        **SUBCLASS HOOK**: Perform additional custom initialization actions in **__init__** stage.

        Gets called from :py:func:`~BaseApp.__init__`.

        :param kwargs: Various additional parameters passed down from constructor.
        """

    def _sub_stage_setup(self):
        """
        **SUBCLASS HOOK**: Perform additional custom setup actions in **setup** stage.

        Gets called from :py:func:`~BaseApp._stage_setup` and it is a **SETUP SUBSTAGE 06**.
        """

    def _sub_stage_process(self):
        """
        **SUBCLASS HOOK**: Perform some actual processing in **process** stage.
        This is a mandatory method, that must be implemented in subclass, the
        default iplementation in this class raises ``NotImplementedError``.

        Gets called from :py:func:`~BaseApp._stage_process`.
        """
        raise NotImplementedError("Method must be implemented in subclass")

    def _sub_stage_evaluate(self, analysis):
        """
        **SUBCLASS HOOK**: Perform additional evaluation actions in **evaluate** stage.

        Gets called from :py:func:`~BaseApp._stage_evaluate` and it is a **EVALUATE SUBSTAGE 01**.
        """
        self.logger.info(
            "Application runtime: '%s' (effectivity %6.2f %%)",
            datetime.timedelta(seconds = analysis[self.RLANKEY_DURRUN]),
            analysis[self.RLANKEY_EFFECTIVITY]
        )

    def _sub_stage_teardown(self):
        """
        **SUBCLASS HOOK**: Perform additional teardown actions in **teardown** stage.

        Gets called from :py:func:`~BaseApp._stage_teardown` and it is a **TEARDOWN SUBSTAGE 01**.
        """

    def _sub_runlog_analyze(self, runlog, analysis):  # pylint: disable=locally-disabled,no-self-use,unused-argument
        """
        **SUBCLASS HOOK**: Analyze given runlog.
        """
        return analysis

    def _sub_runlog_format_analysis(self, analysis):  # pylint: disable=locally-disabled,no-self-use,unused-argument
        """
        **SUBCLASS HOOK**: Format given runlog analysis.
        """

    def _sub_runlogs_evaluate(self, runlogs, evaluation):  # pylint: disable=locally-disabled,no-self-use,unused-argument
        """
        **SUBCLASS HOOK**: Evaluate given runlog analyses.
        """
        return evaluation

    def _sub_runlogs_format_evaluation(self, evaluation):  # pylint: disable=locally-disabled,no-self-use,unused-argument
        """
        **SUBCLASS HOOK**: Format given runlogs evaluation.
        """


    #---------------------------------------------------------------------------
    # "SETUP:CONFIGURATION" SUBSTAGE METHODS.
    #---------------------------------------------------------------------------


    def _configure_from_cli(self):
        """
        Process application configurations received from command line. It would be
        much cleaner to do the parsing in this method. However the arguments had
        to be already parsed and loaded, because we needed to hack the process to
        check for ``--debug`` option to turn the debug flag on and enable output
        of debug messages. So only task this method has is to perform some additional
        processing. The presence of ``--config-file`` or ``--config-dir`` options
        will cause the appropriate default values to be overwritten. This way an
        alternative configuration file or directory will be loaded in next step.

        Gets called from :py:func:`~BaseApp._stage_setup_configuration` and is
        therefore part of **SETUP** stage.
        """

        # IMPORTANT! Immediatelly apply some configuration values to alter further
        # configuration loading.
        for cfgkey in (self.CONFIG_CFG_FILE, self.CONFIG_CFG_DIR, self.CONFIG_CFG_FILE_S, self.CONFIG_CFG_DIR_S):
            if self._config_cli.get(cfgkey, None) is not None:
                self.dbgout(
                    "Configuration '{}' overridden from '{}' to '{}' by command line option.".format(
                        cfgkey,
                        self.config[cfgkey],
                        self._config_cli[cfgkey]
                    )
                )
                self.config[cfgkey] = self._config_cli[cfgkey]

    def _configure_from_file(self):
        """
        Load and initialize application configurations from single configuration file.
        Name of the configuration file is either autogenerated from application
        name and path to configuration directory, or it might come from command
        line option.

        Gets called from :py:func:`~BaseApp._stage_setup_configuration` and is
        therefore part of **SETUP** stage.
        """
        try:
            self._config_file = pyzenkit.jsonconf.config_load(
                self.c(self.CONFIG_CFG_FILE),
                silent = self.c(self.CONFIG_CFG_FILE_S)
            )
            self.dbgout("Loaded contents of configuration file '{}'".format(self.c(self.CONFIG_CFG_FILE)))

        except FileNotFoundError:
            raise ZenAppSetupException("Configuration file '{}' does not exist".format(self.c(self.CONFIG_CFG_FILE)))

    def _configure_from_dir(self):
        """
        Load and initialize application configurations from multiple files in
        configuration directory. Name of the configuration directory is either
        autogenerated from application name and path to configuration directory,
        or it might come from command line option.

        Gets called from :py:func:`~BaseApp._stage_setup_configuration` and is
        therefore part of **SETUP** stage.
        """
        try:
            self._config_dir = pyzenkit.jsonconf.config_load_dir(
                self.c(self.CONFIG_CFG_DIR),
                silent = self.c(self.CONFIG_CFG_DIR_S)
            )
            self.dbgout("Loaded contents of configuration directory '{}'".format(self.c(self.CONFIG_CFG_DIR)))

        except FileNotFoundError:
            raise ZenAppSetupException("Configuration directory '{}' does not exist".format(self.c(self.CONFIG_CFG_DIR)))

    def _configure_merge(self):
        """
        Configure application and produce final configuration by merging all available
        configuration values in appropriate order ('default' <= 'dir' <= 'file' <= 'cli').

        Gets called from :py:func:`~BaseApp._stage_setup_configuration` and is
        therefore part of **SETUP** stage.
        """
        exceptions = (self.CONFIG_CFG_FILE, self.CONFIG_CFG_DIR)

        # Merge configuration directory values with current config, if possible.
        if self.c(self.CONFIG_CFG_DIR, False):
            self.config.update((key, val) for key, val in self._config_dir.items() if val is not None and key not in exceptions)
            self.dbgout("Merged directory configurations into global configurations")

        # Merge configuration file values with current config, if possible.
        if self.c(self.CONFIG_CFG_FILE, False):
            self.config.update((key, val) for key, val in self._config_file.items() if val is not None and key not in exceptions)
            self.dbgout("Merged file configurations into global configurations")

        # Merge command line values with current config, if possible.
        self.config.update((key, val) for key, val in self._config_cli.items() if val is not None)
        self.dbgout("Merged command line configurations into global configurations")

    def _configure_postprocess(self):
        """
        Perform configuration postprocessing and calculate core configurations.
        Core configurations is an internal mechanism, that separates configurations
        received from untrusted sources from those that are calculated internally. Also,
        there is a set of configuations, that can be only determined programatically
        and usually from multiple base configuration keys. For example there may be
        a configuration representing some desired application state, however the
        correct value may be determined only after evaluating values of multiple
        configurations (e.g. switch for console output, that depends on value of
        ``debug`` and ``verbosity`` configurations).

        Gets called from :py:func:`~BaseApp._stage_setup_configuration` and is
        therefore part of **SETUP** stage.
        """
        # Always mstart with a clean slate.
        self.config[self.CORE] = {}

        # Initial logging configurations.
        ccfg = {}
        ccfg[self.CORE_LOGGING_TOCONS] = True
        ccfg[self.CORE_LOGGING_TOFILE] = True
        ccfg[self.CORE_LOGGING_LEVEL]  = self.c(self.CONFIG_LOG_LEVEL).upper()
        ccfg[self.CORE_LOGGING_LEVELF] = ccfg[self.CORE_LOGGING_LEVEL]
        ccfg[self.CORE_LOGGING_LEVELC] = ccfg[self.CORE_LOGGING_LEVEL]
        self.config[self.CORE][self.CORE_LOGGING] = ccfg

        # Initial persistent configurations.
        ccfg = {}
        ccfg[self.CORE_PSTATE_SAVE] = True
        self.config[self.CORE][self.CORE_PSTATE] = ccfg

        # Initial runlog configurations.
        ccfg = {}
        ccfg[self.CORE_RUNLOG_SAVE] = True
        self.config[self.CORE][self.CORE_RUNLOG] = ccfg

        # Postprocess user account configurations, when necessary.
        if self.config[self.CONFIG_USER]:
            usa = self.config[self.CONFIG_USER]
            res = None
            if not res:
                try:
                    res = pwd.getpwnam(usa)
                    self.config[self.CONFIG_USER] = [res[0], res[2]]
                except:  # pylint: disable=locally-disabled,bare-except
                    pass
            if not res:
                try:
                    res = pwd.getpwuid(int(usa))
                    self.config[self.CONFIG_USER] = [res[0], res[2]]
                except:  # pylint: disable=locally-disabled,bare-except
                    pass
            if not res:
                raise ZenAppSetupException("Requested unknown user account '{}'".format(usa))

            self.dbgout("System user account will be set to '{}':'{}'".format(res[0], res[2]))

        # Postprocess group account configurations, when necessary.
        if self.config[self.CONFIG_GROUP]:
            gra = self.config[self.CONFIG_GROUP]
            res = None
            if not res:
                try:
                    res = grp.getgrnam(gra)
                    self.config[self.CONFIG_GROUP] = [res[0], res[2]]
                except:  # pylint: disable=locally-disabled,bare-except
                    pass
            if not res:
                try:
                    res = grp.getgrgid(int(gra))
                    self.config[self.CONFIG_GROUP] = [res[0], res[2]]
                except:  # pylint: disable=locally-disabled,bare-except
                    pass
            if not res:
                raise ZenAppSetupException("Requested unknown group account '{}'".format(gra))

            self.dbgout("System group account will be set to '{}':'{}'".format(res[0], res[2]))

    def _configure_plugins(self):
        """
        Perform configurations of all application plugins. This method will simply
        call the :py:func:`ZenAppPlugin.configure` of all plugins to let them
        perform their own configuration tasks.

        Gets called from :py:func:`~BaseApp._stage_setup_configuration` and is
        therefore part of **SETUP** stage.
        """
        for plugin in self._plugins:
            self.dbgout("Configuring application plugin '{}'".format(plugin))
            plugin.configure(self)

    def _configure_check(self):
        """
        Perform configuration validation and checking.

        Gets called from :py:func:`~BaseApp._stage_setup_configuration` and is
        therefore part of **SETUP** stage.

        .. todo::

            Missing implementation, work in progress.
        """

    #---------------------------------------------------------------------------
    # "SETUP" STAGE METHODS.
    #---------------------------------------------------------------------------

    def _stage_setup_configuration(self):
        """
        **SETUP SUBSTAGE 01:** Setup application configurations. This method will
        perform following configuration tasks in following order:

        * :py:func:`~BaseApp._configure_from_cli`
        * :py:func:`~BaseApp._configure_from_file` (optional)
        * :py:func:`~BaseApp._configure_from_dir` (optional)
        * :py:func:`~BaseApp._configure_merge`
        * :py:func:`~BaseApp._configure_postprocess`
        * :py:func:`~BaseApp._configure_plugins`
        * :py:func:`~BaseApp._configure_check`

        Gets called from :py:func:`~BaseApp._stage_setup`.
        """
        # Load configurations from command line.
        self._configure_from_cli()

        # Load configurations from config file, if the appropriate feature is enabled.
        if self.c(self.CONFIG_CFG_FILE, False):
            self._configure_from_file()

        # Load configurations from config directory, if the appropriate feature is enabled.
        if self.c(self.CONFIG_CFG_DIR, False):
            self._configure_from_dir()

        # Merge all available configurations together with default.
        self._configure_merge()

        # Postprocess loaded configurations
        self._configure_postprocess()

        # Postprocess loaded configurations
        self._configure_plugins()

        # Check all loaded configurations.
        self._configure_check()

    def _stage_setup_privileges(self):
        """
        **SETUP SUBSTAGE 02:** Setup application privileges (user and group account).

        Target user and group account are retrieved from already processed internal
        configuration dictionary.

        Gets called from :py:func:`~BaseApp._stage_setup`.
        """
        gra = self.c(self.CONFIG_GROUP, None)
        if gra and gra[1] != os.getgid():
            cga = grp.getgrgid(os.getgid())
            self.dbgout("Dropping group privileges from '{}':'{}' to '{}':'{}'".format(cga[0], cga[2], gra[0], gra[1]))
            os.setgid(gra[1])

        usa = self.c(self.CONFIG_USER, None)
        if usa and usa[1] != os.getuid():
            cua = pwd.getpwuid(os.getuid())
            self.dbgout("Dropping user privileges from '{}':'{}' to '{}':'{}'".format(cua[0], cua[2], usa[0], usa[1]))
            os.setuid(usa[1])

    def _stage_setup_logging(self):
        """
        **SETUP SUBSTAGE 03:** Setup console and file logging facilities. All
        logging configuration is retrieved from already processed internal
        configuration dictionary.

        Gets called from :py:func:`~BaseApp._stage_setup`.
        """
        ccl = self.cc(self.CORE_LOGGING, {})
        if ccl[self.CORE_LOGGING_TOCONS] or ccl[self.CORE_LOGGING_TOFILE]:
            # [PUBLIC] Register the logger object as internal attribute.
            self.logger = logging.getLogger('zenapplogger')
            self.logger.setLevel(ccl[self.CORE_LOGGING_LEVEL])

            # Setup console logging.
            if ccl[self.CORE_LOGGING_TOCONS]:
                logging_level = getattr(logging, ccl[self.CORE_LOGGING_LEVELC], None)
                if not isinstance(logging_level, int):
                    raise ValueError("Invalid log severity level '{}'".format(ccl[self.CORE_LOGGING_LEVELC]))

                # Initialize console logging handler.
                fm1 = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
                ch1 = logging.StreamHandler()
                ch1.setLevel(logging_level)
                ch1.setFormatter(fm1)
                self.logger.addHandler(ch1)
                self.dbgout("Logging to console with severity threshold '{}'".format(ccl[self.CORE_LOGGING_LEVELC]))

            # Setup file logging
            if ccl[self.CORE_LOGGING_TOFILE]:
                logging_level = getattr(logging, ccl[self.CORE_LOGGING_LEVELF], None)
                if not isinstance(logging_level, int):
                    raise ValueError("Invalid log severity level '{}'".format(ccl[self.CORE_LOGGING_LEVELF]))

                lfn = self.c(self.CONFIG_LOG_FILE)
                fm2 = logging.Formatter('%(asctime)s {} [%(process)d] %(levelname)s: %(message)s'.format(self.name))
                #ch2 = logging.FileHandler(lfn)
                ch2 = logging.handlers.WatchedFileHandler(lfn)
                ch2.setLevel(logging_level)
                ch2.setFormatter(fm2)
                self.logger.addHandler(ch2)
                self.dbgout("Logging to log file '{}' with severity threshold '{}'".format(lfn, ccl[self.CORE_LOGGING_LEVELF]))

    def _stage_setup_pstate(self):
        """
        **SETUP SUBSTAGE 04:** Setup persistent state from external JSON file.
        Persistent state is just a writable dictionary, that is deserialized on
        application startup from a file and serialized back to the same file on
        application teardown. It can be used to store or pass data between multiple
        application runs.

        Gets called from :py:func:`~BaseApp._stage_setup`.
        """
        if os.path.isfile(self.c(self.CONFIG_PSTATE_FILE)):
            self.dbgout("Loading persistent state from file '{}'".format(self.c(self.CONFIG_PSTATE_FILE)))
            self.pstate = self.json_load(self.c(self.CONFIG_PSTATE_FILE))
        else:
            self.dbgout("Setting default empty persistent state")
            self.pstate =  {}

    def _stage_setup_plugins(self):
        """
        **SETUP SUBSTAGE 05:** Perform setup of all application plugins. This method
        will simply call the :py:func:`ZenAppPlugin.setup` of all plugins to let them
        perform their own setup tasks.

        Gets called from :py:func:`~BaseApp._stage_setup`.
        """
        for plugin in self._plugins:
            self.dbgout("Setting-up application plugin '{}'".format(plugin))
            plugin.setup(self)

    def _stage_setup_dump(self):
        """
        **SETUP SUBSTAGE 07:** Dump application setup information. This method will
        display all vital information about application setup like filesystem paths,
        configurations etc. The ``debug`` command line option or configuration key
        must be set for any output.

        Gets called from :py:func:`~BaseApp._stage_setup`.
        """
        self.logger.debug("Application name is '%s'", self.name)
        self.logger.debug("System paths >>>\n%s", self.json_dump(self.paths))
        if self.c(self.CONFIG_CFG_DIR, False):
            self.logger.debug("Loaded directory configurations >>>\n%s", self.json_dump(self._config_dir))
        if self.c(self.CONFIG_CFG_FILE, False):
            self.logger.debug("Loaded file configurations >>>\n%s", self.json_dump(self._config_file))
        self.logger.debug("Loaded command line configurations >>>\n%s", self.json_dump(self._config_cli))
        self.logger.debug("Final application configurations >>>\n%s", self.json_dump(self.config))
        self.logger.debug("Loaded persistent state >>>\n%s", self.json_dump(self.pstate))
        self.logger.debug("Application plugins >>>\n%s", self.json_dump(self._plugins))


    #---------------------------------------------------------------------------
    # "TEARDOWN" STAGE METHODS.
    #---------------------------------------------------------------------------

    def _prepare_runlog(self, **kwargs):
        """
        Prepare runlog before exporting. This method allows user to append additional
        keys or overwrite existing keys in application runlog.
        """
        # Save additional keys to runlog.
        for key, value in kwargs.items():
            self.runlog[key] = value

        self.runlog[self.RLKEY_RC] = self.retc
        return self.runlog

    def _stage_teardown_pstate(self):
        """
        **TEARDOWN SUBSTAGE 02:** Save application persistent state into JSON file, dump
        it to ``stdout`` or write it to logging service. The output destination is
        determined based on application configuration.

        Gets called from :py:func:`~BaseApp._stage_teardown`.
        """
        if self.cc(self.CORE_PSTATE, {}).get(self.CORE_PSTATE_SAVE):
            self._utils_pstate_save(self.pstate)
        if self.c(self.CONFIG_PSTATE_DUMP):
            self._utils_pstate_dump(self.pstate)
        if self.c(self.CONFIG_PSTATE_LOG):
            self._utils_pstate_log(self.pstate)

    def _stage_teardown_runlog(self):
        """
        **TEARDOWN SUBSTAGE 03:** Save application runlog into JSON file, dump it to
        ``stdout`` or write it to logging service. The output destination is
        determined based on application configuration.

        Gets called from :py:func:`~BaseApp._stage_teardown`.
        """
        if self.cc(self.CORE_RUNLOG, {}).get(self.CORE_RUNLOG_SAVE):
            self._utils_runlog_save(self._prepare_runlog())
        if self.c(self.CONFIG_RUNLOG_DUMP):
            self._utils_runlog_dump(self._prepare_runlog())
        if self.c(self.CONFIG_RUNLOG_LOG):
            self._utils_runlog_log(self._prepare_runlog())


    #---------------------------------------------------------------------------
    # MAIN STAGE METHODS.
    #---------------------------------------------------------------------------


    def _stage_setup(self):
        """
        **STAGE:** *SETUP*.

        Perform full application bootstrap. Any exception during this stage will
        get caught, logged using :py:func:`~BaseApp.excout` method and the application
        will immediatelly terminate.
        """
        self.time_mark('stage_setup_start', 'Start of the setup stage')

        try:
            # Setup configurations.
            self._stage_setup_configuration()

            # Setup application privileges
            self._stage_setup_privileges()

            # Setup logging, if the appropriate feature is enabled.
            if self.c(self.CONFIG_LOG_FILE):
                self._stage_setup_logging()

            # Setup persistent state, if the appropriate feature is enabled.
            if self.c(self.CONFIG_PSTATE_FILE):
                self._stage_setup_pstate()

            # Perform plugin setup actions.
            self._stage_setup_plugins()

            # Perform custom setup actions.
            self._sub_stage_setup()

            # Finally dump information about the application setup.
            self._stage_setup_dump()

        except ZenAppSetupException as exc:
            # At this point the logging facilities may not yet be configured, so
            # we must use other means of diplaying the error to the user. For that
            # reason use custom function to supress the traceback print for known
            # issues and errors.
            self.excout(exc)

        self.time_mark('stage_setup_stop', 'End of the setup stage')

    def _stage_action(self):
        """
        **STAGE:** *ACTION*.

        Perform a quick action. Following method will call appropriate callback
        method to service the requested action. The application will immediatelly
        terminate afterwards.

        Name of the callback method is calculated from the name of the action by
        prepending string ``cbk_action_`` and replacing all ``-`` with ``_``.
        Adding more actions is therefore really simple.
        """
        self.time_mark('stage_action_start', 'Start of the action stage')

        try:
            # Determine, which action to execute.
            self.runlog[self.CONFIG_ACTION] = self.c(self.CONFIG_ACTION)
            actname = self.c(self.CONFIG_ACTION)
            actcbkname = self.PTRN_ACTION_CBK + actname.lower().replace('-','_')

            cbk = getattr(self, actcbkname, None)
            if cbk:
                self.dbgout("Executing callback '{}' for action '{}'".format(actcbkname, actname))
                cbk()
            else:
                raise ZenAppProcessException("Invalid action '{}', callback '{}' does not exist".format(actname, actcbkname))

        except subprocess.CalledProcessError as err:
            self.error("System command error: {}".format(err))

        except ZenAppProcessException as exc:
            self.error("Action exception: {}".format(exc))

        except ZenAppException as exc:
            self.error("Application exception: {}".format(exc))

        self.time_mark('stage_action_stop', 'End of the action stage')

    def _stage_process(self):
        """
        **STAGE:** *PROCESS*.

        Finally perform some real work. This method will call :py:func:`~BaseApp._sub_stage_process`
        hook, which must be implemented in subclass.
        """
        self.time_mark('stage_process_start', 'Start of the processing stage')

        try:
            self._sub_stage_process()

        except subprocess.CalledProcessError as err:
            self.error("System command error: {}".format(err))

        except ZenAppProcessException as exc:
            self.error("Processing exception: {}".format(exc))

        except ZenAppException as exc:
            self.error("Application exception: {}".format(exc))

        self.time_mark('stage_process_stop', 'End of the processing stage')

    def _stage_evaluate(self):
        """
        **STAGE:** *EVALUATE*.

        Perform application runlog postprocessing evaluation.
        """
        self.time_mark('stage_evaluate_start', 'Start of the evaluation stage')

        try:
            # Perform runlog analysis.
            analysis = self.runlog_analyze(self._prepare_runlog())

            # Evaluate the analysis.
            self._sub_stage_evaluate(analysis)

        except ZenAppEvaluateException as exc:
            self.error("Evaluation exception: {}".format(exc))

        except ZenAppException as exc:
            self.error("Application exception: {}".format(exc))

        self.time_mark('stage_evaluate_stop', 'End of the evaluation stage')

    def _stage_teardown(self):
        """
        **STAGE:** *TEARDOWN*

        Main teardown routine. This method will call the sequence of following
        teardown routines:

        * :py:func:`~BaseApp._sub_stage_teardown`
        * :py:func:`~BaseApp._sub_teardown_pstate`
        * :py:func:`~BaseApp._sub_teardown_runlog`
        """
        try:
            # Perform custom teardown actions.
            self._sub_stage_teardown()

            # Teardown persistent state.
            if self.c(self.CONFIG_PSTATE_FILE):
                self._stage_teardown_pstate()

            # Teardown runlog.
            if self.c(self.CONFIG_RUNLOG_DIR):
                self._stage_teardown_runlog()

        except ZenAppTeardownException as exc:
            self.error("Teardown exception: {}".format(exc))

        except ZenAppException as exc:
            self.error("Application exception: {}".format(exc))


    #---------------------------------------------------------------------------
    # APPLICATION MODE METHODS (MAIN RUN METHODS).
    #---------------------------------------------------------------------------


    def run(self):
        """
        **APPLICATION MODE:** *Standalone application mode* - Main processing method.

        Run as standalone application, performs all stages of object life-cycle:
            1. setup stage
            2.1 action stage
            2.2.1 processing stage
            2.2.2 evaluation stage
            2.2.3 teardown stage
        """
        self._stage_setup()

        if self.c(self.CONFIG_ACTION):
            self._stage_action()
        else:
            self._stage_process()
            self._stage_evaluate()
            self._stage_teardown()

        self.dbgout("Exiting with return code '{}'".format(self.retc))
        sys.exit(self.retc)

    def plugin(self):
        """
        **APPLICATION MODE:** *Plugin mode* - Main processing method.

        This method allows the object to be used as plugin within larger framework.
        Only the necessary setup is performed.
        """
        self._stage_setup()


    #---------------------------------------------------------------------------
    # BUILT-IN ACTION CALLBACK METHODS.
    #---------------------------------------------------------------------------


    def cbk_action_config_view(self):
        """
        **ACTION:** Parse and view application configurations.
        """
        self.p("Script configurations:")
        tree = pydgets.widgets.TreeWidget()
        self.p("\n".join(tree.render(self.config)))

    def cbk_action_runlog_dump(self):
        """
        **ACTION:** Dump given application runlog.
        """
        rld = self.c(self.CONFIG_RUNLOG_DIR)
        input_file = self.c(self.CONFIG_INPUT, False)
        if not input_file:
            rlfn = os.path.join(rld, '*.runlog')
            runlog_files = sorted(glob.glob(rlfn), reverse = True)
            if runlog_files:
                input_file = runlog_files.pop(0)
            else:
                self.p("There are no runlog files")
                return

        self.p("")
        self.p("Raw view of application runlog '{}':".format(input_file))
        runlog = self.json_load(input_file)
        self.p("")
        tree = pydgets.widgets.TreeWidget()
        self.p("\n".join(tree.render(runlog)))

    def cbk_action_runlog_view(self):
        """
        **ACTION:** View details of given application runlog.
        """
        rld = self.c(self.CONFIG_RUNLOG_DIR)
        input_file = self.c(self.CONFIG_INPUT, False)
        if not input_file:
            rlfn = os.path.join(rld, '*.runlog')
            runlog_files = sorted(glob.glob(rlfn), reverse = True)
            if runlog_files:
                input_file = runlog_files.pop(0)
            else:
                self.p("There are no runlog files")
                return

        self.p("")
        self.p("Viewing application runlog '{}':".format(input_file))
        runlog = self.json_load(input_file)
        self.p("")
        analysis = self.runlog_analyze(runlog)

        self.runlog_format_analysis(analysis)
        self.p("")

    def cbk_action_runlogs_list(self):
        """
        **ACTION:** View list of all available application runlogs.
        """
        rld = self.c(self.CONFIG_RUNLOG_DIR)
        limit = self.c(self.CONFIG_LIMIT)
        (runlog_files, rlcount) = self.runlogs_list(reverse = True, limit = limit)
        runlogtree = {}
        runlogtree[rld] = []
        for rlf in runlog_files:
            runlogtree[rld].append(rlf)

        self.p("")
        self.p("Listing application runlogs in directory '{}':".format(rld))
        self.p("  Runlog(s) found: {:,d}".format(rlcount))
        if limit:
            self.p("  Result limit: {:,d}".format(limit))
        if runlogtree[rld]:
            self.p("")
            tree = pydgets.widgets.TreeWidget()
            self.p("\n".join(tree.render(runlogtree)))
        self.p("")

    def cbk_action_runlogs_dump(self):
        """
        **ACTION:** View list of all available application runlogs.
        """
        rld = self.c(self.CONFIG_RUNLOG_DIR)
        limit = self.c(self.CONFIG_LIMIT)
        (runlog_files, rlcount) = self.runlogs_list(reverse = True, limit = limit)
        runlogs = []
        for rlf in runlog_files:
            runlogs.append((rlf, self.json_load(rlf)))

        self.p("")
        self.p("Dumping application runlog(s) in directory '{}':".format(rld))
        self.p("  Runlog(s) found: {:,d}".format(rlcount))
        if limit:
            self.p("  Result limit: {:,d}".format(limit))
        if runlogs:
            self.p("")
            tree = pydgets.widgets.TreeWidget()
            for runl in runlogs:
                self.p("Runlog '{}':".format(runl[0]))
                self.p("\n".join(tree.render(runl[1])))
        self.p("")

    def cbk_action_runlogs_evaluate(self):
        """
        **ACTION:** Evaluate previous application runlogs.
        """
        rld = self.c(self.CONFIG_RUNLOG_DIR)
        limit = self.c(self.CONFIG_LIMIT)
        (runlog_files, rlcount) = self.runlogs_list(reverse = True, limit = limit)
        runlogs = []
        for rlf in runlog_files:
            runlogs.append(self.json_load(rlf))

        self.p("")
        self.p("Evaluating application runlogs in directory '{}':".format(rld))
        self.p("  Runlog(s) found: {:,d}".format(rlcount))
        if limit:
            self.p("  Result limit: {:,d}".format(limit))
        if runlogs:
            self.p("")
            evaluation = self.runlogs_evaluate(runlogs)
            self.runlogs_format_evaluation(evaluation)
        self.p("")


    #---------------------------------------------------------------------------
    # ACTION HELPERS
    #---------------------------------------------------------------------------


    def runlog_analyze(self, runlog):
        """
        Analyze given runlog.
        """
        curt = int(time.time())
        tm_tmp = {}
        analysis = {self.RLANKEY_DURPRE: 0, self.RLANKEY_DURPROC: 0, self.RLANKEY_DURPOST: 0, self.RLANKEY_DURATIONS: {}}
        analysis[self.RLANKEY_RUNLOG]  = runlog
        analysis[self.RLANKEY_LABEL]   = runlog[self.RLKEY_TSSTR]
        analysis[self.RLANKEY_AGE]     = curt - runlog[self.RLKEY_TS]
        analysis[self.RLANKEY_RESULT]  = runlog[self.RLKEY_RESULT]
        analysis[self.RLANKEY_COMMAND] = runlog.get(self.RLANKEY_COMMAND, runlog.get('operation', 'unknown'))

        # Calculate application processing duration
        analysis[self.RLANKEY_DURRUN]  = runlog[self.RLKEY_TMARKS][-1]['time'] - runlog[self.RLKEY_TMARKS][0]['time']

        # Calculate separate durations for all stages
        for tmark in runlog[self.RLKEY_TMARKS]:
            ptrna = re.compile('^(.*)_start$')
            ptrnb = re.compile('^(.*)_stop$')
            match = ptrna.match(tmark['ident'])
            if match:
                matchg = match.group(1)
                tm_tmp[matchg] = tmark['time']
                continue
            match = ptrnb.match(tmark['ident'])
            if match:
                matchg = match.group(1)
                analysis[self.RLANKEY_DURATIONS][matchg] = tmark['time'] - tm_tmp[matchg]
                if matchg in ('stage_configure', 'stage_check', 'stage_setup'):
                    analysis[self.RLANKEY_DURPRE] += analysis[self.RLANKEY_DURATIONS][matchg]
                elif matchg == 'stage_process':
                    analysis[self.RLANKEY_DURPROC] += analysis[self.RLANKEY_DURATIONS][matchg]
                elif matchg in ('stage_evaluate', 'stage_teardown'):
                    analysis[self.RLANKEY_DURPOST] += analysis[self.RLANKEY_DURATIONS][matchg]
                continue

        analysis[self.RLANKEY_EFFECTIVITY] = ((analysis[self.RLANKEY_DURPROC]/analysis[self.RLANKEY_DURRUN])*100)
        return self._sub_runlog_analyze(runlog, analysis)

    def runlog_format_analysis(self, analysis):
        """
        Format given runlog analysis.
        """
        self.p("General information:")
        tablew = pydgets.widgets.TableWidget()
        tcols = [
            { 'label': 'Statistics', 'data_formating': '{:s}', 'align': '<' },
            { 'label': 'Value',      'data_formating': '{:s}', 'align': '>' },
        ]
        tbody = [
            ['Label:',       analysis[self.RLANKEY_LABEL]],
            ['Runtime:',     str(datetime.timedelta(seconds=analysis[self.RLANKEY_DURRUN]))],
            ['Effectivity:', '{:6.2f} %'.format(analysis[self.RLANKEY_EFFECTIVITY])],
            ['Age:',         str(datetime.timedelta(seconds=int(analysis[self.RLANKEY_AGE])))],
            ['Command:',     analysis[self.RLANKEY_COMMAND]],
            ['Errors:',      str(len(analysis[self.RLANKEY_RUNLOG][self.RLKEY_ERRORS]))],
            ['Result:',      analysis[self.RLANKEY_RESULT]],
        ]
        self.p("\n".join(tablew.render(tbody, columns = tcols, enumerate = False, header = False)))

        if analysis[self.RLANKEY_RUNLOG][self.RLKEY_ERRORS]:
            self.p("")
            self.p("Processing errors:")
            listw = pydgets.widgets.ListWidget()
            self.p("\n".join(listw.render(analysis[self.RLANKEY_RUNLOG][self.RLKEY_ERRORS])))

        #self.p("")
        #self.p("Full analysis:")
        #treew = pydgets.widgets.TreeWidget()
        #self.p("\n".join(treew.render(analysis)))

        self.p("")
        self._sub_runlog_format_analysis(analysis)

    def runlogs_evaluate(self, runlogs):
        """
        Evaluate given runlogs.
        """
        evaluation = {self.RLEVKEY_ANALYSES: []}
        for runl in runlogs:
            rslt = self.runlog_analyze(runl)
            evaluation[self.RLEVKEY_ANALYSES].append(rslt)
        if evaluation[self.RLEVKEY_ANALYSES]:
            evaluation[self.RLEVKEY_MINDURRUN] = min([x[self.RLANKEY_DURRUN] for x in evaluation[self.RLEVKEY_ANALYSES]])
            evaluation[self.RLEVKEY_MAXDURRUN] = max([x[self.RLANKEY_DURRUN] for x in evaluation[self.RLEVKEY_ANALYSES]])
            evaluation[self.RLEVKEY_AVGDURRUN] = sum([x[self.RLANKEY_DURRUN] for x in evaluation[self.RLEVKEY_ANALYSES]]) / len(evaluation[self.RLEVKEY_ANALYSES])
            evaluation[self.RLEVKEY_MINDURPROC] = min([x[self.RLANKEY_DURPROC] for x in evaluation[self.RLEVKEY_ANALYSES]])
            evaluation[self.RLEVKEY_MAXDURPROC] = max([x[self.RLANKEY_DURPROC] for x in evaluation[self.RLEVKEY_ANALYSES]])
            evaluation[self.RLEVKEY_AVGDURPROC] = sum([x[self.RLANKEY_DURPROC] for x in evaluation[self.RLEVKEY_ANALYSES]]) / len(evaluation[self.RLEVKEY_ANALYSES])
            evaluation[self.RLEVKEY_MINEFFECT] = min([x[self.RLANKEY_EFFECTIVITY] for x in evaluation[self.RLEVKEY_ANALYSES]])
            evaluation[self.RLEVKEY_MAXEFFECT] = max([x[self.RLANKEY_EFFECTIVITY] for x in evaluation[self.RLEVKEY_ANALYSES]])
            evaluation[self.RLEVKEY_AVGEFFECT] = sum([x[self.RLANKEY_EFFECTIVITY] for x in evaluation[self.RLEVKEY_ANALYSES]]) / len(evaluation[self.RLEVKEY_ANALYSES])
        return self._sub_runlogs_evaluate(runlogs, evaluation)

    def runlogs_format_evaluation(self, evaluation):
        """
        Format runlog evaluation.
        """
        table_columns = [
            { 'label': 'Date' },
            { 'label': 'Age',     'data_formating': '{}',      'align': '>' },
            { 'label': 'Runtime', 'data_formating': '{}',      'align': '>' },
            { 'label': 'Process', 'data_formating': '{}',      'align': '>' },
            { 'label': 'E [%]',   'data_formating': '{:6.2f}', 'align': '>' },
            { 'label': 'Errors',  'data_formating': '{:,d}',   'align': '>' },
            { 'label': 'Command', 'data_formating': '{}',      'align': '>' },
            { 'label': 'Result',  'data_formating': '{}',      'align': '>' },
        ]
        table_data = []
        for anl in evaluation[self.RLEVKEY_ANALYSES]:
            table_data.append(
                [
                    anl[self.RLANKEY_LABEL],
                    str(datetime.timedelta(seconds=int(anl[self.RLANKEY_AGE]))),
                    str(datetime.timedelta(seconds=anl[self.RLANKEY_DURRUN])),
                    str(datetime.timedelta(seconds=anl[self.RLANKEY_DURPROC])),
                    anl[self.RLANKEY_EFFECTIVITY],
                    len(anl[self.RLANKEY_RUNLOG][self.RLKEY_ERRORS]),
                    anl[self.RLANKEY_COMMAND],
                    anl[self.RLANKEY_RESULT],
                ]
            )
        self.p("General application processing statistics:")
        tablew = pydgets.widgets.TableWidget()
        self.p("\n".join(tablew.render(table_data, columns = table_columns)))
        if evaluation[self.RLEVKEY_ANALYSES]:
            self.p("                   Minimal value: {:s}   {:s}   {:6.2f}".format(
                str(datetime.timedelta(seconds=evaluation[self.RLEVKEY_MINDURRUN])),
                str(datetime.timedelta(seconds=evaluation[self.RLEVKEY_MINDURPROC])),
                evaluation[self.RLEVKEY_MINEFFECT]
            ))
            self.p("                   Maximal value: {:s}   {:s}   {:6.2f}".format(
                str(datetime.timedelta(seconds=evaluation[self.RLEVKEY_MAXDURRUN])),
                str(datetime.timedelta(seconds=evaluation[self.RLEVKEY_MAXDURPROC])),
                evaluation[self.RLEVKEY_MAXEFFECT]
            ))
            self.p("                   Average value: {:s}   {:s}   {:6.2f}".format(
                str(datetime.timedelta(seconds=evaluation[self.RLEVKEY_AVGDURRUN])),
                str(datetime.timedelta(seconds=evaluation[self.RLEVKEY_AVGDURPROC])),
                evaluation[self.RLEVKEY_AVGEFFECT]
            ))

        self.p("")
        self._sub_runlogs_format_evaluation(evaluation)

    def runlogs_list(self, **kwargs):
        """
        List all available runlogs.
        """
        reverse = kwargs.get('reverse', False)
        limit = kwargs.get('limit', None)
        rlfn = os.path.join(self.c(self.CONFIG_RUNLOG_DIR), '*.runlog')
        rllist = sorted(glob.glob(rlfn), reverse = reverse)
        rlcount = len(rllist)

        if limit:
            return (rllist[:limit], rlcount)
        return (rllist, rlcount)


    #---------------------------------------------------------------------------
    # INTERNAL UTILITIES.
    #---------------------------------------------------------------------------


    def _get_process_serial(self):
        """
        Return part of the filename unique for this process in case multiple instances are running.
        """
        if self._process_serial is None:
            self._process_serial = hex(os.getpid())[2:].zfill(5)
        return self._process_serial

    def _get_fn_runlog(self):
        """
        Return the name of the runlog file for current process.

        :return: Name of the runlog file.
        :rtype: str
        """
        return os.path.join(self.c(self.CONFIG_RUNLOG_DIR), "{}.{}.runlog".format(self.runlog[self.RLKEY_TSFSF], self._get_process_serial()))

    def _get_fn_pstate(self):
        """
        Return the name of the persistent state file for current process.

        :return: Name of the persistent state file.
        :rtype: str
        """
        return self.c(self.CONFIG_PSTATE_FILE)

    def _get_fn_pidfile(self):
        """
        Return the name of the pidfile for current process.
        """
        return re.sub(r'\.pid$',".{}.pid".format(self._get_process_serial()), self.c(self.CONFIG_PID_FILE))

    def _utils_detect_actions(self):
        """
        Returns the sorted list of all available actions current application is capable
        of performing. The detection algorithm is based on string analysis of all
        available methods. Any method starting with string ``cbk_action_`` will
        be appended to the list, lowercased and with ``_`` characters replaced with ``-``.
        """
        ptrn = re.compile(self.PTRN_ACTION_CBK)
        attrs = sorted(dir(self))
        result = []
        for atr in attrs:
            if not callable(getattr(self, atr)):
                continue
            match = ptrn.match(atr)
            if match:
                result.append(atr.replace(self.PTRN_ACTION_CBK,'').replace('_','-').lower())
        return result

    def _utils_runlog_dump(self, runlog):
        """
        Write application runlog into ``stdout``.

        :param dict runlog: Structure containing application runlog.
        """
        self.p("Application runlog >>>\n{}".format(self.json_dump(runlog)))

    def _utils_runlog_log(self, runlog):
        """
        Write application runlog into logging service.

        :param dict runlog: Structure containing application runlog.
        """
        self.p("Application runlog >>>\n{}".format(self.json_dump(runlog)))

    def _utils_runlog_save(self, runlog):
        """
        Write application runlog to external JSON file.

        :param dict runlog: Structure containing application runlog.
        """
        # Attempt to create application runlog directory.
        if not os.path.isdir(self.c(self.CONFIG_RUNLOG_DIR)):
            self.logger.info("Creating application runlog directory '%s'", self.c(self.CONFIG_RUNLOG_DIR))
            os.makedirs(self.c(self.CONFIG_RUNLOG_DIR))

        rlfn = self._get_fn_runlog()
        self.dbgout("Saving application runlog to file '{}'".format(rlfn))
        self.json_save(rlfn, runlog)
        self.logger.info("Application runlog saved to file '%s'", rlfn)

    def _utils_pstate_dump(self, state):
        """
        Write persistent state into ``stdout``.

        :param dict state: Structure containing application persistent state.
        """
        self.p("Application persistent state >>>\n{}".format(self.json_dump(state)))

    def _utils_pstate_log(self, state):
        """
        Write persistent state into logging service.

        :param dict state: Structure containing application persistent state.
        """
        self.logger.info("Application persistent state >>>\n%s", self.json_dump(state))

    def _utils_pstate_save(self, state):
        """
        Write application persistent state to external JSON file.

        :param dict state: Structure containing application persistent state.
        """
        sfn = self._get_fn_pstate()
        self.dbgout("Saving application persistent state to file '{}'".format(sfn))
        self.json_save(sfn, state)
        self.logger.info("Application persistent state saved to file '%s'", sfn)


    #---------------------------------------------------------------------------
    # SHORTCUT METHODS, HELPERS AND TOOLS.
    #---------------------------------------------------------------------------


    def c(self, key, default = None):  # pylint: disable=locally-disabled,invalid-name
        """
        Shortcut method: Get given configuration value, shortcut for:

            self.config.get(key, default)

        :param str key: Name of the configuration value.
        :param default: Default value to be returned when key is not set.
        :return: Configuration value fogr given key.
        """
        if default is None:
            return self.config.get(key)
        return self.config.get(key, default)

    def cc(self, key, default = None):  # pylint: disable=locally-disabled,invalid-name
        """
        Shortcut method: Get given core configuration value, shortcut for:

            self.config[self.CORE].get(key, default)

        Core configurations are special configurations under configuration key
        ``__CORE__``, which may only either be hardcoded, or calculated from other
        configurations.

        :param str key: Name of the core configuration value.
        :param default: Default value to be returned when key is not set.
        :return: Core configuration value fogr given key.
        """
        if default is None:
            return self.config[self.CORE].get(key)
        return self.config[self.CORE].get(key, default)

    def p(self, string, level = 0):  # pylint: disable=locally-disabled,invalid-name
        """
        Print given string to ``sys.stdout`` with respect to ``quiet`` and ``verbosity``
        settings.

        :param str string: String to print.
        :param int level: Required minimal verbosity level to print the message.
        """
        if not self.c(self.CONFIG_QUIET) and self.c(self.CONFIG_VERBOSITY) >= level:
            print(string)

    def error(self, error, retc = None, trcb = None):
        """
        Register given error, that occured during application run. Registering in
        the case of this method means printing the error message to logging facility,
        storing the message within the appropriate runlog data structure, generating
        the traceback when required and altering the runlog result and return code
        attributes accordingly.

        :param str error: Error message to be written.
        :param int retc: Requested return code with which to terminate the application.
        :param Exception trcb: Optional exception object.
        """
        self.retc = retc if retc is not None else self.RC_FAILURE

        errstr = "{}".format(error)
        self.logger.error(errstr)

        if trcb:
            tbexc = traceback.format_tb(trcb)
            self.logger.error("\n%s", "".join(tbexc))

        self.runlog[self.RLKEY_ERRORS].append(errstr)
        self.runlog[self.RLKEY_RESULT] = self.RESULT_FAILURE
        self.runlog[self.RLKEY_RC]     = self.retc

    @staticmethod
    def dbgout(message):
        """
        Routine for printing additional debug messages. The given message will be
        printed only in case the static class variable ``FLAG_DEBUG`` flag is set
        to ``True``. This can be done either by explicit assignment in code, or
        using command line argument ``--debug``, which is evaluated ASAP and sets
        the variable to ``True``. The message will be printed to ``sys.stderr``.

        :param str message: Message do be written.
        """
        if BaseApp.FLAG_DEBUG:
            print("* {} DBGOUT: {}".format(time.strftime('%Y-%m-%d %X', time.localtime()), message), file=sys.stderr)

    @staticmethod
    def excout(exception, retc = None):
        """
        Routine for displaying the exception message to the user without traceback
        and terminating the application. This routine is intended to display information
        about application errors, that are not caused by the application code itself
        (like missing configuration file, non-writable directories, etc.) and that
        can not be logged because of the fact, that the logging service was not yet
        initialized. For that reason this method is used to handle exceptions during
        the **__init__** and **setup** stages.

        :param Exception exception: Exception object.
        :param int retc: Requested return code with which to terminate the application.
        """
        retc = retc if retc is not None else BaseApp.RC_FAILURE

        print("{} CRITICAL ERROR: {}".format(time.strftime('%Y-%m-%d %X', time.localtime()), exception), file=sys.stderr)
        sys.exit(retc)

    def execute_command(self, command, can_fail = False):
        """
        Execute given shell command.
        """
        self.logger.info("Executing system command >>>\n%s", command)

        result = None
        if can_fail:
            result = subprocess.call(command, shell = True)
        else:
            result = subprocess.check_output(command, shell = True)

        self.logger.debug("System command result >>>\n%s", pprint.pformat(result, indent=4))
        return result

    def time_mark(self, ident, descr):
        """
        Mark current time with additional identifier and description to application
        runlog.

        :param str ident: Time mark identifier.
        :param str descr: Time mark description.
        :return: Time mark data structure.
        :rtype: dict
        """
        mark = {
            'ident': ident,
            'descr': descr,
            'time':  time.time()
        }
        self.runlog[self.RLKEY_TMARKS].append(mark)
        return mark

    @staticmethod
    def json_dump(data, **kwargs):
        """
        Dump given data structure into JSON string.

        :param dict data: Data to be dumped to JSON.
        :param kwargs: Optional arguments to pass to :py:func:`pyzenkit.jsonconf.json_dump` method.
        :return: Data structure as JSON string.
        :rtype: str
        """
        return pyzenkit.jsonconf.json_dump(data, **kwargs)

    @staticmethod
    def json_save(json_file, data, **kwargs):
        """
        Save given data structure into given JSON file.

        :param str json_file: Name of the JSON file to write to.
        :param dict data: Data to be dumped to JSON.
        :param kwargs: Optional arguments to pass to :py:func:`pyzenkit.jsonconf.json_save` method.
        :return: Always returns ``True``.
        :rtype: bool
        """
        return pyzenkit.jsonconf.json_save(json_file, data, **kwargs)

    @staticmethod
    def json_load(json_file):
        """
        Load data structure from given JSON file.

        :param str json_file: Name of the JSON file to read from.
        :return: Loaded data structure.
        :rtype: dict
        """
        return pyzenkit.jsonconf.json_load(json_file)

    @staticmethod
    def format_progress_bar(percent, bar_len = 50):
        """
        Format progress bar from given values.
        """
        progress = ""
        for i in range(bar_len):
            if i < int(bar_len * percent):
                progress += "="
            else:
                progress += " "
        return " [%s] %.2f%%" % (progress, percent * 100)

    @staticmethod
    def draw_progress_bar(percent, bar_len = 50):
        """
        Draw progress bar on standard output terminal.
        """
        sys.stdout.write("\r")
        sys.stdout.write(BaseApp.format_progress_bar(percent, bar_len))
        sys.stdout.flush()


#-------------------------------------------------------------------------------


class DemoBaseApp(BaseApp):
    """
    Minimalistic class for demonstration purposes. Study implementation of this
    class for tutorial on how to use this framework.
    """

    def __init__(self, name = None, description = None):
        """
        Initialize demonstration application. This method overrides the base
        implementation in :py:func:`baseapp.BaseApp.__init__` and it aims to
        even more simplify the application object creation.

        :param str name: Optional application name.
        :param str description: Optional application description.
        """
        name        = 'demo-baseapp.py' if not name else name
        description = 'DemoBaseApp - Demonstration application' if not description else description

        super().__init__(
            name        = name,
            description = description,

            #
            # Configure required application paths to harmless locations.
            #
            path_bin = 'tmp',
            path_cfg = 'tmp',
            path_var = 'tmp',
            path_log = 'tmp',
            path_run = 'tmp',
            path_tmp = 'tmp'
        )

    def _sub_stage_process(self):
        """
        Script lifecycle stage **PROCESS**.
        """
        # Update the persistent state to view the changes.
        self.pstate['counter'] = self.pstate.get('counter', 0) + 1

        # Log something to show we have reached this point of execution.
        self.logger.info("Demonstration implementation for BaseApp demo application")
        self.logger.info("Try executing this demo with following parameters:")
        self.logger.info("* python3 pyzenkit/baseapp.py --help")
        self.logger.info("* python3 pyzenkit/baseapp.py --verbose")
        self.logger.info("* python3 pyzenkit/baseapp.py --verbose --verbose")
        self.logger.info("* python3 pyzenkit/baseapp.py --verbose --verbose --verbose")
        self.logger.info("* python3 pyzenkit/baseapp.py --debug")
        self.logger.info("* python3 pyzenkit/baseapp.py --log-level debug")
        self.logger.info("* python3 pyzenkit/baseapp.py --pstate-dump")
        self.logger.info("* python3 pyzenkit/baseapp.py --runlog-dump")
        self.logger.info("Number of BaseApp runs from persistent state: '%d'", self.pstate.get('counter'))

        # Test direct console output with conjunction with verbosity levels.
        self.p("Hello world from BaseApp")
        self.p("Hello world from BaseApp, verbosity level 1", 1)
        self.p("Hello world from BaseApp, verbosity level 2", 2)
        self.p("Hello world from BaseApp, verbosity level 3", 3)


#-------------------------------------------------------------------------------

#
# Perform the demonstration.
#
if __name__ == "__main__":

    # Prepare demonstration environment.
    APP_NAME = 'demo-baseapp.py'
    for directory in (
            DemoBaseApp.get_resource_path('tmp'),
            DemoBaseApp.get_resource_path('tmp/{}'.format(APP_NAME))
    ):
        try:
            os.mkdir(directory)
        except FileExistsError:
            pass

    DemoBaseApp.json_save(
        DemoBaseApp.get_resource_path('tmp/{}.conf'.format(APP_NAME)),
        {'test_a':1}
    )

    # Launch demonstration.
    BASE_APP = DemoBaseApp(APP_NAME)
    BASE_APP.run()
