# -*- coding: future_fstrings -*-

import os
import shutil
import sys


if __name__ == "__main__":
    cur_dir = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    sys.path.insert(0, cur_dir)

from sumoappclient.common.utils import create_dir
from sumoappclient.pkggenerator.base import PkgGenerator


class OnPremPkgGen(PkgGenerator):

    def __init__(self, configpath, *args, **kwargs):
        super(OnPremPkgGen, self).__init__(configpath, *args, **kwargs)

    def setup_env(self):
        self.remove_unwanted_files(self.project_dir)
        target_dir = os.path.join(self.project_dir, "target")
        create_dir(target_dir)
        self.onprem_target_dir = os.path.join(target_dir, "onprem")
        self.log.info(f"creating onprem target directory {self.onprem_target_dir}")
        create_dir(self.onprem_target_dir)

    def build_package(self):
        os.chdir(self.project_dir)
        self.log.debug("changing to root dir: %s" % os.getcwd())
        self.log.info("generating build...")
        self.run_command([self.PYTHON_CMD, "setup.py", "sdist", "bdist_wheel"])
        self.run_command(["check-manifest"])
        eggfile = f'''{self.deploy_config['PACKAGENAME'].replace("-", "_")}.egg-info'''
        for filename in [eggfile, "build", "dist"]:
            if os.path.isdir(filename) or os.path.isfile(filename):
                shutil.move(filename, self.onprem_target_dir)

    def deploy_package(self):
        os.chdir(self.onprem_target_dir)
        self.log.info("deploying package to pypi: %s" % self.onprem_target_dir)
        self.run_command([self.PYTHON_CMD, "-m", "twine", "upload", "dist/*"])

    def deploy_package_test_repo(self):
        os.chdir(self.onprem_target_dir)
        self.log.info("deploying package to testpypi: %s" % self.onprem_target_dir)
        self.run_command([self.PYTHON_CMD, "-m", "twine", "upload", "dist/*", "--repository", "testpypi"])
        self.log.info("install using command: pip install --extra-index-url https://testpypi.python.org/pypi %s --no-cache-dir" % self.deploy_config['PACKAGENAME'])

    def get_wheel_file(self):
        whldir = os.path.join(self.onprem_target_dir, "dist")
        if os.path.isdir(whldir):
            for filename in os.listdir(whldir):
                if filename.endswith(".whl"):
                    return os.path.join(whldir, filename)

    def build_and_deploy(self, deploy=False):
        self.build_package()
        if deploy:
            if deploy == "prod":
                self.deploy_package()
            elif deploy == "test":
                self.deploy_package_test_repo()
            else:
                self.log.info("install using command: pip install %s" % self.get_wheel_file())


if __name__ == "__main__":
    deploy = False
    if len(sys.argv) > 1:
        configpath = sys.argv[1]
        if len(sys.argv) > 2:
            deploy = sys.argv[2]
    else:
        raise Exception("pass collection config path as param")
    OnPremPkgGen(configpath).build_and_deploy(deploy)

