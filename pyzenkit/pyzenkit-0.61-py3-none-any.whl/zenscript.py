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
This module provides base implementation of generic script represented by the
:py:class:`pyzenkit.zenscript.ZenScript` class with built-in support for regular
executions. It builds on top of :py:mod:`pyzenkit.baseapp` module and adds couple
of other usefull features:

* Support for executing multiple different **commands**.
* Support for multiple execution modes (**default**, **regular**, **shell**).
* Support for executions in regular time intervals.


Script commands
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Every script provides support for more, possibly similar, commands to be implemented
within one script. The use case for this may be a fictional example backup script,
that can provide separate commands for *backup* and *restore* features, but pack
both of them nicelly into one package/module/executable.

Commands are implemented very easily by adding new method according to following
convention:

* Command callback must be method without any mandatory arguments.
* Command callback method name must begin with ``cbk_command_`` prefix.
* Command name in the method name after the prefix must also be `snake_cased``.
* Command name will be calculated by replacing ``_`` with ``-``.

Following are examples of valid command callbacks::

    cbk_command_test(self)         # Will be mapped to 'test' command.
    cbk_command_another_test(self) # Will be mapped to 'another-test' command.

When a method is implemented according to these guidelines, it will be automatically
recognized and executable.

Commands may be executed by selecting the desired command by command line argument::

    path/to/zenscript.py --command default
    path/to/zenscript.py --command=alternative

Command may also be selected permanently inside configuration file under the dictionary
key ``command``.


Script execution modes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Script execution supports following modes:

**regular**
    In a **regular** mode the script is intended to be executed in regular time
    intervals from a *cron-like* service (usually). The internal application
    configuration is forced into following state:

    * Console output is explicitly suppressed
    * Console logging level is explicitly forced to **warning** level
    * Logging to log file is explicitly forced to be **enabled**
    * Runlog saving is explicitly forced to be **enabled**
    * Persistent state saving is explicitly forced to be **enabled**

**shell**
    In a **shell** mode the script is intended to be executed by hand from interactive
    shell. It is intended to be used for debugging or experimental purposes, or for
    applications that are executed by hand by a user. The internal application
    configuration is forced into following state:

    * Logging to log file is explicitly **disabled**
    * Runlog saving is explicitly **disables**
    * Persistent state saving is explicitly **disabled**

**default**
    In a **default** mode the script directs its output both to the files and
    ``stdout`` and runlog and persistent state saving are **enabled**.


Regular executions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Following is a list of predefined regular execution time intervals:

* 5_minutes
* 10_minutes
* 15_minutes
* 20_minutes
* 30_minutes
* hourly
* 2_hourly
* 3_hourly
* 4_hourly
* 6_hourly
* 12_hourly
* daily
* weekly
* 2_weekly
* 4_weekly

The :py:func:`ZenScript.calculate_interval_thresholds` method can be used to calculate
time interval thresholds (lower and upper boundary) for given time interval and
time. These values can be then used for a number of use cases like fetching data
from database etc.


Module contents
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* :py:class:`ZenScriptException`
* :py:class:`ZenScript`
* :py:class:`DemoZenScript`


Programming API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* public methods:

    * calculate time interval thresholds: :py:func:`ZenScript.calculate_interval_thresholds`
    * execute script command by name: :py:func:`ZenScript.execute_script_command`
    * get a name of a default command: :py:func:`ZenScript.get_default_command`
"""

__author__  = "Honza Mach <honza.mach.ml@gmail.com>"


import os
import re
import datetime

#
# Custom libraries.
#
import pyzenkit.baseapp


#
# Predefined constants for runtime intervals
#
RUN_INTERVALS = {
    '5_minutes':      300,
    '10_minutes':     600,
    '15_minutes':     900,
    '20_minutes':    1200,
    '30_minutes':    1800,
    'hourly':        3600,
    '2_hourly':   (2*3600),
    '3_hourly':   (3*3600),
    '4_hourly':   (4*3600),
    '6_hourly':   (6*3600),
    '12_hourly': (12*3600),
    'daily':        86400,
    'weekly':    (7*86400),
    '2_weekly': (14*86400),
    '4_weekly': (28*86400),
}

RE_TIMESTAMP = re.compile(r"^([0-9]{4})-([0-9]{2})-([0-9]{2})[Tt ]([0-9]{2}):([0-9]{2}):([0-9]{2})(?:\.([0-9]+))?([Zz]|(?:[+-][0-9]{2}:[0-9]{2}))$")


#-------------------------------------------------------------------------------


def t_datetime(val):
    """
    Convert/validate datetime. The value received by this conversion function may
    be either ``datetime.datetime`` object (in that case no action will be done),
    unix timestamp as ``float`` or datetime as RFC3339 string.

    :param any val: Value to be converted/validated
    :return: Datetime object
    :rtype: datetime.datetime
    :raises ValueError: if the value could not be converted to datetime.datetime object
    """
    # There is nothing to do in case val is already datetime object.
    if isinstance(val, datetime.datetime):
        return val

    # First try a numeric type - UTC unix timestamp.
    try:
        return datetime.datetime.utcfromtimestamp(float(val))
    except (TypeError, ValueError):
        pass

    # Finally try RFC3339 string.
    res = RE_TIMESTAMP.match(val)
    if res is not None:
        year, month, day, hour, minute, second = (int(n or 0) for n in res.group(*range(1, 7)))
        us_str = (res.group(7) or '0')[:6].ljust(6, '0')
        us_int = int(us_str)
        zonestr = res.group(8)
        zonespl = (0, 0) if zonestr in ['z', 'Z'] else [int(i) for i in zonestr.split(':')]
        zonediff = datetime.timedelta(minutes = zonespl[0]*60+zonespl[1])
        return datetime.datetime(year, month, day, hour, minute, second, us_int) - zonediff
    raise ValueError("Invalid datetime '{:s}'".format(val))


#-------------------------------------------------------------------------------


class ZenScriptException(pyzenkit.baseapp.ZenAppProcessException):
    """
    Describes problems specific to scripts.
    """


#-------------------------------------------------------------------------------


class ZenScript(pyzenkit.baseapp.BaseApp):
    """
    Base implementation of generic one-time execution script with built-in regular
    execution interval support.
    """

    #
    # Class constants.
    #

    # String patterns.
    PTRN_COMMAND_CBK = 'cbk_command_'

    # List of configuration keys.
    CONFIG_REGULAR           = 'regular'
    CONFIG_SHELL             = 'shell'
    CONFIG_COMMAND           = 'command'
    CONFIG_INTERVAL          = 'interval'
    CONFIG_ADJUST_THRESHOLDS = 'adjust_thresholds'
    CONFIG_TIME_HIGH         = 'time_high'

    # List of runlog keys.
    RLKEY_COMMAND = 'command'


    #---------------------------------------------------------------------------


    def _init_argparser(self, **kwargs):
        """
        Initialize application command line argument parser. This method overrides
        the base implementation in :py:func:`baseapp.BaseApp._init_argparser` and
        it must return valid :py:class:`argparse.ArgumentParser` object.

        Gets called from main constructor :py:func:`BaseApp.__init__`.

        :param kwargs: Various additional parameters passed down from constructor.
        :return: Initialized argument parser object.
        :rtype: argparse.ArgumentParser
        """
        argparser = super()._init_argparser(**kwargs)

        #
        # Create and populate options group for common script arguments.
        #
        arggroup_script = argparser.add_argument_group('common script arguments')

        # Setup mutually exclusive group for regular x shell mode option.
        group_a = arggroup_script.add_mutually_exclusive_group()

        group_a.add_argument('--regular', help = 'operational mode: regular script execution (flag)', action='store_true', default = None)
        group_a.add_argument('--shell',   help = 'operational mode: manual script execution from shell (flag)', action = 'store_true', default = None)

        arggroup_script.add_argument('--command',           help = 'name of the script command to be executed', choices = self._utils_detect_commands(), type = str, default = None)
        arggroup_script.add_argument('--interval',          help = 'time interval for regular executions', choices = RUN_INTERVALS.keys(), type = str, default = None)
        arggroup_script.add_argument('--adjust-thresholds', help = 'round-up time interval threshols to interval size (flag)', action = 'store_true', default = None)
        arggroup_script.add_argument('--time-high',         help = 'upper time interval threshold', type = t_datetime, default = None)

        return argparser

    def _init_config(self, cfgs, **kwargs):
        """
        Initialize default application configurations. This method overrides the
        base implementation in :py:func:`baseapp.BaseApp._init_argparser` and it
        adds additional configurations via ``cfgs`` parameter.

        Gets called from main constructor :py:func:`BaseApp.__init__`.

        :param list cfgs: Additional set of configurations.
        :param kwargs: Various additional parameters passed down from constructor.
        :return: Default configuration structure.
        :rtype: dict
        """
        cfgs = (
            (self.CONFIG_REGULAR,           False),
            (self.CONFIG_SHELL,             False),
            (self.CONFIG_INTERVAL,          None),
            (self.CONFIG_COMMAND,           self.get_default_command()),
            (self.CONFIG_ADJUST_THRESHOLDS, False),
            (self.CONFIG_TIME_HIGH,         datetime.datetime.utcnow()),
        ) + cfgs
        return super()._init_config(cfgs, **kwargs)

    def _configure_postprocess(self):
        """
        Perform configuration postprocessing and calculate core configurations.
        This method overrides the base implementation in :py:func:`baseapp.BaseApp._configure_postprocess`.

        Gets called from :py:func:`BaseApp._stage_setup_configuration`.
        """
        super()._configure_postprocess()

        if self.c(self.CONFIG_SHELL):
            self.config[self.CORE][self.CORE_LOGGING][self.CORE_LOGGING_TOFILE] = False
            self.dbgout("Logging to log file is explicitly suppressed by '--shell' configuration")

            self.config[self.CORE][self.CORE_RUNLOG][self.CORE_RUNLOG_SAVE] = False
            self.dbgout("Runlog saving is explicitly suppressed by '--shell' configuration")

            self.config[self.CORE][self.CORE_PSTATE][self.CORE_PSTATE_SAVE] = False
            self.dbgout("Persistent state saving is explicitly suppressed by '--shell' configuration")

        elif self.c(self.CONFIG_REGULAR):
            self.config[self.CONFIG_QUIET] = True
            self.dbgout("Console output is explicitly suppressed by '--regular' configuration")

            self.config[self.CORE][self.CORE_LOGGING][self.CORE_LOGGING_LEVELC] = 'WARNING'
            self.dbgout("Console logging level is explicitly forced to 'warning' by '--regular' configuration")

            self.config[self.CORE][self.CORE_LOGGING][self.CORE_LOGGING_TOFILE] = True
            self.dbgout("Logging to log file is explicitly forced by '--regular' configuration")

            self.config[self.CORE][self.CORE_RUNLOG][self.CORE_RUNLOG_SAVE] = True
            self.dbgout("Runlog saving is explicitly forced by '--regular' configuration")

            self.config[self.CORE][self.CORE_PSTATE][self.CORE_PSTATE_SAVE] = True
            self.dbgout("Persistent state saving is explicitly forced by '--regular' configuration")

        else:
            self.config[self.CORE][self.CORE_LOGGING][self.CORE_LOGGING_TOFILE] = True
            self.config[self.CORE][self.CORE_RUNLOG][self.CORE_RUNLOG_SAVE]     = True
            self.config[self.CORE][self.CORE_PSTATE][self.CORE_PSTATE_SAVE]     = True

    def _sub_stage_process(self):
        """
        **SUBCLASS HOOK**: Perform some actual processing in **process** stage.
        """
        # Determine, which command to execute.
        cmdname = self.c(self.CONFIG_COMMAND)
        self.runlog[self.RLKEY_COMMAND] = cmdname

        # Execute.
        self.execute_script_command(cmdname)


    #---------------------------------------------------------------------------


    def _utils_detect_commands(self):
        """
        Returns the sorted list of all available commands current script is capable
        of performing. The detection algorithm is based on string analysis of all
        available methods. Any method starting with string ``cbk_command_`` will
        be appended to the list, lowercased and with ``_`` characters replaced with ``-``.
        """
        ptrn = re.compile(self.PTRN_COMMAND_CBK)
        attrs = sorted(dir(self))
        result = []
        for atr in attrs:
            if not callable(getattr(self, atr)):
                continue
            match = ptrn.match(atr)
            if match:
                result.append(atr.replace(self.PTRN_COMMAND_CBK,'').replace('_','-').lower())
        return result


    #---------------------------------------------------------------------------


    def get_default_command(self):
        """
        Return the name of the default command. This method must be present and
        overriden in subclass and must return the name of desired default command.
        Following code is just a reminder for developer to not forget to implement
        this method.

        :return: Name of the default command.
        :rtype: str
        """
        raise NotImplementedError("This method must be implemented in subclass")

    def execute_script_command(self, command_name):
        """
        Execute given script command and store the received results into script runlog.

        Following method will call appropriate callback method to service the
        requested script command.

        Name of the callback method is generated from the name of the command by
        prepending string ``cbk_command_`` and replacing all ``-`` with ``_``.
        """
        command_name    = command_name.lower().replace('-','_')
        command_cbkname = '{}{}'.format(self.PTRN_COMMAND_CBK, command_name)
        self.dbgout("Executing callback '{}' for script command '{}'".format(command_cbkname, command_name))

        cbk = getattr(self, command_cbkname, None)
        if cbk:
            self.logger.info("Executing script command '%s'", command_name)
            self.runlog[command_name] = cbk()  # pylint: disable=locally-disabled,not-callable
        else:
            raise ZenScriptException("Invalid script command '{}', callback '{}' does not exist".format(command_name, command_cbkname))

    def calculate_interval_thresholds(self, time_high = None, interval = 'daily', adjust = False):
        """
        Calculate time interval thresholds based on given upper time interval boundary and
        time interval size.

        :param time_high: Upper time threshold as float (unix timestamp), string (RFC3339), or datetime.datetime object.
        :param str interval: Time interval, one of the interval defined in :py:mod:`pyzenkit.zenscript`.
        :param bool adjust: Adjust time thresholds to round values (floor).
        :return: Lower and upper time interval boundaries.
        :rtype: tuple of datetime.datetime
        """
        if interval not in RUN_INTERVALS:
            raise ValueError("Invalid time interval '{}', valid values are: '{}'".format(interval, ','.join(RUN_INTERVALS.keys())))
        interval_delta = RUN_INTERVALS[interval]

        if not time_high:
            time_high = datetime.datetime.utcnow()

        time_high = t_datetime(time_high)
        time_low  = time_high - datetime.timedelta(seconds = interval_delta)
        self.logger.debug("Calculated time interval thresholds: '%s' -> '%s' (%s, %i -> %i)", time_low.isoformat(), time_high.isoformat(), interval, time_low.timestamp(), time_high.timestamp())

        if adjust:
            ts_h = datetime.datetime.fromtimestamp(time_high.timestamp() - (time_high.timestamp() % interval_delta))
            ts_l = ts_h - datetime.timedelta(seconds = interval_delta)
            time_high = ts_h
            time_low  = ts_l
            self.logger.debug("Adjusted time interval thresholds: '%s' -> '%s' (%s, %i -> %i)", time_low.isoformat(), time_high.isoformat(), interval, time_low.timestamp(), time_high.timestamp())

        return (time_low, time_high)

    def calculate_upper_threshold(self, time_high = None, interval = 'daily', adjust = False):
        """
        Calculate upper time threshold based on given upper time interval boundary and
        time interval size.

        :param time_high: Upper time threshold as float (unix timestamp), string (RFC3339), or datetime.datetime object.
        :param str interval: Time interval, one of the interval defined in :py:mod:`pyzenkit.zenscript`.
        :param bool adjust: Adjust time thresholds to round values (floor).
        :return: Lower and upper time interval boundaries.
        :rtype: tuple of datetime.datetime
        """
        if interval not in RUN_INTERVALS:
            raise ValueError("Invalid time interval '{}', valid values are: '{}'".format(interval, ','.join(RUN_INTERVALS.keys())))
        interval_delta = RUN_INTERVALS[interval]

        if not time_high:
            time_high = datetime.datetime.utcnow()

        time_high = t_datetime(time_high)
        self.logger.debug("Calculated upper time threshold: '%s' (%s, %i)", time_high.isoformat(), interval, time_high.timestamp())

        if adjust:
            ts_h = datetime.datetime.fromtimestamp(time_high.timestamp() - (time_high.timestamp() % interval_delta))
            time_high = ts_h
            self.logger.debug("Adjusted upper time threshold: '%s' (%s, %i)", time_high.isoformat(), interval, time_high.timestamp())

        return time_high


class DemoZenScript(ZenScript):
    """
    Minimalistic class for demonstration purposes.
    """

    def __init__(self, name = None, description = None):
        """
        Initialize demonstration script. This method overrides the base
        implementation in :py:func:`baseapp.BaseApp.__init__` and it aims to
        even more simplify the script object creation.

        :param str name: Optional script name.
        :param str description: Optional script description.
        """
        name        = 'demo-zenscript.py' if not name else name
        description = 'DemoZenScript - Demonstration script' if not description else description

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

    def get_default_command(self):
        """
        Return the name of a default script operation.
        """
        return 'default'

    def cbk_command_default(self):
        """
        Default script command.
        """
        # Update the persistent state to view the changes.
        self.pstate['counter'] = self.pstate.get('counter', 0) + 1

        # Log something to show we have reached this point of execution.
        self.logger.info("Demonstration implementation for default script command")
        self.logger.info("Try executing this demo with following parameters:")
        self.logger.info("* python3 pyzenkit/zenscript.py --help")
        self.logger.info("* python3 pyzenkit/zenscript.py --verbose")
        self.logger.info("* python3 pyzenkit/zenscript.py --verbose --verbose")
        self.logger.info("* python3 pyzenkit/zenscript.py --verbose --verbose --verbose")
        self.logger.info("* python3 pyzenkit/zenscript.py --debug")
        self.logger.info("* python3 pyzenkit/zenscript.py --log-level debug")
        self.logger.info("* python3 pyzenkit/zenscript.py --pstate-dump")
        self.logger.info("* python3 pyzenkit/zenscript.py --runlog-dump")
        self.logger.info("* python3 pyzenkit/zenscript.py --command alternative")
        self.logger.info("Number of runs from persistent state: '%d'", self.pstate.get('counter'))
        self.logger.info("Current upper time boundary:          '%s'", self.c(self.CONFIG_TIME_HIGH).isoformat())

        # Test direct console output with conjunction with verbosity levels.
        self.p("Hello world")
        self.p("Hello world, verbosity level 1", 1)
        self.p("Hello world, verbosity level 2", 2)
        self.p("Hello world, verbosity level 3", 3)

        return { 'result': self.RESULT_SUCCESS, 'data': 5 }

    def cbk_command_alternative(self):
        """
        Alternative script command.
        """
        # Update the persistent state to view the changes.
        self.pstate['counter'] = self.pstate.get('counter', 0) + 1

        # Log something to show we have reached this point of execution.
        self.logger.info("Demonstration implementation for alternative script command")
        self.logger.info("Number of runs from persistent state: '%d'", self.pstate.get('counter'))

        # Test direct console output with conjunction with verbosity levels.
        self.p("Hello world")
        self.p("Hello world, verbosity level 1", 1)
        self.p("Hello world, verbosity level 2", 2)
        self.p("Hello world, verbosity level 3", 3)

        return { 'result': self.RESULT_SUCCESS, 'data': 100 }


#-------------------------------------------------------------------------------

#
# Perform the demonstration.
#
if __name__ == "__main__":

    # Prepare demonstration environment.
    APP_NAME = 'demo-zenscript.py'
    for directory in (
            DemoZenScript.get_resource_path('tmp'),
            DemoZenScript.get_resource_path('tmp/{}'.format(APP_NAME))
    ):
        try:
            os.mkdir(directory)
        except FileExistsError:
            pass

    DemoZenScript.json_save(
        DemoZenScript.get_resource_path('tmp/{}.conf'.format(APP_NAME)),
        {'test_a':1}
    )

    # Launch demonstration.
    ZENSCRIPT = DemoZenScript(APP_NAME)
    ZENSCRIPT.run()
