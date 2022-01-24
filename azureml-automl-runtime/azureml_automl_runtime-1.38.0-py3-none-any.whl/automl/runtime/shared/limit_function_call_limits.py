# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Functionality to enforce limits on a process.

Adapted from https://github.com/sfalkner/pynisher
"""
from typing import Optional
from azureml.automl.core.shared import limit_function_call_exceptions as lfce
import logging
import os

from azureml.automl.runtime.shared.win32_helper import Win32Helper


logger = logging.getLogger(__name__)


def set_limits(mem_in_mb: Optional[int],
               num_procs: Optional[int],
               wall_time_limit_in_s: Optional[int],
               cpu_time_limit_in_s: Optional[int],
               grace_period_in_s: int = 0) -> None:
    """Set the limits on the child process to enforce."""
    if os.name == 'nt':
        if Win32Helper.is_windows_7_or_earlier():
            # Setting limits will affect the parent process too, so it's not safe to do this on Windows 7 or lower.
            logger.warning('Resource limiting is not supported on Windows 7 or lower due to Win32 API limitations.')
            return
        # Wall clock time limit and grace period not supported under Windows
        Win32Helper.set_resource_limits(num_procs, cpu_time_limit_in_s, mem_in_mb)
    else:
        import resource
        import signal

        # TODO: Better error messages

        # simple signal handler to catch the signals for time limits
        def handler(signum, frame):
            # logs message with level debug on this logger
            logger.debug("signal handler: %i" % signum)
            if signum == signal.SIGXCPU:
                # when process reaches soft limit --> a SIGXCPU signal is
                # sent (it
                # normally terminates the process)
                raise lfce.CpuTimeoutException.create_without_pii()
            elif signum == signal.SIGALRM:
                # SIGALRM is sent to process when the specified time limit to
                # an alarm function elapses (when real or clock time elapses)
                logger.debug("timeout")
                raise lfce.TimeoutException.create_without_pii()
            elif signum == signal.SIGSEGV:
                # SIGSEGV possibly from AppInsights.
                # Unfortunately, there is no real way to recover from here as we
                # cannot go back to the stack frame in the main process where this occurred.
                logger.debug('Received segmentation fault.')

            raise lfce.SubprocessException.create_without_pii(
                'Uncaught signal: {} ({})'.format(signum, signal.Signals(signum).name))

        # catching all signals at this point turned out to interfere with the
        # subprocess (e.g. using ROS)
        signal.signal(signal.SIGALRM, handler)
        signal.signal(signal.SIGXCPU, handler)
        signal.signal(signal.SIGQUIT, handler)
        signal.signal(signal.SIGSEGV, handler)

        # code to catch EVERY catchable signal (even X11 related ones ... )
        # only use for debugging/testing as this seems to be too intrusive.
        """
        for i in [x for x in dir(signal) if x.startswith("SIG")]:
            try:
                signum = getattr(signal,i)
                print("register {}, {}".format(signum, i))
                signal.signal(signum, handler)
            except:
                print("Skipping %s"%i)
        """

        # set the memory limit
        if mem_in_mb is not None:
            # byte --> megabyte
            mem_in_b = mem_in_mb * 1024 * 1024
            # the maximum area (in bytes) of address space which may be taken
            # by the process.
            resource.setrlimit(resource.RLIMIT_AS, (mem_in_b, mem_in_b))

        # for now: don't allow the function to spawn subprocesses itself.
        # resource.setrlimit(resource.RLIMIT_NPROC, (1, 1)) Turns out, this is
        # quite restrictive, so we don't use this option by default
        if num_procs is not None:
            resource.setrlimit(resource.RLIMIT_NPROC, (num_procs, num_procs))

        # schedule an alarm in specified number of seconds
        if wall_time_limit_in_s is not None:
            signal.alarm(wall_time_limit_in_s)

        if cpu_time_limit_in_s is not None:
            # From the Linux man page: When the process reaches the soft
            # limit, it is sent a SIGXCPU signal. The default action for this
            # signal is to  terminate the process. However, the signal can
            # be caught, and the handler can return control to the main
            # program. If the process continues to consume CPU time, it will
            # be sent SIGXCPU once per second until the hard limit is
            # reached, at which time it is sent SIGKILL.
            resource.setrlimit(
                resource.RLIMIT_CPU, (cpu_time_limit_in_s,
                                      cpu_time_limit_in_s + grace_period_in_s))
