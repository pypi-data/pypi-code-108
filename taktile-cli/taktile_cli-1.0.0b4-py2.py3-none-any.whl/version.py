import sys
import xmlrpc.client as xmlrpclib
from distutils.version import StrictVersion
from platform import system

from tktl import __version__
from tktl.core.exceptions import TimeoutError
from tktl.core.loggers import LOG


class PackageNotFoundError(Exception):
    pass


class VersionChecker(object):
    def is_up_to_date(self, module_name, current_version):
        version_in_repository = self.get_version_from_repository(module_name)

        up_to_date = StrictVersion(current_version) >= StrictVersion(
            version_in_repository
        )
        return up_to_date, version_in_repository

    @staticmethod
    def get_version_from_repository(
        module_name, repository_url="http://pypi.python.org/pypi"
    ):
        pypi = xmlrpclib.ServerProxy(repository_url)
        versions = pypi.package_releases(module_name)
        if not versions:
            raise PackageNotFoundError("Package {} not found".format(module_name))

        return versions[0]


class TaktileVersionChecker(object):
    @classmethod
    def look_for_new_version_with_timeout(cls):
        if not cls._should_check_version():
            return

        if not system() == "Linux":
            cls.look_for_new_version()
            return

        import signal

        def handler(signum, frame):
            raise TimeoutError

        signal.signal(signal.SIGALRM, handler)
        signal.alarm(1)

        try:
            cls.look_for_new_version()
        except TimeoutError:
            pass

        signal.alarm(0)

    @staticmethod
    def look_for_new_version():
        vc = VersionChecker()
        try:
            up_to_date, version_from_repository = vc.is_up_to_date(
                "taktile-cli", __version__
            )
        except Exception as e:
            LOG.error(e)
            return

        if not up_to_date:
            msg = f"""
Warning: this version of the Taktile CLI ({__version__}) is out of date.
Some functionality might not be supported until you upgrade.
Latest available version: {version_from_repository}\n
Run `pip install -U taktile-cli` to upgrade.
"""
            LOG.warning(msg)

    @staticmethod
    def _should_check_version():
        if not hasattr(sys.stdin, "isatty"):
            return False
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            return False

        return True
