from distutils.version import StrictVersion

from tktl import __version__
from tktl.version import TaktileVersionChecker, VersionChecker


def test_get_version(capsys):
    TaktileVersionChecker.look_for_new_version_with_timeout()
    out, err = capsys.readouterr()
    assert out == ""
    vc = VersionChecker()
    up_to_date, version_from_repository = vc.is_up_to_date("taktile-cli", __version__)
    if __version__[0:3] == version_from_repository[0:3]:
        assert up_to_date is True
        assert StrictVersion(__version__) >= StrictVersion(version_from_repository)
