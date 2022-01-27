from johnnydep.lib import JohnnyDist
from sys import argv
from inspyre_toolbox.syntactic_sweets import suppress_stdout


class Version(object):

    class UpdateAvail(object):
        def __init__(self, avail_version):
            self.available_version = avail_version

    def __init__(self):

        self.prog_name = 'IP-Reveal-Headless'

        self.dist = None

        self.outdated = None
        self.version_list = None
        self.stable_latest = None
        self.bleeding_latest = None
        self.current = None
        self.raw_args = argv
        self.debug_mode = None

        self.Update = None

    def __get_dist(self):
        self.dist = JohnnyDist(self.prog_name.lower())

        return self.dist

    def __repr__(self, full=False):
        if self.current is None:
            self.load_dist()
        if not full:
            returning = self.current
        else:
            returning = ''
            returning += self.prog_name + f' | {self.current}'
        if self.needs_update:
            returning += f' | Update Available ({self.Update.available_version})'

        return returning

    @property
    def latest(self):
        return self.dist.version_latest

    @property
    def needs_update(self):
        return bool(self.Update)

    def load_dist(self):
        self.dist = self.__get_dist()

        self.current = self.dist.version_installed
        self.bleeding_latest = self.dist.version_latest
        self.stable_latest = self.dist.version_latest_in_spec
        self.version_list = self.dist.versions_available
        self.outdated = self.needs_update

        if self.latest == self.current:
            self.Update = None
        else:
            self.Update = self.UpdateAvail(avail_version=self.current)


debug_mode = None


def in_debug_mode():
    global debug_mode
    cli_args = argv

    if debug_mode is None:
        found_match = None
        for arg in cli_args:
            if arg in ['-l', '--log-level']:
                next_spot = cli_args.index(arg) + 1
                if cli_args[next_spot].lower() == 'debug':
                    found_match = True

        debug_mode = bool(found_match)

    return debug_mode


if not in_debug_mode():
    with suppress_stdout():
        VERSION = Version()
        VERSION.load_dist()
else:
    VERSION = Version()
    VERSION.load_dist()
