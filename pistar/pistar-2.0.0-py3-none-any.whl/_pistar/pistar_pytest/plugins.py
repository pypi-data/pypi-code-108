# -*- coding: utf-8 -*-
import os

from _pistar.pistar_pytest.collector import Collector


def pytest_addoption(parser):
    parser.getgroup("reporting").addoption(
        '--pistar_dir',
        action="store",
        dest="pistar_dir",
        metavar="DIR",
        default=None,
        help="Generate result data in the specified directory (may not exist)")


def pytest_configure(config):
    report_dir = config.option.pistar_dir

    if report_dir:
        report_dir = os.path.abspath(report_dir)
        collector = Collector(report_dir)
        config.pluginmanager.register(collector)
