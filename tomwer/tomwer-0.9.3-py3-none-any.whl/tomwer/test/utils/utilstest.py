# coding: utf-8
#
#    Copyright (C) 2012-2016 European Synchrotron Radiation Facility, Grenoble, France
#
#    Principal author:       Jérôme Kieffer (Jerome.Kieffer@ESRF.eu)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
"bunch of utility function/static classes to handle testing environment"

__author__ = "Jérôme Kieffer"
__contact__ = "jerome.kieffer@esrf.eu"
__license__ = "MIT"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "24/01/2018"

import os
import sys
import threading
import unittest
import logging
import shutil
import tempfile
import getpass


from argparse import ArgumentParser
from silx.resources import ExternalResources

PACKAGE = "pyFAI"
DATA_KEY = "PYFAI_DATA"

logger = logging.getLogger(__name__)

TEST_HOME = os.path.dirname(os.path.abspath(__file__))


def copy(infile, outfile):
    "link or copy file according to the OS"
    if "link" in dir(os):
        os.link(infile, outfile)
    else:
        shutil.copy(infile, outfile)


class TestContext(object):
    """
    Class providing useful stuff for preparing tests.
    """

    def __init__(self):
        self.options = None
        self.timeout = 60  # timeout in seconds for downloading images
        # url_base = "http://forge.epn-campus.eu/attachments/download"
        self.url_base = "http://ftp.edna-site.org/pyFAI/testimages"
        self.resources = ExternalResources(
            PACKAGE, timeout=self.timeout, env_key=DATA_KEY, url_base=self.url_base
        )
        self.sem = threading.Semaphore()
        self.recompiled = False
        self.reloaded = False
        self.name = PACKAGE
        self.script_dir = None
        self.installed = False

        self.download_images = self.resources.download_all
        self.getimage = self.resources.getfile
        self.low_mem = bool(os.environ.get("PYFAI_LOW_MEM"))
        self.opencl = bool(os.environ.get("PYFAI_OPENCL", True))

        self._tempdir = None

    def deep_reload(self):
        self.pyFAI = __import__(self.name)
        logger.info("%s loaded from %s", self.name, self.pyFAI.__file__)
        sys.modules[self.name] = self.pyFAI
        self.reloaded = True
        import pyFAI.utils.decorators

        pyFAI.utils.decorators.depreclog.setLevel(logging.ERROR)
        return self.pyFAI

    def forceBuild(self, remove_first=True):
        """
        Force the recompilation of pyFAI

        Nonesense, kept for legacy reasons
        """
        return

    def get_options(self):
        """
        Parse the command line to analyse options ... returns options
        """
        if self.options is None:
            parser = ArgumentParser(usage="Tests for %s" % self.name)
            parser.add_argument(
                "-d",
                "--debug",
                dest="debug",
                help="run in debugging mode",
                default=False,
                action="store_true",
            )
            parser.add_argument(
                "-i",
                "--info",
                dest="info",
                help="run in more verbose mode ",
                default=False,
                action="store_true",
            )
            parser.add_argument(
                "-f",
                "--force",
                dest="force",
                help="force the build of the library",
                default=False,
                action="store_true",
            )
            parser.add_argument(
                "-r",
                "--really-force",
                dest="remove",
                help="remove existing build and force the build of the library",
                default=False,
                action="store_true",
            )
            parser.add_argument(dest="args", type=str, nargs="*")
            self.options = parser.parse_args([])
        return self.options

    def get_test_env(self):
        """
        Returns an associated environment with a working project.
        """
        env = dict((str(k), str(v)) for k, v in os.environ.items())
        env["PYTHONPATH"] = os.pathsep.join(sys.path)
        return env

    def script_path(self, script_name, module_name):
        """Returns the script path according to it's location"""
        if self.installed:
            script = self.get_installed_script_path(script_name)
        else:
            import importlib

            module = importlib.import_module(module_name)
            script = module.__file__
        return script

    def get_installed_script_path(self, script):
        """
        Returns the path of the executable and the associated environment

        In Windows, it checks availability of script using .py .bat, and .exe
        file extensions.
        """
        if sys.platform == "win32":
            available_extensions = [".py", ".bat", ".exe"]
        else:
            available_extensions = [""]

        paths = os.environ.get("PATH", "").split(os.pathsep)
        for base in paths:
            # clean up extra quotes from paths
            if base.startswith('"') and base.endswith('"'):
                base = base[1:-1]
            for file_extension in available_extensions:
                script_path = os.path.join(base, script + file_extension)
                print(script_path)
                if os.path.exists(script_path):
                    # script found
                    return script_path
        # script not found
        logger.warning("Script '%s' not found in paths: %s", script, ":".join(paths))
        script_path = script
        return script_path

    def _initialize_tmpdir(self):
        """Initialize the temporary directory"""
        if not self._tempdir:
            with self.sem:
                if not self._tempdir:
                    self._tempdir = tempfile.mkdtemp(
                        "_" + getpass.getuser(), self.name + "_"
                    )

    @property
    def tempdir(self):
        if not self._tempdir:
            self._initialize_tmpdir()
        return self._tempdir

    def clean_up(self):
        """Removes the temporary directory (and all its content !)"""
        with self.sem:
            if not self._tempdir:
                return
            if not os.path.isdir(self._tempdir):
                return
            for root, dirs, files in os.walk(self._tempdir, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
            os.rmdir(self._tempdir)
            self._tempdir = None


UtilsTest = TestContext()
"""Singleton containing util context of whole the tests"""


class ParametricTestCase(unittest.TestCase):
    pass
