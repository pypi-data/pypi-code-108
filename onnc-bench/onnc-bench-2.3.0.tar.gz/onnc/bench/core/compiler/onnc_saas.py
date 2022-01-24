from pathlib import Path
from typing import Dict, List, Any, Callable, Union, Set
from abc import abstractmethod
from pathlib import Path
import inspect
import os
import time
import re
import zipfile
from dataclasses import dataclass
import sys
import json

import requests
from loguru import logger

from onnc.bench.core.project import ProjectData
from onnc.bench.core.deployment import Deployment
from .builder import IBuilder
from ..dataset.dataset import Dataset
from ..model.model import Model
from .saas_config import URI_MAP, timeout, poll_interval
from ..modelpackage import ModelPackage
from onnc.bench.core.common import get_tmp_path
from . import Compilation

def spinning_cursor():
    while True:
        for cursor in '|/-\\':
            yield cursor


class SaaSResult:
    def __init__(self, http_res):
        self.success = None
        self.message = None
        self.http_status_code = None
        self.data: Dict = {}

        self.from_http_res(http_res)

    def __bool__(self):
        return True if self.success else False

    def from_http_res(self, http_res) -> None:
        self.http_status_code = http_res.status_code

        if http_res.status_code == requests.codes.ok:
            self.success = True
            self.message = ""
            try:
                self.data = http_res.json()
            except Exception:
                self.data = {}
        else:
            self.success = False
            self.message = http_res.json()["error"]["message"]
            self.data = http_res.json()


class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token):
        self.token = token
    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r


class ONNCSaaSBuilder(IBuilder):
    BUILDER_NAME = "ONNCSaaSBuilder"

    def __init__(self, protocal: str, url: str, port: int):
        self.base_url = f"{protocal}://{url}:{port}"
        self.auth_token = ""
        self._compilations: Dict[int, Compilation] = {}
        self._project_id: str = ""
        self._build_id: str = ""

    def _http_req(self, api: Union[Callable, List], *args, **kwargs):
        if type(api) == list:
            uri = URI_MAP[api[0]]["uri"].format(*api[1:])
            method = URI_MAP[api[0]]["method"]
        elif callable(api):
            uri = URI_MAP[api.__name__]["uri"]
            method = URI_MAP[api.__name__]["method"]

        if method == 'GET':
            return requests.get(f"{self.base_url}{uri}",
                                auth=BearerAuth(self.auth_token),
                                *args, **kwargs)
        elif method == 'POST':
            return requests.post(f"{self.base_url}{uri}",
                                 auth=BearerAuth(self.auth_token),
                                 *args, **kwargs)
        elif method == 'DELETE':
            return requests.delete(f"{self.base_url}{uri}",
                                   auth=BearerAuth(self.auth_token),
                                   *args, **kwargs)
        elif method == 'PATCH':
            return requests.patch(f"{self.base_url}{uri}",
                                  auth=BearerAuth(self.auth_token),
                                  *args, **kwargs)
        elif method == 'PUT':
            return requests.put(f"{self.base_url}{uri}",
                                auth=BearerAuth(self.auth_token),
                                *args, **kwargs)

    def saas_login(self, email: str, password: str) -> SaaSResult:
        data = {
            "email": email,
            "password": password
        }
        r = self._http_req(self.saas_login, json=data)
        if r.status_code == requests.codes.ok:
            self.auth_token = r.json()["token"]
            logger.info(f"Login successfully")
        else:
            logger.error(f"Login failed")

        return SaaSResult(r)

    def saas_verify_key(self, api_key) -> bool:
        pass

    def saas_create_project(self, name: str, info: Dict = {}) -> SaaSResult:
        data = {
            "name": name,
            "info": info
        }
        r = self._http_req(self.saas_create_project, json=data)
        if r.status_code == requests.codes.ok:
            self._project_id = r.json()["id"]
            logger.info(f"Project ID: {self._project_id}")

        return SaaSResult(r)

    def saas_get_project_id_by_name(self, project_name: str) -> SaaSResult:
        r = self._http_req(['saas_get_project_id_by_name', project_name])
        r_list = r.json()
        if len(r_list) > 0:
            self._project_id = r_list[0]["id"]
            logger.info(f"Project ID: {self._project_id}")

        return SaaSResult(r)

    def saas_upload_file(self, file_path: str) -> SaaSResult:
        files = {os.path.basename(file_path): open(file_path, 'rb')}

        r = self._http_req(self.saas_upload_file, files=files)

        return SaaSResult(r)

    def _saas_create_compilation(self, model_path, dataset_path,
                                params: Dict = {}):

        logger.info(f'Start to upload model: {model_path}')
        model_sr = self.saas_upload_file(model_path)  # type: ignore[arg-type]
        logger.info('The model was uploaded successfully')

        logger.info(f'Start to upload dataset: {dataset_path}')
        dataset_sr = self.saas_upload_file(dataset_path)  # type: ignore[arg-type]
        logger.info('The dataset was uploaded successfully')

        data = {
            "model": model_sr.data["files"][0]["url"],
            "modelSize": model_sr.data["files"][0]["size"],
            "calibration": dataset_sr.data["files"][0]["url"],
            "calibrationSize": dataset_sr.data["files"][0]["size"],
            "compilerParameters": params
        }

        return data

    def saas_create_build(self, project_id: str, saas_compilations: List,
                          device: str) -> SaaSResult:
        data = {
            # "userId": "0",
            "projectId": project_id,
            "boardId": device,
            "input": saas_compilations
        }

        r = self._http_req(self.saas_create_build, json=data)

        sr = SaaSResult(r)
        logger.debug(f"Build ID: {sr.data['id']}")

        return sr

    def saas_get_build_state(self, build_id: str) -> SaaSResult:
        """Get state code of a build.

        :returns:
            The state code of the build
        :rtype:
            str
        """
        r = self._http_req(['saas_get_build_state', build_id])

        return SaaSResult(r)

    def saas_download_deployment_package(self, file_id, dest: Path):
        r = self._http_req(['saas_download_deployment_package', file_id],
                           stream=True)

        r.raise_for_status()

        logger.debug(f"Download destination: {dest}")

        with open(dest, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)

        return SaaSResult(r)

    def saas_upload_report(self, compilation_id: str, report_type: str,
                           report: Dict) -> SaaSResult:
        data = {
            "values": report,
            "compilationId": compilation_id,
            "report_type": report_type
        }

        r = self._http_req(self.saas_upload_report, json=data)

        return SaaSResult(r)

    def saas_list_devices(self) -> SaaSResult:
        r = self._http_req(self.saas_list_devices)
        return SaaSResult(r)

    def prepare_model(self, model_path, dataset_path,
                      model_meta, dataset_meta) -> int:
        """ Upload a model and its corresponding calibration dataset.
            And create a compilation.

        :param str model:
            A path to a model file
        :param str dataset:
            A path to a model file
        :param Dict model_meta
            Metadata of the model
        :param Dict dataset_meta
            Metadata of the dataset
        :returns:
            internal compilation id
        :rtype:
            int
        """

        compilation = Compilation()
        compilation.model_path = model_path
        compilation.sample_path = dataset_path
        compilation.model_meta = model_meta
        compilation.sample_meta = dataset_meta

        _internal_cid = id(model_path)
        self._compilations[_internal_cid] = compilation
        return _internal_cid

    def calibrate(self, model_id: int, params: Dict):
        """Update calibration parameters
        """
        self._compilations[model_id].calibrator_params = params

    def compile(self, model_id, params: Dict):
        """Update compilation parameters
        """
        self._compilations[model_id].compiler_params = params

    def build(self, target: str, converter_params={}) -> Dict:

        saas_compilations = []

        # Upload files and create compilation
        for iternal_cid in self._compilations:
            compilation = self._compilations[iternal_cid]

            compilation.compiler_params['target'] = target

            params = {}
            params["model_meta"] = compilation.model_meta
            params["sample_meta"] = compilation.sample_meta
            params["compiler_params"] = compilation.compiler_params
            params["calibrator_params"] = compilation.calibrator_params
            params["converter_params"] = converter_params

            data = self._saas_create_compilation(compilation.model_path,
                                                 compilation.sample_path,
                                                 params)
            # saas_compilations.append(cr.data["id"])
            saas_compilations.append(data)

        # Create Build and trigger build/compilation
        build_sr = self.saas_create_build(project_id=self._project_id,
                                          saas_compilations=saas_compilations,
                                          device=target)
        if not build_sr:
            return build_sr.data

        self._build_id = build_sr.data["id"]

        logger.info(f"ONNC-SAAS BuildID: {self._build_id}")

        # Wait and poll the result
        t = 0
        spinner = spinning_cursor()
        sys.stdout.write("Building... ")
        while t < (timeout / poll_interval):
            t += 1

            # update spinner
            sys.stdout.write(next(spinner))
            sys.stdout.flush()
            sys.stdout.write('\b')
            time.sleep(poll_interval)

            state_sr = self.saas_get_build_state(build_sr.data["id"])

            # HTTP failure
            if not state_sr:
                logger.error(f"Something was wrong: {state_sr.data}")
                return state_sr.data

            # compilation is still running
            elif state_sr and (state_sr.data["state"] in ["pending",
                                                          "running"]):
                time.sleep(poll_interval)

            # compilation finishes
            else:
                if state_sr.data["state"] == "success":
                    logger.success(f"Compiled successfully.")
                    file_url = state_sr.data["output"]["deploymentPackage"]
                    logger.info(file_url)
                else:
                    logger.error(f"Compiled Unsuccessfully: {state_sr.data}")

                return state_sr.data

        logger.error(f"Compilation failed: Timeout")
        return {"error": {"message": "Timeout"},
                "id": self._build_id}

    def save(self, output: Path) -> Deployment:
        bs = self.saas_get_build_state(self._build_id)

        if bs.data["state"] == "success":
            file_url = bs.data["output"]["deploymentPackage"]

            file_ids = re.findall('files/(.*?)$', file_url)
            if len(file_ids) != 1:
                logger.error(f"Parse file_id error: {file_url}")
            else:
                file_id = file_ids[0]

            tmp_download = get_tmp_path() + '.zip'

            logger.info(tmp_download)

            self.saas_download_deployment_package(file_id, tmp_download)

            with zipfile.ZipFile(tmp_download, 'r') as zip_ref:
                zip_ref.extractall(output)

            deployment = Deployment(output)
        else:
            try:
                deployment = Deployment(None,
                                        bs.data["output"]["report"]["metrics"],
                                        bs.data["output"]["report"]["logs"])
            except KeyError:
                logger.error(f"Unable to parse SaaS result")
                logger.error(json.dumps(bs.data))
                deployment = Deployment(None, {}, [])

                return deployment

        return deployment

    @property
    def supported_devices(self) -> Dict:
        sr = self.saas_list_devices()
        devices = {x['name']: x['id'] for x in sr.data}
        return devices
