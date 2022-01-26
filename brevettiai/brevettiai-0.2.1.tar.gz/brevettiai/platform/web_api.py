import base64
import getpass
import json
import os
import re
import requests
import uuid
from urllib.parse import urlparse, unquote
from pydantic import BaseModel, PrivateAttr
from cryptography.fernet import Fernet, InvalidToken
from typing import ClassVar

from brevettiai.io.utils import IoTools
from brevettiai.platform import backend, PlatformBackend
from brevettiai.platform.platform_credentials import PlatformDatasetCredentials


class WebApiConfig(BaseModel):
    """Keeps track of web api setup"""
    secret: bytes = b''
    _config_file: ClassVar[str] = os.path.join(os.path.expanduser("~"), ".brevetti", "webapi")
    _modified: bool = PrivateAttr(default=False)

    @staticmethod
    def _get_fernet():
        """Retrieve Fernet module"""
        node = uuid.getnode()
        key = base64.urlsafe_b64encode(node.to_bytes(6, 'little') +
                                       b'Q\x19$v>8Lx\xbaQ\x86T\x06$\x91\x04x\x1a\xc7\xa5/\x83~\xe6+m')
        return Fernet(key)

    def set_credentials(self, username: str, password: str):
        """Set credentials for later retrieval"""
        self.secret = self._get_fernet().encrypt(f"{username}:{password}".encode())
        self._modified = True

    def get_credentials(self):
        """Get Username and password for platform login
        :return: username, password
        """
        try:
            return tuple(self._get_fernet().decrypt(self.secret).decode().split(":"))
        except InvalidToken as ex:
            raise ValueError("Invalid secret")

    @property
    def is_modified(self):
        """Is the configuration modified?"""
        return self._modified

    @staticmethod
    def load():
        """Load WebApiConfig from config_file"""
        return WebApiConfig.parse_file(WebApiConfig._config_file)

    def save(self):
        """Save WebApiConfig to config_file"""
        os.makedirs(os.path.dirname(WebApiConfig._config_file), exist_ok=True)
        with open(WebApiConfig._config_file, "w") as fp:
            fp.write(self.json())


class PlatformAPI:
    def __init__(self, username=None, password=None, host=None):
        self.host = host or backend
        self.session = requests.session()
        try:
            self.config = WebApiConfig().load()
        except IOError:
            self.config = WebApiConfig()
        self.user = self.login(username, password)
        self._io = IoTools()
        self._io.minio.credentials = PlatformDatasetCredentials(self)

    @property
    def host(self):
        return self._host.host if isinstance(self._host, PlatformBackend) else self._host

    @host.setter
    def host(self, host):
        self._host = host

    @property
    def backend(self):
        if isinstance(self._host, PlatformBackend):
            return self._host
        else:
            raise AttributeError("Backend unknown")

    def login(self, username, password):
        try:
            if username and password:
                self.config.set_credentials(username, password)
            else:
                username, password = self.config.get_credentials()
        except ValueError:
            if username is None:
                username = input(f"{self.host} - username: ")
            if password is None:
                password = getpass.getpass("Password:")
            self.config.set_credentials(username, password)

        res = self.session.post(self.host + "/api/account/token", data=dict(userName=username, password=password))
        if not res.ok:
            raise PermissionError(f"Could not log in: {res.reason}")

        data = res.json()
        if self.config.is_modified:
            answer = input("Persist login? y/n [n]")
            if answer.lower() == "y":
                self.config.save()
        return data

    def _http_get(self, url, headers=None, **kwargs):
        if headers is None:
            headers = self.antiforgery_headers

        r = self.session.get(url, headers=headers, **kwargs)
        if r.status_code == 401:
            raise PermissionError("Not authorized")
        return r

    def _http_post(self, url, headers=None, **kwargs):
        if headers is None:
            headers = self.antiforgery_headers

        r = self.session.post(url, headers=headers, **kwargs)
        if r.status_code == 401:
            raise PermissionError("Not authorized")
        return r

    def _http_delete(self, url, headers=None, **kwargs):
        if headers is None:
            headers = self.antiforgery_headers

        r = self.session.delete(url, headers=headers, **kwargs)
        if r.status_code == 401:
            raise PermissionError("Not authorized")
        return r

    @property
    def antiforgery_headers(self):
        """
        Get anti forgery headers from platform
        :return:
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + self.user['token']
        }
        r = self.session.get(self.host + "/api/account/antiforgery", headers=headers)
        return {**headers, 'X-XSRF-TOKEN': r.json()['requestToken']}

    def get_dataset(self, id=None, raw=False, write_access=False):
        """
        Get dataset, or list of all datasets
        :param id: guid of dataset (accessible from url on platform) or None for all dataset
        :param raw: get as dict, or attempt parsing to Criterion Dataset
        :return:
        """
        url = self.host + "/api/data"
        url = url if id is None else url + "/" + id
        r = self._http_get(url)

        if raw:
            return r.json()
        else:
            data = r.json()
            if isinstance(data, dict):
                return dataset_from_web(**data, io=self._io, resolve_access_rights=write_access)
            else:
                return [dataset_from_web(**ds, io=self._io, resolve_access_rights=write_access) for ds in data]

    def create_dataset(self, name, reference="", notes="", tag_ids=None, application=None):
        """
        Create dataset on platform
        :param name: Name of dataset
        :param tag_ids:
        :param application:
        :return:
        """
        payload = {
            'name': name,
            'tagIds': tag_ids,
            'reference': reference,
            'notes': notes,
        }
        if application is not None:
            payload["applicationId"] = application if isinstance(application, str) else application["id"]

        r = self._http_post(self.host + "/api/data/", json=payload)
        return r.json()

    def update_dataset(self, id, *, name: str, reference: str, notes: str, tags: list, locked: bool):
        """
        Update dataset on platform
        :param id: guid of dataset
        :param name: dataset name
        :param reference: dataset reference
        :param notes: dataset notes
        :param tags: list of tag ids (each represented by a string)
        :param locked: sets the lock status of the dataset
        :return:
        """

        r = self._http_post(self.host + "/api/data/" + id,
                            json={'name': name, "Reference": reference, "Notes": notes, 'tagIds': tags,
                                  "Locked": locked})
        return r

    def update_dataset_permission(self, id, userId, groupId=None, permissionType="Editor"):
        """
        Update dataset permissions for user
        :param id:
        :param userId:
        :param groupId:
        :param permissionType:
        :return:
        """
        payload = {"groupId": groupId, "userId": userId, "resourceId": id, "objectType": 0,
                   "permissionType": permissionType}
        r = self._http_post(self.host + "/api/admin/datasets/" + id + "/permissions", json=payload)
        return r

    def get_dataset_sts_assume_role_response(self, guid):
        cred = self._http_get(f"{self.host}/api/data/{guid}/securitycredentials")
        return cred.text

    def create_tag(self, name, parent_id=None):
        """
        Create a tag on the platform
        :param name:
        :param parent_id: guid of tag parent or none to create root tag
        :return:
        """
        payload = {
            'name': name,
        }
        if parent_id is not None:
            payload["parentId"] = parent_id

        r = self._http_post(+ "/api/resources/tags", json=payload)

        tag = next(filter(lambda x: x["name"] == name, self.get_tag(parent_id)['children']))
        return tag

    def get_tag(self, id=None):
        """
        Get tag or list of all tags
        :param id: tag guid
        :return:
        """
        url = self.host + "/api/resources/tags"
        url = url if id is None else url + "/" + id
        r = self._http_get(url)
        return r.json()

    def delete_tag(self, id):
        """
        Delete a tag by id
        :param id:
        :return:
        """
        url = self.host + "/api/resources/tags/" + id
        r = self._http_get(url)

    def get_model(self, id=None):
        """
        Get model or list of all models
        :param id: Guid of model (available in the url), or None
        :return:
        """
        url = self.host + "/api/models"
        url = url if id is None else url + "/" + id
        r = self._http_get(url)
        return r.json()

    def get_report(self, id=None):
        """
        Get test report, or list of all reports
        :param id: Guid of test report (available in the url), or None
        :return:
        """
        url = self.host + "/api/reports"
        url = url if id is None else url + "/" + id
        r = self._http_get(url)
        return r.json()

    def create_model(self, name, model_type, settings, datasets, tags=[], application=None):
        """
        Create new model
        :param name:
        :param model_type:
        :param settings:
        :param datasets:
        :param tags:
        :param application:
        :param schema:
        :return:
        """
        s_ = json.dumps(settings, sort_keys=True)

        payload = dict(
            name=name,
            modelTypeId=model_type if isinstance(model_type, str) else model_type["id"],
            settings=s_,
            tagIds=[x if isinstance(x, str) else x["id"] for x in tags],
            datasetIds=[x if isinstance(x, str) else x["id"] for x in datasets]
        )
        if application is not None:
            payload["applicationId"] = application if isinstance(application, str) else application["id"]
        r = self._http_post(self.host + "/api/models", json=payload)
        return r.json()

    def delete_model(self, id=None):
        """
        Get model or list of all models
        :param id: Guid of model (available in the url), or None
        :return:
        """
        url = self.host + "/api/models/" + id
        r = self._http_delete(url)
        return r

    def create_testreport(self, model_id, datasets):
        """
        Create new test report
        :param model_id:
        :param datasets:
        :return:
        """
        model_id = model_id if isinstance(model_id, str) else model_id["id"]
        url = self.host + "/api/models/{}/createtestreport".format(model_id)
        payload = dict(
            modelId=model_id,
            submitToGoogleCloud=True,
            datasetIds=[x if isinstance(x, str) else x["id"] for x in datasets]
        )
        r = self._http_post(url, json=payload)
        return r

    def get_artifacts(self, model_id, prefix='', type="models"):
        """
        Get artifacts for model or test report
        :param model_id: Guid of model/test report (available in the url)
        :param prefix:
        :param type: 'models' / 'reports'
        :return:
        """
        if type == "reports":
            r = self._http_get(self.host + "/api/reports/{}/artifacts?prefix={}".format(model_id, prefix))
        else:
            r = self._http_get(self.host + "/api/models/{}/artifacts?prefix={}".format(model_id, prefix))

        return r.json()

    def start_model_training(self, model, submitCloudJob=False):
        """
        Start training flow
        :param model: model or model id
        :param submitCloudJob: submit training to the cloud
        :return: updated model
        """
        r = self._http_post(
            self.host + "/api/models/{}/start".format(model if isinstance(model, str) else model["id"]),
            params={"submitToCloud": "true" if submitCloudJob else "false"})
        return r.json()

    def stop_model_training(self, model, submitCloudJob=False):
        """
        Stop training flow
        :param model: model or model id
        :param submitCloudJob: submit training to google cloud
        :return: updated model
        """
        r = self._http_post(
            self.host + "/api/models/{}/stop".format(model if isinstance(model, str) else model["id"]),
            params={"submitToCloud": "true" if submitCloudJob else "false"})
        return r.json()

    def get_modeltype(self, id=None):
        """
        Grt type of model
        :param id: model guid
        :return:
        """
        url = self.host + "/api/resources/modeltypes"
        url = url if id is None else url + "/" + id
        r = self._http_get(url)
        return r.json()

    def get_available_model_types(self):
        """
        List all available model types
        :return:
        """
        url = self.host + "/api/models/availabletypes"
        r = self._http_get(url)
        return r.json()

    def get_application(self, id=None, model_id=None):
        """
        Get application by id
        :param id: either application id or model id
        :return:
        """
        projects = self.get_project()
        ap_proj = next(({"ap": ap, "proj": proj} for proj in projects for ap in proj["applications"]
                        if ap["id"] == id or id in ap["modelIds"]))
        url = self.host + f"/api/resources/projects/{ap_proj['proj']['id']}/applications/{ap_proj['ap']['id']}/classification"
        r = self._http_get(url)
        return r.json()

    def get_devices(self, id=None):
        url = self.host + "/api/devices"
        url = url if id is None else url + "/" + id
        r = self._http_get(url)
        return r.json()

    def get_project(self, id=None):
        url = self.host + "/api/resources/projects"
        url = url if id is None else url + "/" + id
        r = self._http_get(url)
        return r.json()

    def get_schema(self, modeltype):
        """
        Get schema for a certain model type
        :param modeltype: model type or guid
        :return:
        """
        if isinstance(modeltype, str):
            modeltype = self.get_modeltype(modeltype)
        url = modeltype["settingsSchemaPath"]
        r = self._http_get(url, headers={})
        return r.json()

    def get_userinfo(self):
        """
        Get info on user
        :return:
        """
        url = self.host + "/api/manage/index"
        r = self._http_get(url)
        return r.json()

    def get_endpoint(self, endpoint, **kwargs):
        url = self.host + endpoint
        r = self._http_get(url, **kwargs)
        return r

    def get_sftp_user(self, dataset, **kwargs):
        if isinstance(dataset, dict):
            dsid = dataset["id"]
        else:
            dsid = dataset
        url = self.host + "/api/data/" + dsid + "/sftp"
        r = self._http_post(url, **kwargs)
        return r.json()

    def delete_sftp_user(self, dataset, user):
        if isinstance(dataset, dict):
            dsid = dataset["id"]
        else:
            dsid = dataset
        if isinstance(user, dict):
            userid = user["userName"]
        else:
            userid = user
        url = self.host + "/api/data/" + dsid + "/sftp/" + userid
        r = self._http_delete(url)
        return r

    def download_url(self, url, dst=None, headers=None):
        if url.startswith("/api/"):
            url = self.host + url

        r = self._http_get(url, stream=True, headers=headers)
        if r.status_code == requests.codes.ok:
            if dst is not None:
                if os.path.isdir(dst):
                    try:
                        d = r.headers['content-disposition']
                        fname = re.findall('filename="(.+)"', d)[0]
                    except:
                        fname = os.path.basename(unquote(urlparse(url).path))
                    assert fname is not ""
                    dst = os.path.join(dst, fname)
                else:
                    if os.path.dirname(dst):
                        os.makedirs(os.path.dirname(dst), exist_ok=True)
                with open(dst, 'wb') as f:
                    for data in r:
                        f.write(data)
            else:
                return r
        return dst


def dataset_from_web(id, name, folderName, tagIds, **kwargs):
    from brevettiai.platform import Dataset, backend
    return Dataset(
        id=id,
        name=name,
        bucket=f"{backend.data_bucket}/{folderName}",
        tags=tagIds,
        **kwargs
    )
