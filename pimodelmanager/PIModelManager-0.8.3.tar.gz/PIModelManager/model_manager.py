import importlib.metadata
import importlib.util
import io
import json
import logging
import mimetypes
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable, ClassVar, Dict, List, Union
from zipfile import ZipFile

import ray
import requests
from aioify import aioify
from fastapi.exceptions import HTTPException
from starlette.responses import JSONResponse
from ray import serve

from PIModelManager.pandora_model import PandoraModel

logger = logging.getLogger("ModelManager")
logger.setLevel(os.environ.get("LOG_LEVEL"))


class ModelManager:
    """Singleton class that manages ML models"""

    __instance: ClassVar[object] = None

    _config: ClassVar[Dict] = {}

    _credentials: ClassVar[Dict[str, str]] = {}
    _container: ClassVar[Union[str, None]] = None
    _login_url: ClassVar[Union[str, None]] = None
    _get_files_url: ClassVar[Union[str, None]] = None
    _download_file_url: ClassVar[Union[str, None]] = None
    _upload_file_url: ClassVar[Union[str, None]] = None
    _delete_file_url: ClassVar[Union[str, None]] = None

    _available_files: ClassVar[List[str]] = []
    _downloaded_models: ClassVar[List[PandoraModel]] = []

    _model_class_mapping: ClassVar[Dict[str, Callable]] = {}
    _tenant_configs: ClassVar[Dict] = {}
    _models: ClassVar[Dict] = {}
    _config_key: ClassVar[str] = ""

    def __init__(
        cls, config_key: str, model_class_mapping: Dict[str, Callable] = {}
    ) -> None:
        cls._model_class_mapping = model_class_mapping
        cls._config_key = config_key

    def __new__(cls, config_key: str = None):
        if ModelManager.__instance is None:

            ModelManager.__instance = object.__new__(cls)
            cls._busy = False
            if config_key:
                cls._config_key = config_key
            logger.info("__new__: setting model manager instance")
        else:
            logger.info("__new__: instance already exists")
        return ModelManager.__instance

    class BearerAuth(requests.auth.AuthBase):
        def __init__(self, token):
            self.token = token

        def __call__(self, r):
            r.headers["authorization"] = "Bearer " + self.token
            return r

    @classmethod
    def add_model_class_mapping(cls, model_name: str, class_instance: Callable) -> None:
        """ a function that adds a model mapping from a name to a Class """
        if model_name in cls._model_class_mapping:
            logger.info(
                f"{model_name} already taken but updating with new Class definition"
            )
        if not ray.is_initialized() and isinstance(
            class_instance, ray.serve.api.Deployment
        ):
            class_instance = class_instance._func_or_class
            logger.info(
                f"Ray is not initialized, reverting to default class instead of deployment."
            )
        cls._model_class_mapping[model_name] = class_instance
        cls._update_initialized_models()

    @classmethod
    def remove_model_class_mapping(cls, model_name: str) -> None:
        """ a function that removes a model mapping from a name to a Class """
        if model_name in cls._model_class_mapping:
            del cls._model_class_mapping[model_name]

    @classmethod
    def _update_initialized_models(cls) -> None:
        for tenant_name in cls._tenant_configs:
            for model_name in cls._tenant_configs[tenant_name]:
                if model_name in cls._model_class_mapping:
                    for language in cls._tenant_configs[tenant_name][model_name]:
                        config = cls._tenant_configs[tenant_name][model_name][language]
                        cls.download_model_from_config(config)
                        cls._initialize_model_from_config(config)
                else:
                    logger.info(
                        f"class mapping not present for model {model_name}")

    @classmethod
    def _remove_unused_models(cls) -> None:
        """ Check whether any of the models are no longer being used, if so, delete them from RAM """
        models_to_delete = []
        for model_name in cls._models:
            for language in cls._models[model_name]:
                for version_model in cls._models[model_name][language]:
                    used = False
                    for tenant_name in cls._tenant_configs:
                        try:
                            version_config = cls._tenant_configs[tenant_name][
                                model_name
                            ][language]["version"]
                            client = cls._tenant_configs[tenant_name][model_name][
                                language
                            ]["client"]
                            if version_config == version_model:
                                used = True
                                break
                        except:
                            continue
                    if not used:
                        model_path = cls.get_model_path(
                            language=language,
                            name=model_name,
                            client=client,
                            version=version_model,
                        )
                        shutil.rmtree(model_path)
                        models_to_delete.append(
                            [model_name, language, version_model])

        indices_to_be_deleted = []
        for model in models_to_delete:
            model_name, language, version = model

            # delete model from RAM locally and delete deployment from ray if present
            if isinstance(
                cls._model_class_mapping[model_name], ray.serve.api.Deployment
            ):
                name = f"{language}_{model_name}_{client}_{version}"
                serve.get_deployment(name).delete()

            del cls._models[model_name][language][version_model]

            for pandora_model in cls._downloaded_models:
                if (
                    (pandora_model.name == model_name)
                    and (pandora_model.language == language)
                    and (pandora_model.version == version)
                ):
                    indices_to_be_deleted.append(
                        cls._downloaded_models.index(pandora_model)
                    )
            logger.info(
                f"Deleting unused model {model_name} {language} {version} from RAM"
            )
        for idx in indices_to_be_deleted:
            del cls._downloaded_models[idx]

        # check for old ray models that ought to be deleted
        if ray.is_initialized():
            models = list(serve.list_deployments().keys())
            for entry in models:
                language, model_name, client, version = entry.split("_")
                used = False
                for tenant_name in cls._tenant_configs:
                    if model_name in cls._tenant_configs[tenant_name]:
                        if language in cls._tenant_configs[tenant_name][model_name]:
                            check_version = (
                                cls._tenant_configs[tenant_name][model_name][language][
                                    "version"
                                ]
                                == version
                            )
                            check_client = (
                                cls._tenant_configs[tenant_name][model_name][language][
                                    "client"
                                ]
                                == client
                            )
                            if check_version and check_client:
                                used = True
                                break
                if not used:
                    logger.info(f"Deleting deprecated ray deployment {entry}")
                    serve.get_deployment(entry).delete()

    @classmethod
    def _initialize_model_from_config(cls, config: Dict[str, str]) -> None:
        language, model_name, client, version = (
            config["language"],
            config["name"],
            config["client"],
            config["version"],
        )

        if not model_name in cls._models:
            cls._models[model_name] = {}
        if not language in cls._models[model_name]:
            cls._models[model_name][language] = {}
        if not version in cls._models[model_name][language]:
            cls._models[model_name][language][version] = {}

        if not cls._models[model_name][language][version]:
            name = f"{language}_{model_name}_{client}_{version}"
            if isinstance(
                cls._model_class_mapping[model_name], ray.serve.api.Deployment
            ):
                if name not in serve.list_deployments():
                    cls._model_class_mapping[model_name].options(
                        name=name, init_args=tuple([config])
                    ).deploy()
                deployment = serve.get_deployment(name)
                cls._models[model_name][language][version] = deployment.get_handle()
            else:
                cls._models[model_name][language][version] = cls._model_class_mapping[
                    model_name
                ](config)
            logger.info(
                f"Finished initializing {model_name} model with {config}")

    @classmethod
    def set_credentials(
        cls,
        grant_type: Union[str, None] = os.environ.get(
            "MODEL_MANAGER_GRANT_TYPE"),
        client_id: Union[str, None] = os.environ.get(
            "MODEL_MANAGER_CLIENT_ID"),
        client_secret: Union[str, None] = os.environ.get(
            "MODEL_MANAGER_CLIENT_SECRET"),
        scope: Union[str, None] = os.environ.get("MODEL_MANAGER_SCOPE"),
        container: Union[str, None] = os.environ.get(
            "MODEL_MANAGER_CONTAINER"),
        login_url: Union[str, None] = os.environ.get(
            "MODEL_MANAGER_LOGIN_URL"),
        get_files_url: Union[str, None] = os.environ.get(
            "MODEL_MANAGER_GET_FILES_URL"),
        download_file_url: Union[str, None] = os.environ.get(
            "MODEL_MANAGER_DOWNLOAD_FILE_URL"
        ),
        default_tenant_name: Union[str, None] = os.environ.get(
            "STS_APPLICATION_DEFAULT_TENANT_NAME"
        ),
    ) -> None:
        """Set credentials for the ModelManager. If args are empty, they are read from environment vars.

        Args:
            grant_type (str): Type of grant
            client_id (str): The consumer key
            client_secret (str): The consumer secret
            scope (str): The control scope
            container (str): The name of the storage container
            login_url (str): The sts login url
            get_files_url (str): The URL for getting a list of available files in a container. Put variables in curly brackets.
            download_file_url (str): The URL for downloading a specific file from a container. Put variables in curly brackets.
        """

        if not all(
            [
                grant_type,
                client_id,
                client_secret,
                scope,
                container,
                login_url,
                get_files_url,
                download_file_url,
                default_tenant_name,
            ]
        ):
            raise Exception("Missing environment variables.")

        cls._credentials = {
            "grant_type": grant_type,
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": scope,
        }

        cls._default_tenant_name = default_tenant_name
        cls._container = container
        cls._login_url = login_url
        cls._get_files_url = get_files_url
        cls._download_file_url = download_file_url
        cls._upload_file_url = f"{cls._get_files_url}/upload"
        cls._delete_file_url = f"{cls._get_files_url}" + "/{filename}"

    @classmethod
    def __authenticate(cls) -> str:
        """Authenticate with the server.

        Raises:
            HTTPException: in case the credentials are not previously set using 'set_credentials' method.
            HTTPException: in case the authentication with STS fails.

        Returns:
            str: Access token
        """
        if not cls._credentials or not cls._login_url:
            raise HTTPException(
                status_code=404,
                detail="Credentials not set. Use method set_credentials.",
            )

        # Authentication request
        response = requests.post(cls._login_url, data=cls._credentials)
        if response.ok:
            result = json.loads(response.text)

            return result["access_token"]
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"ModelManager authentication failed: {response.text}",
            )

    @classmethod
    def set_config(cls, path: str) -> None:
        """Set the models configuration

        Args:
            path (str): A Path to the json configuration file

        Raises:
            Exception: if the path does not exist
            Exception: if the configuration file is empty
        """
        if not Path(path).exists():
            raise Exception("Path does not exist.")

        with open(path) as f:
            config = json.load(f)
            if not config:
                raise Exception("Config file is empty.")

        for tenant_config in config:
            cls.add_tenant_config(cls._default_tenant_name, tenant_config)

    @classmethod
    def _config_has_changed(cls, token_info: Any) -> bool:
        return token_info.tenant_config[cls._config_key]["has_changed"]

    @classmethod
    def update_config_from_json(cls, token_info: Any, bg_task: Any = None):
        """updates the tenant config mapping if it isn't present or if it has changed.
        Afterwards, download the models, remove the unused models and update the initialized models.

        Args:
            token_info (Any): [description]
        """
        msg = JSONResponse(
            status_code=503, content={"message": "Update config: try again shortly."}
        )

        if cls._busy:
            msg = JSONResponse(
                status_code=503,
                content={
                    "message": "Updating and downloading models: this will take a couple of minutes."
                },
            )
            return msg

        tenant_name = token_info.tenant_name
        check_tenant_present = tenant_name in cls._tenant_configs
        check_has_changed = cls._config_has_changed(token_info)
        cls._check_validity_config(token_info)

        if check_tenant_present and check_has_changed:
            cls.remove_tenant_config(tenant_name)

        if check_has_changed or not check_tenant_present:
            if bg_task:
                bg_task.add_task(cls._apply_update, token_info)
                return msg
            else:
                cls._apply_update(token_info)

    @classmethod
    def _check_validity_config(cls, token_info):
        config = token_info.tenant_config[cls._config_key]["configurations"][
            "MODELS_JSON"
        ]
        required_keys = [
            "model_type",
            "download_scenario",
            "language",
            "name",
            "client",
            "version",
        ]
        for tenant_config in config:
            try:
                assert set(required_keys) == set(tenant_config.keys())
            except:
                msg = f"Config {tenant_config} does not contain required keys {required_keys}"
                logger.error(msg)
                raise HTTPException(400, detail=msg)

    @classmethod
    def _apply_update(cls, token_info):
        """A specific function for the potential background tast for updating

        Args:
            token_info ([type]): [description]
        """
        cls._busy = True
        try:
            tenant_name = token_info.tenant_name
            check_tenant_present = tenant_name in cls._tenant_configs
            check_has_changed = cls._config_has_changed(token_info=token_info)

            if check_has_changed or not check_tenant_present:
                config = token_info.tenant_config[cls._config_key]["configurations"][
                    "MODELS_JSON"
                ]
                for tenant_config in config:
                    cls.add_tenant_config(tenant_name, tenant_config)
                cls.download_models()
                cls._remove_unused_models()
                cls._update_initialized_models()
        except Exception as e:
            print(e)
            cls._busy = False
        cls._busy = False

    @classmethod
    def add_tenant_config(
        cls, tenant_name: Union[str, None], tenant_config: dict
    ) -> None:
        model_name, language = tenant_config["name"], tenant_config["language"]
        if not tenant_name in cls._tenant_configs:
            cls._tenant_configs[tenant_name] = {}
        if not model_name in cls._tenant_configs[tenant_name]:
            cls._tenant_configs[tenant_name][model_name] = {}
        if not language in cls._tenant_configs[tenant_name][model_name]:
            cls._tenant_configs[tenant_name][model_name][language] = {}
        cls._tenant_configs[tenant_name][model_name][language] = tenant_config
    import asyncio

    @classmethod
    async def get_model(
        cls,
        model_name: str,
        language: str,
        token_info: Any = {},
        path: bool = False,
        method: str = '__call__',
        **kwargs,
    ) -> Any:
        """Calls the function of a specific method for a specific initialized ModelManager class

        Args:
            model_name (str): name of the model it is getting
            language (str): language of the model it is retrieving
            token_info (Any, optional): token info/versioning the user is requesting. Defaults to {} == default tenant.
            path (bool, optional): if True, returns the path of the model. Defaults to False.
            method (str, optional): the class mapping method that ought to be called. Defaults to '__call__'.
            **kwargs (dic): a dictionary containing the potential arguments required for calling a method

        Raises:
            Exception: [description]
            HTTPException: [description]
            HTTPException: [description]

        Returns:
            Any: [description]
        """
        version = ""
        tenant_name = None
        client = ""
        if token_info:
            tenant_name = token_info.tenant_name

        try:
            version = cls._tenant_configs[tenant_name][model_name][language]["version"]
            client = cls._tenant_configs[tenant_name][model_name][language]["client"]
        except Exception as _:
            logger.warning(
                f"No tenant_config for {tenant_name}, {model_name}, {language}. Ask an administrator to set this within the App Config STS."
            )
            version = cls._tenant_configs[cls._default_tenant_name][model_name][
                language
            ]["version"]
            client = cls._tenant_configs[cls._default_tenant_name][model_name][
                language
            ]["client"]
            logger.warning(
                f"Using model for default tenant {cls._default_tenant_name} instead."
            )
        if path:
            return cls.get_model_path(
                language=language, name=model_name, client=client, version=version
            )
        else:
            try:
                model = cls._models[model_name][language][version]
                if model is None:
                    raise Exception
            except:
                msg = f"No initialized model for {model_name}, {language}, {version}"
                logger.warning(msg)
                raise HTTPException(status_code=404, detail=msg)
            try:
                if isinstance(
                    cls._model_class_mapping[model_name], ray.serve.api.Deployment
                ):
                    return await getattr(model, method).remote(**kwargs)
                else:
                    return await getattr(model, method)(**kwargs)
            except Exception as e:
                msg = repr(e)
                logger.warning(msg)
                raise HTTPException(status_code=404, detail=msg)

    @classmethod
    def remove_tenant_config(cls, tenant_name: str) -> None:
        if tenant_name in cls._tenant_configs:  # check if tenant already in config
            del cls._tenant_configs[tenant_name]

    @classmethod
    def download_models(cls) -> None:
        """Download all models described in a config.

        Raises:
            Exception: if the config file is invalid.
        """
        for tenant_name in cls._tenant_configs:
            for model_name in cls._tenant_configs[tenant_name]:
                for language in cls._tenant_configs[tenant_name][model_name]:
                    config = cls._tenant_configs[tenant_name][model_name][language]
                    cls.download_model_from_config(config)

    @classmethod
    def download_model_from_config(cls, config: Dict[str, str]) -> None:
        download_scenario = config.get("download_scenario", None)
        if download_scenario == "pip":
            if config["model_type"] == "spacy":
                cls.__download_model_pip(config)
            else:
                raise Exception(
                    f"Invalid config file - pip not supported for model type {config['model_type']}"
                )
        elif download_scenario == "dataservices":
            cls.__download_model_dataservices(config)
        else:
            raise Exception("Invalid config file - missing download scenario.")

    @classmethod
    def __download_model_pip(cls, model: Dict[str, str]) -> None:
        """Download a model as a pip package.

        Args:
            model (Dict[str, str]): model description from a config file

        Raises:
            Exception: if the config file is invalid.
        """

        if model["model_type"] == "spacy":
            name = model.get("name", None)
            version = model.get("version", None)

            if name and version:
                if cls.__pip_package_is_available(name, version):
                    logger.info(
                        f"Package {name}-{version} is already installed.")
                else:
                    package = name + "-" + version
                    url = f"https://github.com/explosion/spacy-models/releases/download/{package}/{package}.tar.gz"
                    logger.info(
                        f"Downloading package {name}-{version} from {url}")

                    # ensure the model is only downloaded on external cluster
                    class_instance = cls._model_class_mapping.get(name)
                    if isinstance(class_instance, ray.serve.api.Deployment):
                        logger.info(
                            f"Model {model} obtained through Ray deployment.")
                    else:
                        output = subprocess.run(
                            [sys.executable, "-m", "pip", "install", url],
                            env=os.environ.copy(),
                            encoding="utf8",
                        )

                        logger.info(f"Return code: {output.returncode}")
                        if output.returncode != 0:
                            raise Exception(
                                f"Error when installing package {package}")
                        else:
                            logger.info(
                                f"Successfully installed package: {package}")

                pandora_model = PandoraModel(
                    type=model["model_type"],
                    language=model["language"],
                    size=model["size"],
                    name=name,
                    client=model.get("client", "default"),
                    version=version,
                    path=Path(model.get("path", name)),
                )

                if pandora_model not in cls._downloaded_models:
                    cls._downloaded_models.append(pandora_model)
            else:
                raise Exception(
                    "Invalid config file - missing name and/or version fields."
                )
        else:
            Exception(
                f"Invalid config file - pip not supported for model type {model['model_type']}"
            )

    @classmethod
    def __pip_package_is_available(cls, name: str, version: str = None) -> bool:
        """Check if a pip package is already installed

        Args:
            name (str): name of the package
            version (str): version of the package

        Returns:
            bool: if the package is installed or not
        """

        try:
            if importlib.util.find_spec(name):
                if not version:
                    return True
                else:
                    if importlib.metadata.version(name) == version:
                        return True
        except Exception:
            return False

        return False

    @classmethod
    def __download_model_dataservices(cls, model: Dict[str, str]) -> None:
        """Download a model from dataservices.

        Args:
            model (Dict[str, str]): model description from a config file

        Raises:
            Exception: if the config file is invalid.
        """
        if not cls._credentials:
            raise Exception("Authentication credentials have not been set.")

        cls.__update_available_files()

        language = cls.__clean_str(model["language"])
        name = cls.__clean_str(model["name"])
        client = cls.__clean_str(model.get("client", "default"))
        version = cls.__clean_str(model["version"])

        query = "_".join([language, name, client, version]) + "."

        matched_models = [f for f in cls._available_files if query in f]
        if len(matched_models) == 0:
            raise Exception(
                f"Specified model {query} not found in dataservices.")
        elif len(matched_models) > 1:
            raise Exception(
                f"More than one models match the one provided in the config file: {query}."
            )
        else:
            filename = matched_models[0]
            extension = "".join(Path(filename).suffixes)

            if extension == ".zip":
                model_filename = filename.rstrip(extension)
                temp_path = Path(Path.cwd(), "models",
                                 language, name, client, version)
            else:
                model_filename = filename
                temp_path = Path(
                    Path.cwd(), "models", language, name, client, version, filename
                )

            pandora_model = PandoraModel(
                type=model["model_type"],
                language=language,
                size=model.get("size", None),
                name=name,
                client=client,
                version=version,
                path=None,
                filename=model_filename,
            )

            class_instance = cls._model_class_mapping.get(name)
            if temp_path.exists():
                # Update model object path and add to _downloaded_models
                if isinstance(class_instance, ray.serve.api.Deployment):
                    cls._downloaded_models.append(pandora_model)
                    logger.info(
                        f"Model {model} obtained through Ray deployment.")
                else:
                    pandora_model.path = temp_path
                    if pandora_model not in cls._downloaded_models:
                        cls._downloaded_models.append(pandora_model)
                        logger.info(f"Model already downloaded in {temp_path}")
            else:
                # Download the model and add to _downloaded_models
                if isinstance(class_instance, ray.serve.api.Deployment):
                    cls._downloaded_models.append(pandora_model)
                    logger.info(
                        f"Model {model} obtained through Ray deployment.")
                else:
                    logger.info(f"Downloading model in {temp_path}")
                    access_token = cls.__authenticate()
                    url = cls._download_file_url.replace(
                        "{container}", str(cls._container)
                    )
                    url = url.replace("{filename}", filename)
                    response = requests.get(
                        url, auth=cls.BearerAuth(access_token))

                    if response.ok:
                        dir = Path(
                            Path.cwd(),
                            "models",
                            pandora_model.language,
                            pandora_model.name,
                            pandora_model.client,
                            pandora_model.version,
                        )
                        dir.mkdir(parents=True, exist_ok=True)

                        if extension == ".zip":
                            zf = ZipFile(io.BytesIO(response.content), "r")

                            if not zf.namelist():
                                raise Exception(
                                    f"Zip file {filename} is empty.")

                            zf.extractall(dir)

                            pandora_model.path = dir
                            cls._downloaded_models.append(pandora_model)

                            logger.info(
                                f"Extracted model to: {pandora_model.path}")
                        else:
                            path = Path(dir, pandora_model.filename)

                            with open(path, "wb") as f:
                                f.write(response.content)

                            pandora_model.path = path
                            cls._downloaded_models.append(pandora_model)

                            logger.info(
                                f"Saved model to: {pandora_model.path}")

    @classmethod
    def __get_files(cls, token: str) -> List[str]:
        """Returns a list of available model files.

        Args:
            token (str): Authentication bearer token

        Returns:
            List[str]: List of all available model files
        """
        url = cls._get_files_url.replace("{container}", cls._container)
        response = requests.get(url, auth=cls.BearerAuth(token))
        # response.raise_for_status()
        if response.ok:
            return [dict(x)["name"] for x in json.loads(response.text)]
        else:
            return []

    @classmethod
    def __update_available_files(cls) -> None:
        """Updates the list of available files from dataservices."""

        access_token = cls.__authenticate()
        cls._available_files = cls.__get_files(access_token)

    @classmethod
    def get_model_path(cls, **kwargs) -> Path:
        """Finds the matching model based on the provided keyword arguments and returns its path.

        Raises:
            Exception: if more than one models are matching the provided arguments
            Exception: if no models are matching the provided arguments

        Returns:
            Path: the local model directory
        """

        matching_models = [
            x
            for x in cls._downloaded_models
            if all([getattr(x, attr) == value for (attr, value) in kwargs.items()])
        ]

        if len(matching_models) > 1:
            raise Exception(
                f"More than one models are matching your arguments: {kwargs}"
            )
        elif len(matching_models) == 1:
            return str(matching_models[0].path)
        else:
            raise Exception(f"No models are matching your arguments: {kwargs}")

    @staticmethod
    def __clean_str(s: str) -> str:
        """Cleans a string by replacing underscores and dots with hyphens

        Args:
            s (str): input string

        Returns:
            str: cleaned string
        """

        s = s.replace(".", "-").replace("_", "-").lower()
        return s

    @classmethod
    def upload_model(
        cls,
        path: Path,
        zip: bool,
        language: str,
        name: str,
        client: str,
        version: str,
    ) -> None:
        """Uploads a model to dataservices

        Args:
            path (Path): The local path to the model file or directory
            zip (bool): Whether to zip a model directory, or not (upload a file directly)
            language (str): Language of the model
            name (str): Name of the model
            client (str): The target client of the model
            version (str): Version of the model

        Raises:
            Exception: if the model path does not exist
        """
        if path.exists():
            filename = "_".join(
                map(cls.__clean_str, [language, name, client, version]))
            if zip:
                final_path = Path(shutil.make_archive(filename, "zip", path))
            else:
                extension = "".join(path.suffixes)
                final_path = path.rename(
                    Path(path.parent, f"{filename}{extension}"))

            mimetype = mimetypes.guess_type(final_path)[0]
            if not mimetype:
                mimetype = "multipart/form-data"

            access_token = cls.__authenticate()
            url = cls._upload_file_url.replace("{container}", cls._container)
            files = {"file": (final_path.name, open(
                final_path, "rb"), mimetype)}
            response = requests.post(
                url, auth=cls.BearerAuth(access_token), files=files
            )
            if response.ok:
                logger.info(f"Successfully uploaded file:\n {response.text}")
            else:
                logger.info(
                    f"Error with uploading: {response.status_code}, {response.text}"
                )
        else:
            raise Exception("Model path does not exist.")

    @classmethod
    def get_files(cls) -> List[str]:
        """Get a list of the latest available model files in dataservices

        Returns:
            List[str]: A list of filenames
        """

        cls.__update_available_files()
        return cls._available_files

    @classmethod
    def delete_file(cls, name: str) -> bool:
        """Delete a file from dataservices

        Args:
            name (str): name of the file (incl. file extension)

        Raises:
            Exception: if the delete method is not successful

        Returns:
            bool: whether the file was successfully deleted
        """

        files = cls.get_files()
        if name in files:
            access_token = cls.__authenticate()
            url = cls._delete_file_url.replace("{container}", cls._container)
            url = url.replace("{filename}", name)
            response = requests.delete(url, auth=cls.BearerAuth(access_token))

            if response.ok:
                return True
            else:
                raise Exception(
                    f"Error with deleting file {name}: {response.status_code}, {response.text}"
                )
        else:
            return False

    @classmethod
    def delete_models(cls) -> None:
        """Delete all downloaded and/or installed models from Memory."""

        for m in cls._downloaded_models:
            if not isinstance(m.path, Path):
                try:
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "uninstall", m.path, "-y"]
                    )
                    logger.info(f"Uninstalling {m.path}")
                except:
                    pass

        model_types = [m.type for m in cls._downloaded_models]
        if "allennlp" in model_types:
            if not cls.__pip_package_is_available("allennlp"):
                logger.warning(
                    "You have allennlp model, but allennlp package is missing. Not possible to delete cached allennlp models."
                )
            else:
                try:
                    from allennlp.common.file_utils import remove_cache_entries

                    cleaned_bytes = remove_cache_entries(patterns=[])
                    logger.info(
                        f"Removed {cleaned_bytes} bytes of cached allennlp models."
                    )
                except ImportError:
                    logger.warning(
                        "Could not import allennlp. Not possible to delete cached allennlp models."
                    )

        models_path = Path(Path.cwd(), "models")
        if models_path.exists():
            logger.info(f"Deleting downloaded models")
            shutil.rmtree(models_path)

        del cls._downloaded_models[:]
