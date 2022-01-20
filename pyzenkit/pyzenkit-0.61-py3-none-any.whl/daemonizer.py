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
This module contains simple daemonization library, that takes care of all tasks
necessary to correctly daemonize a process. Correct daemonization consists of
following steps:

# Setup directories and limits
# Setup user and group permissions
# Terminal detachment with double fork and split session
# Setup signal handlers
# Close all open file descriptors (except for possible log files)
# Redirect ``stdin``, ``stdout``, ``stderr`` to ``/dev/null``
# Detect current PID and store it to appropriate PID file
# Remove PID file at process exit

These steps are performed during **full** daemonization. For many purposes it is however
usefull to be capable of some kind of **lite** daemonization, in which case almost
every step in previous list is done except for terminal detachment, closing all files
and redirecting ``std*`` to ``/dev/null``. This can be particularly usefull during
testing or debugging, or even during production deployments for some kind of
*stay in foreground* feature, which still enables the users to control the running
application from outside with signals.


Usage example
--------------------------------------------------------------------------------

Example usage is implemented directly within this module, please refer to source
code. To view the result of demonstration please execute the module directly with
Python3 interpretter.
"""

__author__  = "Honza Mach <honza.mach.ml@gmail.com>"
__credits__ = "Pavel Kácha <ph@rook.cz>"


import os
import signal
import atexit


def get_logger_files(logger):
    """
    Return file handlers of all currently active loggers.

    Result from this method will be used during daemonization process to close
    all open file descriptors but those belonging to given logger service.

    .. warning::

        This method is hacking internal structure of external module and might
        stop working, although the related interface has been stable for a long time.

    :param logging.Logger logger: Logger to be analyzed for open file descriptors.
    :return: List of open file descriptors used by logging service.
    :rtype: list
    """
    files = []
    for handler in logger.handlers:
        if hasattr(handler, 'stream') and hasattr(handler.stream, 'fileno'):
            files.append(handler.stream)
        if hasattr(handler, 'socket') and hasattr(handler.socket, 'fileno'):
            files.append(handler.socket)
    return files

def write_pid(pid_file, pid):
    """
    Write given PID into given PID file.

    :param str pidfile: Name of the PID file to write to.
    :param int pid: PID to write.
    """
    if not isinstance(pid, int):
        raise Exception("Process PID must be integer")
    pidfd = os.open(pid_file, os.O_RDWR|os.O_CREAT|os.O_EXCL|os.O_TRUNC)
    os.write(pidfd, bytes(str(pid)+"\n", 'UTF-8'))
    os.close(pidfd)

def read_pid(pid_file):
    """
    Read PID from given PID file.

    :param str pidfile: Name of the PID file to read from.
    :return: PID from given PID file.
    :rtype: int
    """
    with open(pid_file, 'r') as pidfd:
        return int(pidfd.readline().strip())


#-------------------------------------------------------------------------------

def _setup_fs(chroot_dir, work_dir, umask):
    """
    Internal helper method, setup filesystem related features.

    :param str chroot_dir: Name of the chroot directory (may be ``None``).
    :param str work_dir: Name of the work directory (may be ``None``).
    :param int umask: Umask as octal number (eg. ``0o002`` or ``0o022``, may be ``None``).
    """
    if chroot_dir is not None:
        os.chdir(chroot_dir)
        os.chroot(chroot_dir)
    if work_dir is not None:
        os.chdir(work_dir)
    if umask is not None:
        os.umask(umask)

def _setup_perms(uid, gid):
    """
    Internal helper method, setup user and group permissions.

    :param int uid: User ID to which to drop the permissions (may be ``None``).
    :param int gid: Group ID to which to drop the permissions (may be ``None``).
    """
    if gid is not None:
        os.setgid(gid)
    if uid is not None:
        os.setuid(uid)

def _setup_sh(signals):
    """
    Internal helper method, setup desired signal handlers.

    :param dict signals: Desired signal to be handled as keys and appropriate handlers as values (may be ``None``).
    """
    if signals is not None:
        for (signum, handler) in signals.items():
            signal.signal(signum, handler)

def _setup_pf(pid_file):
    """
    Internal helper method, setup PID file and atexit cleanup callback.

    :param str pid_file: Full path to the PID file (may be ``None``).
    """
    pid = os.getpid()

    if pid_file is not None:
        if not pid_file.endswith('.pid'):
            raise ValueError("Invalid PID file name '{}', it must end with '.pid' extension".format(pid_file))

        write_pid(pid_file, pid)

        # Define and setup 'atexit' closure, that will take care of removing pid file
        @atexit.register
        def unlink_pidfile():  # pylint: disable=locally-disabled,unused-variable
            """
            Callback for removing PID file at application exit.
            """
            try:
                os.unlink(pid_file)
            except:  # pylint: disable=locally-disabled,bare-except
                pass
        return (pid, pid_file)
    return (pid, None)


#-------------------------------------------------------------------------------


def daemonize_lite(  # pylint: disable=locally-disabled,too-many-arguments
        chroot_dir = None, work_dir = None, umask = None, uid = None, gid = None,
        pid_file = None, signals = None):
    """
    Perform lite daemonization of currently running process. All of the function
    arguments are optinal, so that it is possible to easily turn on/off almost
    any part of daemonization process. For example omitting the ``uid`` and ``gid``
    arguments will result in process permissions not to be changed.

    The lite daemonization does everything full daemonization does but detaching
    from current session. This can be usefull when debugging daemons, because they
    can be tested, benchmarked and profiled more easily.

    :param str chroot_dir: Name of the chroot directory (may be ``None``).
    :param str work_dir: Name of the work directory (may be ``None``).
    :param int umask: Umask as octal number (eg. ``0o002`` or ``0o022``, may be ``None``).
    :param int uid: User ID to which to drop the permissions (may be ``None``).
    :param int gid: Group ID to which to drop the permissions (may be ``None``).
    :param str pid_file: Full path to the PID file (may be ``None``).
    :param dict signals: Desired signals to be handled as keys and their appropriate handlers as values (may be ``None``).
    """

    # Setup directories, limits, users, etc.
    _setup_fs(chroot_dir, work_dir, umask)
    _setup_perms(uid, gid)

    # Setup signal handlers.
    _setup_sh(signals)

    # Write PID into PID file.
    return _setup_pf(pid_file)

def daemonize(  # pylint: disable=locally-disabled,too-many-arguments
        chroot_dir = None, work_dir = None, umask = None, uid = None, gid = None,
        pid_file = None, files_preserve = None, signals = None):
    """
    Perform full daemonization of currently running process. All of the function
    arguments are optinal, so that it is possible to easily turn on/off almost
    any part of daemonization process. For example omitting the ``uid`` and ``gid``
    arguments will result in process permissions not to be changed.

    NOTE: It would be possible to call daemonize_lite() method from within this
    method, howewer for readability purposes and to maintain correct ordering
    of the daemonization steps I decided against coding best practices and kept
    two separate methods with similar contents. It will be necessary to update
    both when making any improvements, however I do not expect them to change
    much and often, if ever.

    :param str chroot_dir: Name of the chroot directory (may be ``None``).
    :param str work_dir: Name of the work directory (may be ``None``).
    :param int umask: Umask as octal number (eg. ``0o002`` or ``0o022``, may be ``None``).
    :param int uid: User ID to which to drop the permissions (may be ``None``).
    :param int gid: Group ID to which to drop the permissions (may be ``None``).
    :param str pid_file: Full path to the PID file (may be ``None``).
    :param list files_preserve: List of file handles to preserve from closing (may be ``None``).
    :param dict signals: Desired signals to be handled as keys and their appropriate handlers as values (may be ``None``).
    """

    # Setup directories, limits, users, etc.
    _setup_fs(chroot_dir, work_dir, umask)
    _setup_perms(uid, gid)

    # Doublefork and split session to fully detach from current terminal.
    if os.fork()>0:
        os._exit(0)  # pylint: disable=locally-disabled,protected-access
    os.setsid()
    if os.fork()>0:
        os._exit(0)  # pylint: disable=locally-disabled,protected-access

    # Setup signal handlers.
    _setup_sh(signals)

    # Close all open file descriptors, except excluded files.
    #if files_preserve is None:
    #    files_preserve = []
    #descr_preserve = set(f.fileno() for f in files_preserve)
    #maxfd = resource.getrlimit(resource.RLIMIT_NOFILE)[1]
    #if maxfd==resource.RLIM_INFINITY:
    #    maxfd = 65535
    #for fd in range(maxfd, 3, -1):  # 3 means omit stdin, stdout, stderr
    #    if fd not in descr_preserve:
    #        try:
    #            os.close(fd)
    #        except Exception:
    #            pass

    # Redirect stdin, stdout, stderr to /dev/null.
    devnull = os.open(os.devnull, os.O_RDWR)
    for fdn in range(3):
        os.dup2(devnull, fdn)

    # Write PID into PID file.
    return _setup_pf(pid_file)


#-------------------------------------------------------------------------------

#
# Perform the demonstration.
#
if __name__ == "__main__":

    def hnd_sig_hup(signum, frame):  # pylint: disable=locally-disabled,unused-argument
        """Bogus handler for signal HUP for demonstration purposes."""
        print("HANDLER CALLBACK: Received signal HUP ({})".format(signum))

    def hnd_sig_usr1(signum, frame):  # pylint: disable=locally-disabled,unused-argument
        """Bogus handler for signal USR1 for demonstration purposes."""
        print("HANDLER CALLBACK: Received signal USR1 ({})".format(signum))

    def hnd_sig_usr2(signum, frame):  # pylint: disable=locally-disabled,unused-argument
        """Bogus handler for signal USR2 for demonstration purposes."""
        print("HANDLER CALLBACK: Received signal USR2 ({})".format(signum))

    (PIDV, PIDF) = daemonize_lite(
        work_dir = "/tmp",
        pid_file = "/tmp/demo.pyzenkit.daemonizer.pid",
        umask    = 0o022,
        signals  = {
            signal.SIGHUP:  hnd_sig_hup,
            signal.SIGUSR1: hnd_sig_usr1,
            signal.SIGUSR2: hnd_sig_usr2,
        }
    )

    print("Lite daemonization complete:")
    print("* PID:             '{}'".format(PIDV))
    print("* PID file:        '{}'".format(PIDF))
    print("* CWD:             '{}'".format(os.getcwd()))
    print("* PID in PID file: '{}'".format(read_pid(PIDF)))

    print("Checking signal handling:")
    os.kill(PIDV, signal.SIGHUP)
    os.kill(PIDV, signal.SIGUSR1)
    os.kill(PIDV, signal.SIGUSR2)
    print("Checking signal handling, read PID from PID file:")
    os.kill(read_pid(PIDF), signal.SIGHUP)
    os.kill(read_pid(PIDF), signal.SIGUSR1)
    os.kill(read_pid(PIDF), signal.SIGUSR2)
