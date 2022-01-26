# Copyright 2009-2019 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

# Authors: Daniel Silverstone <daniel.silverstone@canonical.com>
#      and Adam Conrad <adam.conrad@canonical.com>

__metaclass__ = type

import base64
import io
import os
import re
import signal

from six.moves.configparser import (
    NoOptionError,
    NoSectionError,
    )
from twisted.internet import (
    defer,
    threads,
    )
from twisted.python import log

from lpbuildd.builder import (
    BuildManager,
    get_build_path,
    )


class DebianBuildState:
    """States for the DebianBuildManager."""
    INIT = "INIT"
    UNPACK = "UNPACK"
    MOUNT = "MOUNT"
    SOURCES = "SOURCES"
    KEYS = "KEYS"
    UPDATE = "UPDATE"
    UMOUNT = "UMOUNT"
    CLEANUP = "CLEANUP"


class DebianBuildManager(BuildManager):
    """Base behaviour for Debian chrooted builds."""

    def __init__(self, builder, buildid, **kwargs):
        BuildManager.__init__(self, builder, buildid, **kwargs)
        self._cachepath = builder._config.get("builder", "filecache")
        self._state = DebianBuildState.INIT
        builder.emptyLog()
        self.alreadyfailed = False
        self._iterator = None

    @property
    def initial_build_state(self):
        raise NotImplementedError()

    def initiate(self, files, chroot, extra_args):
        """Initiate a build with a given set of files and chroot."""
        self.sources_list = extra_args.get('archives')
        self.trusted_keys = extra_args.get('trusted_keys')

        BuildManager.initiate(self, files, chroot, extra_args)

    def doSourcesList(self):
        """Override apt/sources.list.

        Mainly used for PPA builds.
        """
        args = []
        try:
            apt_proxy_url = self._builder._config.get("proxy", "apt")
            args.extend(["--apt-proxy-url", apt_proxy_url])
        except (NoSectionError, NoOptionError):
            pass
        args.extend(self.sources_list)
        self.runTargetSubProcess("override-sources-list", *args)

    def doTrustedKeys(self):
        """Add trusted keys."""
        trusted_keys = b"".join(
            base64.b64decode(key) for key in self.trusted_keys)
        self.runTargetSubProcess("add-trusted-keys", stdin=trusted_keys)

    def doUpdateChroot(self):
        """Perform the chroot upgrade."""
        self.runTargetSubProcess("update-debian-chroot")

    def doRunBuild(self):
        """Run the main build process.

        Subclasses must override this.
        """
        raise NotImplementedError()

    @staticmethod
    def _parseChangesFile(linesIter):
        """A generator that iterates over files listed in a changes file.

        :param linesIter: an iterable of lines in a changes file.
        """
        seenfiles = False
        for line in linesIter:
            if line.endswith("\n"):
                line = line[:-1]
            if not seenfiles and line.startswith("Files:"):
                seenfiles = True
            elif seenfiles:
                if not line.startswith(' '):
                    break
                filename = line.split(' ')[-1]
                yield filename

    def getChangesFilename(self):
        changes = self._dscfile[:-4] + "_" + self.arch_tag + ".changes"
        return get_build_path(self.home, self._buildid, changes)

    def gatherResults(self):
        """Gather the results of the build and add them to the file cache.

        The primary file we care about is the .changes file. We key from there.
        """
        path = self.getChangesFilename()
        self._builder.addWaitingFile(path)

        with io.open(path, "r", errors="replace") as chfile:
            for fn in self._parseChangesFile(chfile):
                self._builder.addWaitingFile(
                    get_build_path(self.home, self._buildid, fn))

    def deferGatherResults(self, reap=True):
        """Gather the results of the build in a thread."""
        # XXX cjwatson 2018-10-04: Refactor using inlineCallbacks once we're
        # on Twisted >= 18.7.0 (https://twistedmatrix.com/trac/ticket/4632).
        def failed_to_gather(failure):
            if failure.check(defer.CancelledError):
                if not self.alreadyfailed:
                    self._builder.log("Build cancelled unexpectedly!\n")
                    self._builder.buildFail()
            else:
                self._builder.log(
                    "Failed to gather results: %s\n" % failure.value)
                self._builder.buildFail()
            self.alreadyfailed = True

        def reap_processes(ignored):
            self.doReapProcesses(self._state)

        d = threads.deferToThread(self.gatherResults).addErrback(
            failed_to_gather)
        if reap:
            d.addCallback(reap_processes)
        return d

    @defer.inlineCallbacks
    def iterate(self, success, quiet=False):
        # When a Twisted ProcessControl class is killed by SIGTERM,
        # which we call 'build process aborted', 'None' is returned as
        # exit_code.
        if self.alreadyfailed and success == 0:
            # We may have been aborted in between subprocesses; pretend that
            # we were terminated by a signal, which is close enough.
            success = 128 + signal.SIGKILL
        if not quiet:
            log.msg("Iterating with success flag %s against stage %s"
                    % (success, self._state))
        func = getattr(self, "iterate_" + self._state, None)
        if func is None:
            raise ValueError("Unknown internal state " + self._state)
        self._iterator = func(success)
        yield self._iterator
        self._iterator = None

    def iterateReap(self, state, success):
        log.msg("Iterating with success flag %s against stage %s after "
                "reaping processes"
                % (success, state))
        func = getattr(self, "iterateReap_" + state, None)
        if func is None:
            raise ValueError("Unknown internal post-reap state " + state)
        func(success)

    def iterate_INIT(self, success):
        """Just finished initializing the build."""
        if success != 0:
            if not self.alreadyfailed:
                # The init failed, can't fathom why that would be...
                self._builder.builderFail()
                self.alreadyfailed = True
            self._state = DebianBuildState.CLEANUP
            self.doCleanup()
        else:
            self._state = DebianBuildState.UNPACK
            self.doUnpack()

    def iterate_UNPACK(self, success):
        """Just finished unpacking the tarball."""
        if success != 0:
            if not self.alreadyfailed:
                # The unpack failed for some reason...
                self._builder.chrootFail()
                self.alreadyfailed = True
            self._state = DebianBuildState.CLEANUP
            self.doCleanup()
        else:
            self._state = DebianBuildState.MOUNT
            self.doMounting()

    def iterate_MOUNT(self, success):
        """Just finished doing the mounts."""
        if success != 0:
            if not self.alreadyfailed:
                self._builder.chrootFail()
                self.alreadyfailed = True
            self._state = DebianBuildState.UMOUNT
            self.doUnmounting()
        else:
            if self.sources_list is not None:
                self._state = DebianBuildState.SOURCES
                self.doSourcesList()
            elif self.trusted_keys:
                self._state = DebianBuildState.KEYS
                self.doTrustedKeys()
            else:
                self._state = DebianBuildState.UPDATE
                self.doUpdateChroot()

    def searchLogContents(self, patterns_and_flags,
                          stop_patterns_and_flags=[]):
        """Search for any of a list of regex patterns in the build log.

        The build log is matched using a sliding window, which avoids having
        to read the whole file into memory at once but requires that matches
        be no longer than the chunk size (currently 256KiB).

        If any of the stop patterns are matched, the search stops
        immediately without reading the rest of the file.

        :return: A tuple of the regex pattern that matched and the match
            object, or (None, None).
        """
        chunk_size = 256 * 1024
        regexes = [
            re.compile(pattern.encode("UTF-8"), flags)
            for pattern, flags in patterns_and_flags]
        stop_regexes = [
            re.compile(pattern.encode("UTF-8"), flags)
            for pattern, flags in stop_patterns_and_flags]
        buildlog_path = os.path.join(self._cachepath, "buildlog")
        with open(buildlog_path, "rb") as buildlog:
            window = b""
            chunk = buildlog.read(chunk_size)
            while chunk:
                window += chunk
                for regex in regexes:
                    match = regex.search(window)
                    if match is not None:
                        return regex.pattern.decode("UTF-8"), match
                for regex in stop_regexes:
                    if regex.search(window) is not None:
                        return None, None
                if len(window) > chunk_size:
                    window = window[chunk_size:]
                chunk = buildlog.read(chunk_size)
        return None, None

    def iterate_SOURCES(self, success):
        """Just finished overwriting sources.list."""
        if success != 0:
            if not self.alreadyfailed:
                self._builder.chrootFail()
                self.alreadyfailed = True
            self.doReapProcesses(self._state)
        elif self.trusted_keys:
            self._state = DebianBuildState.KEYS
            self.doTrustedKeys()
        else:
            self._state = DebianBuildState.UPDATE
            self.doUpdateChroot()

    def iterateReap_SOURCES(self, success):
        """Just finished reaping after failure to overwrite sources.list."""
        self._state = DebianBuildState.UMOUNT
        self.doUnmounting()

    def iterate_KEYS(self, success):
        """Just finished adding trusted keys."""
        if success != 0:
            if not self.alreadyfailed:
                self._builder.chrootFail()
                self.alreadyfailed = True
            self.doReapProcesses(self._state)
        else:
            self._state = DebianBuildState.UPDATE
            self.doUpdateChroot()

    def iterateReap_KEYS(self, success):
        """Just finished reaping after failure to add trusted keys."""
        self._state = DebianBuildState.UMOUNT
        self.doUnmounting()

    def iterate_UPDATE(self, success):
        """Just finished updating the chroot."""
        if success != 0:
            if not self.alreadyfailed:
                self._builder.chrootFail()
                self.alreadyfailed = True
            self.doReapProcesses(self._state)
        else:
            self._state = self.initial_build_state
            self.doRunBuild()

    def iterateReap_UPDATE(self, success):
        """Just finished reaping after failure to update the chroot."""
        self._state = DebianBuildState.UMOUNT
        self.doUnmounting()

    def iterate_UMOUNT(self, success):
        """Just finished doing the unmounting."""
        if success != 0:
            if not self.alreadyfailed:
                self._builder.builderFail()
                self.alreadyfailed = True
        self._state = DebianBuildState.CLEANUP
        self.doCleanup()

    def iterate_CLEANUP(self, success):
        """Just finished the cleanup."""
        if success != 0:
            if not self.alreadyfailed:
                self._builder.builderFail()
                self.alreadyfailed = True
        else:
            # Successful clean
            if not self.alreadyfailed:
                self._builder.buildOK()
        self._builder.buildComplete()

    def abortReap(self):
        """Abort by killing all processes in the chroot, as hard as we can.

        Overridden here to handle state management.
        """
        self.doReapProcesses(self._state, notify=False)

    def abort(self):
        """See `BuildManager`."""
        super(DebianBuildManager, self).abort()
        if self._iterator is not None:
            self._iterator.cancel()
            self._iterator = None
