# Copyright 2009, 2010 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

# Authors: Daniel Silverstone <daniel.silverstone@canonical.com>
#      and Adam Conrad <adam.conrad@canonical.com>

# The basic builder implementation.

from __future__ import print_function

__metaclass__ = type

from functools import partial
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile

import apt
import six
from six.moves.urllib.request import (
    build_opener,
    HTTPBasicAuthHandler,
    HTTPPasswordMgrWithDefaultRealm,
    urlopen,
    )
from six.moves.xmlrpc_client import Binary
from twisted.internet import protocol
from twisted.internet import reactor as default_reactor
from twisted.internet import process
from twisted.python import log
from twisted.web import xmlrpc

from lpbuildd.target.backend import make_backend
from lpbuildd.util import shell_escape


devnull = open("/dev/null", "r")


def _sanitizeURLs(bytes_seq):
    """A generator that deletes URL passwords from a bytes sequence.

    This generator removes user/password data from URLs if embedded
    in the latter as follows: scheme://user:passwd@netloc/path.

    :param bytes_seq: A sequence of byte strings (that may contain URLs).
    :return: A (sanitized) line stripped of authentication credentials.
    """
    # This regular expression will be used to remove authentication
    # credentials from URLs.
    password_re = re.compile(br'://([^:]*:[^@]+@)(\S+)')
    # Builder proxy passwords are UUIDs.
    proxy_auth_re = re.compile(br',proxyauth=[^:]+:[A-Za-z0-9-]+')

    for line in bytes_seq:
        sanitized_line = password_re.sub(br'://\2', line)
        sanitized_line = proxy_auth_re.sub(b'', sanitized_line)
        yield sanitized_line


# XXX cprov 2005-06-28:
# RunCapture can be replaced with a call to
#
#   twisted.internet.utils.getProcessOutputAndValue
#
# when we start using Twisted 2.0.
class RunCapture(protocol.ProcessProtocol):
    """Run a command and capture its output to a builder's log."""

    def __init__(self, builder, callback, stdin=None):
        self.builder = builder
        self.notify = callback
        self.stdin = stdin
        self.builderFailCall = None
        self.ignore = False

    def connectionMade(self):
        """Write any stdin data."""
        if self.stdin is not None:
            self.transport.write(self.stdin)
            self.transport.closeStdin()

    def outReceived(self, data):
        """Pass on stdout data to the log."""
        self.builder.log(data)

    def errReceived(self, data):
        """Pass on stderr data to the log.

        With a bit of luck we won't interleave horribly."""
        self.builder.log(data)

    def processEnded(self, statusobject):
        """This method is called when a child process got terminated.

        Two actions are required at this point: eliminate pending calls to
        "builderFail", and invoke the programmed notification callback.  The
        notification callback must be invoked last.
        """
        if self.ignore:
            # The build manager no longer cares about this process.
            return

        # Since the process terminated, we don't need to fail the builder.
        if self.builderFailCall and self.builderFailCall.active():
            self.builderFailCall.cancel()

        # notify the builder, it'll perform the required actions
        if self.notify is not None:
            self.notify(statusobject.value.exitCode)


def get_build_path(home, build_id, *extra):
    """Generate a path within the build directory.

    :param home: the user's home directory.
    :param build_id: the build id to use.
    :param extra: the extra path segments within the build directory.
    :return: the generated path.
    """
    return os.path.join(home, "build-" + build_id, *extra)


class BuildManager(object):
    """Build manager abstract parent."""

    backend_name = "chroot"

    def __init__(self, builder, buildid, reactor=None):
        """Create a BuildManager.

        :param builder: A `Builder`.
        :param buildid: Identifying string for this build.
        """
        object.__init__(self)
        self._buildid = buildid
        self._builder = builder
        if reactor is None:
            reactor = default_reactor
        self._reactor = reactor
        self._sharepath = builder._config.get("builder", "sharepath")
        self._bin = os.path.join(self._sharepath, "bin")
        self._preppath = os.path.join(self._bin, "builder-prep")
        self._intargetpath = os.path.join(self._bin, "in-target")
        self._subprocess = None
        self._reaped_states = set()
        self.is_archive_private = False
        self.home = os.environ['HOME']
        self.abort_timeout = 120
        self.status_path = get_build_path(self.home, self._buildid, "status")
        self._final_extra_status = None

    @property
    def needs_sanitized_logs(self):
        return self.is_archive_private

    def runSubProcess(self, command, args, iterate=None, stdin=None, env=None):
        """Run a subprocess capturing the results in the log."""
        if iterate is None:
            iterate = self.iterate
        self._subprocess = RunCapture(self._builder, iterate, stdin=stdin)
        text_args = [
            arg.decode("UTF-8", "replace") if isinstance(arg, bytes) else arg
            for arg in args[1:]]
        self._builder.log("RUN: %s %s\n" % (
            command, " ".join(shell_escape(arg) for arg in text_args)))
        childfds = {
            0: devnull.fileno() if stdin is None else "w",
            1: "r",
            2: "r",
            }
        self._reactor.spawnProcess(
            self._subprocess, command, args, env=env,
            path=self.home, childFDs=childfds)

    def runTargetSubProcess(self, command, *args, **kwargs):
        """Run a subprocess that operates on the target environment."""
        base_args = [
            "in-target",
            command,
            "--backend=%s" % self.backend_name,
            "--series=%s" % self.series,
            "--arch=%s" % self.arch_tag,
            self._buildid,
            ]
        self.runSubProcess(
            self._intargetpath, base_args + list(args), **kwargs)

    def doUnpack(self):
        """Unpack the build chroot."""
        self.runTargetSubProcess(
            "unpack-chroot", "--image-type", self.image_type,
            self._chroottarfile)

    def doReapProcesses(self, state, notify=True):
        """Reap any processes left lying around in the chroot."""
        if state is not None and state in self._reaped_states:
            # We've already reaped this state.  To avoid a loop, proceed
            # immediately to the next iterator.
            self._builder.log("Already reaped from state %s...\n" % state)
            if notify:
                self.iterateReap(state, 0)
        else:
            if state is not None:
                self._reaped_states.add(state)
            if notify:
                iterate = partial(self.iterateReap, state)
            else:
                def iterate(success):
                    pass
            self.runTargetSubProcess("scan-for-processes", iterate=iterate)

    def doCleanup(self):
        """Remove the build tree etc."""
        # Fetch a final snapshot of manager-specific extra status.
        self._final_extra_status = self.status()

        if not self.fast_cleanup:
            self.runTargetSubProcess("remove-build")

        # Sanitize the URLs in the buildlog file if this is a build
        # in a private archive.
        if self.needs_sanitized_logs:
            self._builder.sanitizeBuildlog(self._builder.cachePath("buildlog"))

        if self.fast_cleanup:
            self.iterate(0, quiet=True)

    def doMounting(self):
        """Mount things in the chroot, e.g. proc."""
        self.runTargetSubProcess("mount-chroot")

    def doUnmounting(self):
        """Unmount the chroot."""
        if self.fast_cleanup:
            self.iterate(0, quiet=True)
        else:
            self.runTargetSubProcess("umount-chroot")

    def initiate(self, files, chroot, extra_args):
        """Initiate a build given the input files.

        Please note: the 'extra_args' dictionary may contain a boolean
        value keyed under the 'archive_private' string. If that value
        evaluates to True the build at hand is for a private archive.
        """
        if 'build_url' in extra_args:
            self._builder.log("%s\n" % extra_args['build_url'])

        os.mkdir(get_build_path(self.home, self._buildid))
        for f in files:
            os.symlink(self._builder.cachePath(files[f]),
                       get_build_path(self.home, self._buildid, f))
        self._chroottarfile = self._builder.cachePath(chroot)

        self.image_type = extra_args.get('image_type', 'chroot')
        self.series = extra_args['series']
        self.arch_tag = extra_args.get('arch_tag', self._builder.getArch())
        self.fast_cleanup = extra_args.get('fast_cleanup', False)

        # Check whether this is a build in a private archive and
        # whether the URLs in the buildlog file should be sanitized
        # so that they do not contain any embedded authentication
        # credentials.
        if extra_args.get('archive_private'):
            self.is_archive_private = True

        self.backend = make_backend(
            self.backend_name, self._buildid,
            series=self.series, arch=self.arch_tag)

        self.runSubProcess(self._preppath, ["builder-prep"])

    def status(self):
        """Return extra status for this build manager, as a dictionary.

        This may be used to return manager-specific information from the
        XML-RPC status call.
        """
        if self._final_extra_status is not None:
            return self._final_extra_status
        try:
            with open(self.status_path) as status_file:
                return json.load(status_file)
        except IOError:
            pass
        except Exception as e:
            print(
                "Error deserialising extra status file: %s" % e,
                file=sys.stderr)
        return {}

    def iterate(self, success, quiet=False):
        """Perform an iteration of the builder.

        The BuildManager tends to work by invoking several
        subprocesses in order. the iterate method is called by the
        object created by runSubProcess to gather the results of the
        sub process.
        """
        raise NotImplementedError("BuildManager should be subclassed to be "
                                  "used")

    def iterateReap(self, state, success):
        """Perform an iteration of the builder following subprocess reaping.

        Subprocess reaping is special, typically occurring at several
        positions in a build manager's state machine.  We therefore keep
        track of the state being reaped so that we can select the
        appropriate next state.
        """
        raise NotImplementedError("BuildManager should be subclassed to be "
                                  "used")

    def abortReap(self):
        """Abort by killing all processes in the chroot, as hard as we can.

        We expect this to result in the main build process exiting non-zero
        and giving us some useful logs.

        This may be overridden in subclasses so that they can perform their
        own state machine management.
        """
        self.doReapProcesses(None, notify=False)

    def abort(self):
        """Abort the build by killing the subprocess."""
        if self.alreadyfailed or self._subprocess is None:
            return
        else:
            self.alreadyfailed = True
        primary_subprocess = self._subprocess
        self.abortReap()
        # In extreme cases the build may be hung too badly for
        # scan-for-processes to manage to kill it (blocked on I/O,
        # forkbombing test suite, etc.).  In this case, fail the builder and
        # let an admin sort it out.
        self._subprocess.builderFailCall = self._reactor.callLater(
            self.abort_timeout, self.builderFail,
            "Failed to kill all processes.", primary_subprocess)

    def builderFail(self, reason, primary_subprocess):
        """Mark the builder as failed."""
        self._builder.log("ABORTING: %s\n" % reason)
        self._subprocess.builderFailCall = None
        self._builder.builderFail()
        self.alreadyfailed = True
        # If we failed to kill all processes in the chroot, then the primary
        # subprocess (i.e. the one running immediately before
        # doReapProcesses was called) may not have exited.  Kill it so that
        # we can proceed.
        try:
            primary_subprocess.transport.signalProcess('KILL')
        except process.ProcessExitedAlready:
            self._builder.log("ABORTING: Process Exited Already\n")
        primary_subprocess.transport.loseConnection()
        # Leave the reaper running, but disconnect it from our state
        # machine.  Perhaps an admin can make something of it, and in any
        # case scan-for-processes elevates itself to root so it's awkward to
        # kill it.
        self._subprocess.ignore = True
        self._subprocess.transport.loseConnection()

    def addWaitingFileFromBackend(self, path, name=None):
        fetched_dir = tempfile.mkdtemp()
        try:
            fetched_path = os.path.join(fetched_dir, os.path.basename(path))
            self.backend.copy_out(path, fetched_path)
            self._builder.addWaitingFile(fetched_path, name=name)
        finally:
            shutil.rmtree(fetched_dir)


class BuilderStatus:
    """Status values for the builder."""

    IDLE = "BuilderStatus.IDLE"
    BUILDING = "BuilderStatus.BUILDING"
    WAITING = "BuilderStatus.WAITING"
    ABORTING = "BuilderStatus.ABORTING"

    UNKNOWNSUM = "BuilderStatus.UNKNOWNSUM"
    UNKNOWNBUILDER = "BuilderStatus.UNKNOWNBUILDER"


class BuildStatus:
    """Status values for builds themselves."""

    OK = "BuildStatus.OK"
    DEPFAIL = "BuildStatus.DEPFAIL"
    GIVENBACK = "BuildStatus.GIVENBACK"
    PACKAGEFAIL = "BuildStatus.PACKAGEFAIL"
    CHROOTFAIL = "BuildStatus.CHROOTFAIL"
    BUILDERFAIL = "BuildStatus.BUILDERFAIL"
    ABORTED = "BuildStatus.ABORTED"


class Builder(object):
    """The core of a builder."""

    def __init__(self, config):
        object.__init__(self)
        self._config = config
        self.builderstatus = BuilderStatus.IDLE
        self._cachepath = self._config.get("builder", "filecache")
        self.buildstatus = BuildStatus.OK
        self.waitingfiles = {}
        self.builddependencies = ""
        self._log = None
        self.manager = None

        if not os.path.isdir(self._cachepath):
            raise ValueError("FileCache path is not a dir")

    def getArch(self):
        """Return the Architecture tag for the builder."""
        return self._config.get("builder", "architecturetag")

    def cachePath(self, file):
        """Return the path in the cache of the file specified."""
        return os.path.join(self._cachepath, file)

    def setupAuthHandler(self, url, username, password):
        """Set up a BasicAuthHandler to open the url.

        :param url: The URL that needs authenticating.
        :param username: The username for authentication.
        :param password: The password for authentication.
        :return: The OpenerDirector instance.

        This helper installs an HTTPBasicAuthHandler that will deal with any
        HTTP basic authentication required when opening the URL.
        """
        password_mgr = HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, url, username, password)
        handler = HTTPBasicAuthHandler(password_mgr)
        opener = build_opener(handler)
        return opener

    def ensurePresent(self, sha1sum, url=None, username=None, password=None):
        """Ensure we have the file with the checksum specified.

        Optionally you can provide the librarian URL and
        the builder will fetch the file if it doesn't have it.
        Return a tuple containing: (<present>, <info>)
        """
        extra_info = 'No URL'
        cachefile = self.cachePath(sha1sum)
        if url is not None:
            extra_info = 'Cache'
            if not os.path.exists(cachefile):
                self.log('Fetching %s by url %s' % (sha1sum, url))
                if username:
                    opener = self.setupAuthHandler(
                        url, username, password).open
                else:
                    opener = urlopen
                try:
                    f = opener(url)
                # Don't change this to URLError without thoroughly
                # testing for regressions. For now, just suppress
                # the PyLint warnings.
                # pylint: disable-msg=W0703
                except Exception as info:
                    extra_info = 'Error accessing Librarian: %s' % info
                    self.log(extra_info)
                else:
                    of = open(cachefile + '.tmp', "wb")
                    # Upped for great justice to 256k
                    check_sum = hashlib.sha1()
                    for chunk in iter(lambda: f.read(256*1024), b''):
                        of.write(chunk)
                        check_sum.update(chunk)
                    of.close()
                    f.close()
                    extra_info = 'Download'
                    if check_sum.hexdigest() != sha1sum:
                        os.remove(cachefile + '.tmp')
                        extra_info = "Digests did not match, removing again!"
                    else:
                        os.rename(cachefile + '.tmp', cachefile)
                    self.log(extra_info)
        return (os.path.exists(cachefile), extra_info)

    def storeFile(self, path):
        """Store the content of the provided path in the file cache."""
        f = open(path, "rb")
        tmppath = self.cachePath("storeFile.tmp")
        of = open(tmppath, "wb")
        try:
            sha1 = hashlib.sha1()
            for chunk in iter(lambda: f.read(256*1024), b''):
                sha1.update(chunk)
                of.write(chunk)
            sha1sum = sha1.hexdigest()
        finally:
            of.close()
            f.close()
        present, info = self.ensurePresent(sha1sum)
        if present:
            os.unlink(tmppath)
            return sha1sum
        os.rename(tmppath, self.cachePath(sha1sum))
        return sha1sum

    def addWaitingFile(self, path, name=None):
        """Add a file to the cache and store its details for reporting."""
        if name is None:
            name = os.path.basename(path)
        self.waitingfiles[name] = self.storeFile(path)

    def abort(self):
        """Abort the current build."""
        # XXX: dsilvers: 2005-01-21: Current abort mechanism doesn't wait
        # for abort to complete. This is potentially an issue in a heavy
        # load situation.
        if self.builderstatus == BuilderStatus.ABORTING:
            # This might happen if the master side restarts in the middle of
            # an abort cycle.
            self.log("Builder already ABORTING when asked to abort")
            return
        if self.builderstatus != BuilderStatus.BUILDING:
            # XXX: Should raise a known Fault so that the client can make
            # useful decisions about the error!
            raise ValueError("Builder is not BUILDING when asked to abort")
        self.manager.abort()
        self.builderstatus = BuilderStatus.ABORTING

    def clean(self):
        """Clean up pending files and reset the internal build state."""
        if self.builderstatus != BuilderStatus.WAITING:
            raise ValueError('Builder is not WAITING when asked to clean')
        for f in set(self.waitingfiles.values()):
            os.remove(self.cachePath(f))
        self.builderstatus = BuilderStatus.IDLE
        if self._log is not None:
            self._log.close()
            os.remove(self.cachePath("buildlog"))
            self._log = None
        self.waitingfiles = {}
        self.builddependencies = ""
        self.manager = None
        self.buildstatus = BuildStatus.OK

    def log(self, data):
        """Write the provided data to the log."""
        if self._log is not None:
            data_bytes = (
                data if isinstance(data, bytes) else data.encode("UTF-8"))
            self._log.write(data_bytes)
            self._log.flush()
        data_text = (
            data if isinstance(data, six.text_type)
            else data.decode("UTF-8", "replace"))
        if six.PY3:
            data_str = data_text
        else:
            # Twisted's logger doesn't handle non-ASCII text very reliably
            # on Python 2.  This is just for debugging, so replace non-ASCII
            # characters with the corresponding \u escapes.  We need to go
            # to ridiculous lengths here to avoid (e.g.) replacing newlines
            # with "\n".
            data_str = re.sub(
                r"([^\x00-\x7f])",
                lambda match: "\\u%04x" % ord(match.group(0)),
                data_text).encode("UTF-8")
        if data_str.endswith("\n"):
            data_str = data_str[:-1]
        log.msg("Build log: " + data_str)

    def getLogTail(self):
        """Return the tail of the log.

        If the buildlog is not yet opened for writing (self._log is None),
        return an empty bytes object.

        It safely tries to open the 'buildlog', if it doesn't exist, due to
        job cleanup or buildlog sanitization race-conditions, it also returns
        an empty bytes object.

        When the 'buildlog' is present it returns up to 2 KiB bytes of the
        end of the file.

        The returned content will be 'sanitized', see `_sanitizeURLs` for
        further information.
        """
        if self._log is None:
            return b""

        rlog = None
        try:
            try:
                rlog = open(self.cachePath("buildlog"), "rb")
            except IOError:
                ret = b""
            else:
                # We rely on good OS practices that keep the file handler
                # usable once it's opened. So, if open() is ok, a subsequent
                # seek/tell/read will be safe.
                rlog.seek(0, os.SEEK_END)
                count = rlog.tell()
                if count > 2048:
                    count = 2048
                rlog.seek(-count, os.SEEK_END)
                ret = rlog.read(count)
        finally:
            if rlog is not None:
                rlog.close()

        if self.manager.needs_sanitized_logs:
            # This is a build in a private archive. We need to scrub
            # the URLs contained in the buildlog excerpt in order to
            # avoid leaking passwords.
            log_lines = ret.splitlines()

            # Please note: we are throwing away the first line (of the
            # excerpt to be scrubbed) because it may be cut off thus
            # thwarting the detection of embedded passwords.
            clean_content_iter = _sanitizeURLs(log_lines[1:])
            ret = b'\n'.join(clean_content_iter)

        return ret

    def startBuild(self, manager):
        """Start a build with the provided BuildManager instance."""
        if self.builderstatus != BuilderStatus.IDLE:
            raise ValueError(
                "Builder is not IDLE when asked to start building")
        self.manager = manager
        self.builderstatus = BuilderStatus.BUILDING
        self.emptyLog()

    def emptyLog(self):
        """Empty the log and start again."""
        if self._log is not None:
            self._log.close()
        self._log = open(self.cachePath("buildlog"), "wb")

    def builderFail(self):
        """Cease building because the builder has a problem."""
        if self.builderstatus not in (BuilderStatus.BUILDING,
                                      BuilderStatus.ABORTING):
            raise ValueError(
                "Builder is not BUILDING|ABORTING when set to BUILDERFAIL")
        self.buildstatus = BuildStatus.BUILDERFAIL

    def chrootFail(self):
        """Cease building because the chroot could not be created or contained
        a set of package control files which couldn't upgrade themselves, or
        yet a lot of causes that imply the CHROOT is corrupted not the
        package.
        """
        if self.builderstatus != BuilderStatus.BUILDING:
            raise ValueError("Builder is not BUILDING when set to CHROOTFAIL")
        self.buildstatus = BuildStatus.CHROOTFAIL

    def buildFail(self):
        """Cease building because the package failed to build."""
        if self.builderstatus != BuilderStatus.BUILDING:
            raise ValueError("Builder is not BUILDING when set to PACKAGEFAIL")
        self.buildstatus = BuildStatus.PACKAGEFAIL

    def buildOK(self):
        """Having passed all possible failure states, mark a build as OK."""
        if self.builderstatus != BuilderStatus.BUILDING:
            raise ValueError("Builder is not BUILDING when set to OK")
        self.buildstatus = BuildStatus.OK

    def depFail(self, dependencies):
        """Cease building due to a dependency issue."""
        if self.builderstatus != BuilderStatus.BUILDING:
            raise ValueError("Builder is not BUILDING when set to DEPFAIL")
        self.buildstatus = BuildStatus.DEPFAIL
        self.builddependencies = dependencies

    def giveBack(self):
        """Give-back package due to a transient buildd/archive issue."""
        if self.builderstatus != BuilderStatus.BUILDING:
            raise ValueError("Builder is not BUILDING when set to GIVENBACK")
        self.buildstatus = BuildStatus.GIVENBACK

    def buildAborted(self):
        """Mark a build as aborted."""
        if self.builderstatus != BuilderStatus.ABORTING:
            raise ValueError("Builder is not ABORTING when set to ABORTED")
        if self.buildstatus != BuildStatus.BUILDERFAIL:
            self.buildstatus = BuildStatus.ABORTED

    def buildComplete(self):
        """Mark the build as complete and waiting interaction from the build
        daemon master.
        """
        if self.builderstatus == BuilderStatus.BUILDING:
            self.builderstatus = BuilderStatus.WAITING
        elif self.builderstatus == BuilderStatus.ABORTING:
            self.buildAborted()
            self.builderstatus = BuilderStatus.WAITING
        else:
            raise ValueError(
                "Builder is not BUILDING|ABORTING when told build is complete")

    def sanitizeBuildlog(self, log_path):
        """Removes passwords from buildlog URLs.

        Because none of the URLs to be processed are expected to span
        multiple lines and because build log files are potentially huge
        they will be processed line by line.

        :param log_path: The path to the buildlog file that is to be
            sanitized.
        :type log_path: ``str``
        """
        # First move the buildlog file that is to be sanitized out of
        # the way.
        unsanitized_path = self.cachePath(
            os.path.basename(log_path) + '.unsanitized')
        os.rename(log_path, unsanitized_path)

        # Open the unsanitized buildlog file for reading.
        unsanitized_file = open(unsanitized_path, 'rb')

        # Open the file that will hold the resulting, sanitized buildlog
        # content for writing.
        sanitized_file = None

        try:
            sanitized_file = open(log_path, 'wb')

            # Scrub the buildlog file line by line
            clean_content_iter = _sanitizeURLs(unsanitized_file)
            for line in clean_content_iter:
                sanitized_file.write(line)
        finally:
            # We're done with scrubbing, close the file handles.
            unsanitized_file.close()
            if sanitized_file is not None:
                sanitized_file.close()


class XMLRPCBuilder(xmlrpc.XMLRPC):
    """XMLRPC builder management interface."""

    def __init__(self, config):
        xmlrpc.XMLRPC.__init__(self, allowNone=True)
        # The V1.0 new-style protocol introduces string-style protocol
        # versions of the form 'MAJOR.MINOR', the protocol is '1.0' for now
        # implying the presence of /filecache/ /filecache/buildlog and
        # the reduced and optimised XMLRPC interface.
        self.protocolversion = '1.0'
        self.builder = Builder(config)
        self._managers = {}
        cache = apt.Cache()
        try:
            installed = cache["launchpad-buildd"].installed
            self._version = installed.version if installed else None
        except KeyError:
            self._version = None
        log.msg("Initialized")

    def registerManager(self, managerclass, managertag):
        self._managers[managertag] = managerclass

    def xmlrpc_echo(self, *args):
        """Echo the argument back."""
        return args

    def xmlrpc_info(self):
        """Return the protocol version and the manager methods supported."""
        return (self.protocolversion, self.builder.getArch(),
                list(self._managers))

    def xmlrpc_status(self):
        """Return the status of the build daemon, as a dictionary.

        Depending on the builder status we return differing amounts of data,
        but this always includes the builder status itself.
        """
        status = self.builder.builderstatus
        statusname = status.split('.')[-1]
        func = getattr(self, "status_" + statusname, None)
        if func is None:
            raise ValueError("Unknown status '%s'" % status)
        ret = {"builder_status": status}
        if self._version is not None:
            ret["builder_version"] = self._version
        ret.update(func())
        if self.builder.manager is not None:
            ret.update(self.builder.manager.status())
        return ret

    def status_IDLE(self):
        """Handler for xmlrpc_status IDLE."""
        return {}

    def status_BUILDING(self):
        """Handler for xmlrpc_status BUILDING.

        Returns the build id and up to one kilobyte of log tail.
        """
        tail = self.builder.getLogTail()
        return {"build_id": self.buildid, "logtail": Binary(tail)}

    def status_WAITING(self):
        """Handler for xmlrpc_status WAITING.

        Returns the build id and the set of files waiting to be returned
        unless the builder failed in which case we return the buildstatus
        and the build id but no file set.
        """
        ret = {
            "build_status": self.builder.buildstatus,
            "build_id": self.buildid,
            }
        if self.builder.buildstatus in (
                BuildStatus.OK, BuildStatus.PACKAGEFAIL, BuildStatus.DEPFAIL):
            ret["filemap"] = self.builder.waitingfiles
            ret["dependencies"] = self.builder.builddependencies
        return ret

    def status_ABORTING(self):
        """Handler for xmlrpc_status ABORTING.

        This state means the builder is performing the ABORT command and is
        not able to do anything else than answer its status, so returns the
        build id only.
        """
        return {"build_id": self.buildid}

    def xmlrpc_ensurepresent(self, sha1sum, url, username, password):
        """Attempt to ensure the given file is present."""
        return self.builder.ensurePresent(sha1sum, url, username, password)

    def xmlrpc_abort(self):
        """Abort the current build."""
        self.builder.abort()
        return BuilderStatus.ABORTING

    def xmlrpc_clean(self):
        """Clean up the waiting files and reset the builder's state."""
        self.builder.clean()
        return BuilderStatus.IDLE

    def xmlrpc_build(self, buildid, managertag, chrootsum, filemap, args):
        """Check if requested arguments are sane and initiate build procedure

        return a tuple containing: (<builder_status>, <info>)

        """
        # check requested manager
        if managertag not in self._managers:
            extra_info = "%s not in %r" % (managertag, list(self._managers))
            return (BuilderStatus.UNKNOWNBUILDER, extra_info)
        # check requested chroot availability
        chroot_present, info = self.builder.ensurePresent(chrootsum)
        if not chroot_present:
            extra_info = """CHROOTSUM -> %s
            ***** INFO *****
            %s
            ****************
            """ % (chrootsum, info)
            return (BuilderStatus.UNKNOWNSUM, extra_info)
        # check requested files availability
        for filesum in filemap.values():
            file_present, info = self.builder.ensurePresent(filesum)
            if not file_present:
                extra_info = """FILESUM -> %s
                ***** INFO *****
                %s
                ****************
                """ % (filesum, info)
                return (BuilderStatus.UNKNOWNSUM, extra_info)
        # check buildid sanity
        if buildid is None or buildid == "" or buildid == 0:
            raise ValueError(buildid)

        # builder is available, buildd is non empty,
        # filelist is consistent, chrootsum is available, let's initiate...
        self.buildid = buildid
        self.builder.startBuild(
            self._managers[managertag](self.builder, buildid))
        self.builder.manager.initiate(filemap, chrootsum, args)
        return (BuilderStatus.BUILDING, buildid)
