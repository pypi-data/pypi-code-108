# -*- coding: future_fstrings -*-
import shutil
import subprocess
from string import Template
import os
import sys
from abc import abstractmethod
from sumoappclient.common.logger import get_logger

from sumoappclient.common.utils import read_yaml_file


class PkgGenerator(object):

    RESOURCE_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), "resources")

    def __init__(self, configpath, python_cmd="python"):
        self.base_config, self.deploy_config = self.get_config(configpath)
        self.log = get_logger(__name__, **self.base_config['Logging'])
        self.project_dir = os.path.dirname(os.path.dirname(os.path.abspath(os.path.expanduser(configpath))))
        self.PYTHON_CMD = python_cmd
        self.PIP_CMD = "pip3" if python_cmd.endswith("python3") else "pip"
        self.setup_env()

    @abstractmethod
    def setup_env(self, *args, **kwargs):
        raise NotImplementedError()

    def get_config(self, configpath):
        collection_config = read_yaml_file(configpath)
        deploy_metadata = collection_config["DeployMetaData"]
        deploy_config = {
            "APPNAME": deploy_metadata["APPNAME"],
            "PACKAGENAME": deploy_metadata["PACKAGENAME"],
            "SRC_FOLDER_NAME": deploy_metadata["SRC_FOLDER_NAME"],
            "COLLECTION_CONFIG": os.path.basename(configpath),
            "ENABLE_LAYER": deploy_metadata.get("ENABLE_LAYER", False),
            "APPNAME_SINGLE": deploy_metadata["APPNAME"].replace(" ", '').replace("_", "")
        }

        return collection_config, deploy_config

    def remove_unwanted_files(self, PROJECT_DIR):
        self.log.debug("removing build directories")

        for dirname in ["target"]:
            dirpath = os.path.join(PROJECT_DIR, dirname)
            if os.path.isdir(dirpath):
                shutil.rmtree(dirpath)

        self.log.debug("removing pyc/pycache files")
        for dirpath, dirnames, filenames in os.walk(PROJECT_DIR):

            for file in filenames:
                if file.endswith("pyc") or file.endswith(".db"):
                    os.remove(os.path.join(dirpath, file))
            for dirname in dirnames:
                if dirname.startswith("__pycache__"):
                    shutil.rmtree(os.path.join(dirpath, dirname))

        self.log.debug("removing zip/db files")

    def generate_file(self, basefilepath, params, target_filepath):
        with open(basefilepath) as fin:
            body = fin.read()
        sam_template = Template(body)
        sam_body = sam_template.safe_substitute(**params)
        with open(target_filepath, "w") as fout:
            fout.write(sam_body)

    def _run(self, command, input=None, check=False, **kwargs):
        if sys.version_info >= (3, 5):
            return subprocess.run(command, capture_output=True)
        if input is not None:
            if 'stdin' in kwargs:
                raise ValueError('stdin and input arguments may not both be used.')
            kwargs['stdin'] = subprocess.PIPE

        process = subprocess.Popen(command, **kwargs)
        try:
            stdout, stderr = process.communicate(input)
        except:
            process.kill()
            process.wait()
            raise
        retcode = process.poll()
        if check and retcode:
            raise subprocess.CalledProcessError(
                retcode, process.args, output=stdout, stderr=stderr)
        return retcode, stdout, stderr

    def run_command(self, cmdargs):
        self.log.debug(f"Running cmd: {' '.join(cmdargs)}")
        resp = self._run(cmdargs)
        if resp.returncode != 0 and cmdargs[0] != "check-manifest":
            raise Exception("Error in run command %s cmd: %s" % (resp, cmdargs))
        return resp

