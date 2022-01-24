"""
Description for seclea_ai.py
"""
import inspect
import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import pandas as pd
from pandas import DataFrame
from requests import Response
from seclea_utils.core import (
    CompressedFileManager,
    ModelManager,
    RequestWrapper,
    Zstd,
    decode_func,
    encode_func,
)
from seclea_utils.get_model_manager import Frameworks, get_model_manager

from seclea_ai.authentication import AuthenticationService
from seclea_ai.exceptions import AuthenticationError


def handle_response(res: Response, expected: int, msg: str) -> Response:
    """
    Handle responses from the server

    :param res: Response The response from the server.

    :param expected: int The expected HTTP status code (ie. 200, 201 etc.)

    :param msg: str The message to include in the Exception that is raised if the response doesn't have the expected
        status code

    :return: Response

    :raises: ValueError - if the response code doesn't match the expected code.

    """
    if not res.status_code == expected:
        raise ValueError(
            f"Response Status code {res.status_code}, expected:{expected}. \n{msg} - {res.reason} - {res.text}"
        )
    return res


class SecleaAI:
    def __init__(
        self,
        project_name: str,
        organization: str,
        platform_url: str = "https://platform.seclea.com",
        auth_url: str = "https://auth.seclea.com",
        username: str = None,
        password: str = None,
    ):
        """
        Create a SecleaAI object to manage a session. Requires a project name and framework.

        :param project_name: The name of the project

        :param platform_url: The url of the platform server. Default: "https://platform.seclea.com"

        :param auth_url: The url of the auth server. Default: "https://auth.seclea.com"

        :param username: seclea username

        :param password: seclea password

        :return: SecleaAI object

        :raises: ValueError - if the framework is not supported.

        Example::

            >>> seclea = SecleaAI(project_name="Test Project")
        """
        self._auth_service = AuthenticationService(RequestWrapper(auth_url))
        self._transmission = RequestWrapper(server_root_url=platform_url)
        self._auth_service.authenticate(self._transmission, username=username, password=password)
        self._project = None
        self._project_name = project_name
        self._organization = organization
        self._available_frameworks = {"sklearn", "xgboost", "lightgbm"}
        self._training_run = None
        self._cache_dir = os.path.join(Path.home(), f".seclea/{self._project_name}")
        self._init_project(project_name=project_name)
        print("success")

    def login(self, username=None, password=None) -> None:
        """
        Override login, this also overwrites the stored credentials in ~/.seclea/config.
        Note. In some circumstances the password will be echoed to stdin. This is not a problem in Jupyter Notebooks
        but may appear in scripting usage.

        :return: None

        Example::

            >>> seclea = SecleaAI(project_name="Test Project")
            >>> seclea.login()
        """
        success = False
        for i in range(3):
            try:
                self._auth_service.authenticate(
                    self._transmission, username=username, password=password
                )
                success = True
                break
            except AuthenticationError as e:
                print(e)
        if not success:
            raise AuthenticationError("Failed to login.")

    def upload_dataset(
        self,
        dataset: Union[str, List[str], DataFrame],
        dataset_name: str,
        metadata: Dict,
        parent: DataFrame = None,
        transformations: List[
            Union[Callable, Tuple[Callable, Optional[List], Optional[Dict]]]
        ] = None,
    ):
        """
        Uploads a dataset. Does not set the dataset for the session. Should be carried out before setting the dataset.

        :param dataset: Path or list of paths to the dataset or DataFrame containing the dataset. If a list then they must be split by row only and all
            files must contain column names as a header line.

        :param dataset_name: The name of the dataset.

        :param metadata: Any metadata about the dataset.

        :param parent: DataFrame The parent dataset this one derives from.

        :param transformations: A list of functions that preprocess the Dataset.
            These need to be structured in a particular way:
                [(<function name>, [<list of args>], {<dict of keyword arguments>}), ...] eg.
                [(test_function, [12, "testing"], {"test_argument": 23})] If there are no arguments or keyword arguments
                these may be omitted. Don't include the original Dataframe input as an argument. See the tutorial for more
                detailed information and examples.
        :return: None

        Example::

            >>> seclea = SecleaAI(project_name="Test Project")
            >>> seclea.upload_dataset(dataset="/test_folder/dataset_file.csv", dataset_name="Test Dataset", metadata={})

        Assuming the files are all in the /test_folder/dataset directory.
        Example with multiple files::

            >>> files = os.listdir("/test_folder/dataset")
            >>> seclea = SecleaAI(project_name="Test Project")
            >>> dataset_metadata = {"index": "TransactionID", "outcome_name": "isFraud", "continuous_features": ["TransactionDT", "TransactionAmt"]}
            >>> seclea.upload_dataset(dataset=files, dataset_name="Multifile Dataset", metadata=dataset_metadata)

        Example with DataFrame::

            >>> seclea = SecleaAI(project_name="Test Project")
            >>> dataset = pd.read_csv("/test_folder/dataset_file.csv")
            >>> dataset_metadata = {"index": "TransactionID", "outcome_name": "isFraud", "continuous_features": ["TransactionDT", "TransactionAmt"]}
            >>> seclea.upload_dataset(dataset=dataset, dataset_name="Multifile Dataset", metadata=dataset_metadata)
        """
        temp = False
        if self._project is None:
            raise Exception("You need to create a project before uploading a dataset")
        if isinstance(dataset, List):
            dataset, dataset_hash = self._aggregate_dataset(dataset)
            temp = True
        elif isinstance(dataset, DataFrame):
            if not os.path.exists(self._cache_dir):
                os.makedirs(self._cache_dir)
            temp_path = os.path.join(self._cache_dir, "temp_dataset.csv")
            dataset.to_csv(temp_path, index=False)
            dataset_hash = pd.util.hash_pandas_object(dataset).sum()
            dataset = temp_path
            temp = True
        else:
            dset = pd.read_csv(dataset, index_col=metadata["index"])
            dataset_hash = pd.util.hash_pandas_object(dset).sum()

        dataset_hash = hash(dataset_hash + self._project)

        dataset_queryparams = {
            "project": self._project,
            "organization": self._organization,
            "name": dataset_name,
            "metadata": json.dumps(metadata),
            "hash": str(dataset_hash),
            "parent": str(hash(pd.util.hash_pandas_object(parent).sum() + self._project))
            if parent is not None
            else None,
        }
        print("Query Params: ", dataset_queryparams)
        try:
            res = self._transmission.send_file(
                url_path="/collection/datasets",
                file_path=dataset,
                query_params=dataset_queryparams,
            )
            handle_response(res, 201, f"There was some issue uploading the dataset: {res.text}")
        finally:
            if temp:
                os.remove(dataset)

        if res.status_code == 201 and transformations is not None:
            # upload transformations.
            self._upload_transformations(
                transformations=self._process_transformations(transformations),
                dataset_pk=str(dataset_hash),
            )

    def upload_training_run(
        self,
        model,
        framework: Frameworks,
        dataset: DataFrame,
    ):
        """
        Takes a model and extracts the necessary data for uploading the training run.

        :param model: An ML Model instance. This should be one of {sklearn.Estimator, xgboost.Booster, lgbm.Boster}.

        :param framework: The framework being used. One of {"sklearn", "xgboost", "lgbm"}.

        :param dataset_name: The name of the Dataset, this is set upon Dataset upload.

        :return: None

        Example::

            >>> seclea = SecleaAI(project_name="Test Project")
            >>> dataset = pd.read_csv(<dataset_name>)
            >>> model = LogisticRegressionClassifier()
            >>> model.fit(X, y)
            >>> seclea.upload_training_run(
                    model,
                    framework=seclea_ai.Frameworks.SKLEARN,
                    dataset_name="Test Dataset",
                )
        """
        self._auth_service.authenticate(self._transmission)
        # check the dataset exists prompt if not
        dataset_pk = str(hash(pd.util.hash_pandas_object(dataset).sum() + self._project))

        model_name = model.__class__.__name__

        # check the model exists upload if not
        model_type_pk = self._set_model(model_name=model_name, framework=framework)

        # check the latest training run
        training_runs_res = self._transmission.get(
            "/collection/training-runs",
            query_params={
                "project": self._project,
                "model": model_type_pk,
                "organization": self._organization,
            },
        )
        training_runs = training_runs_res.json()

        # Create the training run name
        largest = -1
        for training_run in training_runs:
            num = int(training_run["name"].split(" ")[2])
            if num > largest:
                largest = num
        training_run_name = f"Training Run {largest + 1}"

        # extract params from the model
        params = framework.value.get_params(model)

        # upload training run
        tr_res = self._upload_training_run(
            training_run_name=training_run_name,
            model_pk=model_type_pk,
            dataset_pk=dataset_pk,
            params=params,
        )
        # if the upload was successful, add the new training_run to the list to keep the names updated.
        self._training_run = tr_res.json()["id"]

        # upload model state. TODO figure out how this fits with multiple model states.
        self._upload_model_state(
            model=model,
            training_run_pk=self._training_run,
            sequence_num=0,
            final=True,
            model_manager=get_model_manager(
                framework=framework, data_manager=CompressedFileManager(compression=Zstd())
            ),
        )

    def _init_project(self, project_name) -> None:
        """
        Initialises the project for the object. If the project does not exist on the server it will be created.

        :param project_name: The name of the project

        :return: None
        """
        self._project = self._get_project(project_name)
        if self._project is None:
            proj_res = self._create_project(project_name=project_name)
            try:
                self._project = proj_res.json()["id"]
            except KeyError:
                print(f"There was an issue: {proj_res.text}")
                resp = self._transmission.get(
                    url_path="/collection/projects", query_params={"name": project_name}
                )
                resp = handle_response(
                    resp, 200, f"There was an issue getting the project: {resp.text}"
                )
                self._project = resp.json()[0]["id"]

    def _get_project(self, project_name: str) -> Any:
        """
        Checks if a project exists on the server. If it does not it will return None otherwise the id of the project.

        :param project_name: str The name of the project.

        :return: int | None The id of the project else None.
        """
        project_res = self._transmission.get(
            url_path="/collection/projects",
            query_params={"name": project_name, "organization": self._organization},
        )
        handle_response(
            project_res, 200, f"There was an issue getting the projects: {project_res.text}"
        )
        if len(project_res.json()) == 0:
            return None
        return project_res.json()[0]["id"]

    def _create_project(self, project_name: str, description: str = "Please add a description.."):
        """
        Creates a new project.

        :param project_name: str The name of the project, must be unique within your Organisation.

        :param description: str Optional The description of the project. This has a default value that can be changed
            at a later date

        :return: Response The response from the server.

        :raises ValueError if the response status is not 201.
        """
        res = self._transmission.send_json(
            url_path="/collection/projects",
            obj={
                "name": project_name,
                "description": description,
                "organization": self._organization,
            },
            query_params={"organization": self._organization},
        )
        return handle_response(
            res, expected=201, msg=f"There was an issue creating the project: {res.text}"
        )

    def _set_model(self, model_name: str, framework: Frameworks) -> int:
        """
        Set the model for this session.
        Checks if it has already been uploaded. If not it will upload it.

        :param model_name: The name for the architecture/algorithm. eg. "GradientBoostedMachine" or "3-layer CNN".

        :return: int The model id.

        :raises: ValueError - if the framework is not one of the supported frameworks or if there is an issue uploading
         the model.

        Example::

            >>> seclea = SecleaAI(project_name="Test Project", framework="seclea_ai.Frameworks.SKLEARN")
            >>> seclea.set_model(model_name="GradientBoostingMachine")
        """
        res = handle_response(
            self._transmission.get(
                url_path="/collection/models",
                query_params={
                    "organization": self._organization,
                    "project": self._project,
                    "name": model_name,
                    "framework": framework.name,
                },
            ),
            expected=200,
            msg="There was an issue getting the model list",
        )
        models = res.json()
        if len(models) == 1:
            return models[0]["id"]
        # if we got here that means that the model has not been uploaded yet. So we upload it.
        res = self._upload_model(model_name=model_name, framework=framework)
        try:
            model_pk = res.json()["id"]
        except KeyError:
            resp = handle_response(
                self._transmission.get(
                    url_path="/collection/models",
                    query_params={
                        "organization": self._organization,
                        "project": self._project,
                        "name": model_name,
                        "framework": framework.name,
                    },
                ),
                expected=200,
                msg="There was an issue getting the model list",
            )
            model_pk = resp.json()[0]["id"]
        return model_pk

    def _upload_model(self, model_name: str, framework: Frameworks):
        """

        :param model_name:
        :param framework: instance of seclea_ai.Frameworks
        :return:
        """
        res = self._transmission.send_json(
            url_path="/collection/models",
            obj={
                "organization": self._organization,
                "project": self._project,
                "name": model_name,
                "framework": framework.name,
            },
            query_params={"organization": self._organization, "project": self._project},
        )
        return handle_response(
            res, expected=201, msg=f"There was an issue uploading the model: {res.text}"
        )

    def _upload_training_run(
        self, training_run_name: str, model_pk: int, dataset_pk: str, params: Dict
    ):
        """

        :param training_run_name: eg. "Training Run 0"
        :param params: Dict The hyper parameters of the model - can auto extract?
        :return:
        """
        if self._project is None:
            raise Exception("You need to create a project before uploading a training run")
        res = self._transmission.send_json(
            url_path="/collection/training-runs",
            obj={
                "organization": self._organization,
                "project": self._project,
                "dataset": dataset_pk,
                "model": model_pk,
                "name": training_run_name,
                "params": params,
            },
            query_params={"organization": self._organization, "project": self._project},
        )
        return handle_response(
            res, expected=201, msg=f"There was an issue uploading the training run: {res.text}"
        )

    def _upload_model_state(
        self,
        model,
        training_run_pk: int,
        sequence_num: int,
        final: bool,
        model_manager: ModelManager,
    ):
        os.makedirs(
            os.path.join(self._cache_dir, str(training_run_pk)),
            exist_ok=True,
        )

        save_path = model_manager.save_model(
            model,
            os.path.join(
                Path.home(), f".seclea/{self._project_name}/{training_run_pk}/model-{sequence_num}"
            ),
        )

        res = self._transmission.send_file(
            url_path="/collection/model-states",
            file_path=save_path,
            query_params={
                "organization": self._organization,
                "project": self._project,
                "sequence_num": sequence_num,
                "training_run": training_run_pk,
                "final_state": final,
            },
        )
        try:
            res = handle_response(
                res, expected=201, msg=f"There was an issue uploading a model state: {res.text}"
            )
        finally:
            os.remove(save_path)
        return res

    def _upload_transformations(
        self, transformations: List[Tuple[Callable, List, Dict]], dataset_pk
    ):
        responses = list()
        transformations = self._process_transformations(transformations)
        for idx, (trans, args, kwargs) in enumerate(transformations):
            # unpack transformations list
            data = {
                "name": trans.__name__,
                "code_raw": inspect.getsource(trans),
                "code_encoded": encode_func(trans, args, kwargs),
                "order": idx,
                "dataset": dataset_pk,
            }
            res = self._transmission.send_json(
                url_path="/collection/dataset-transformations",
                obj=data,
                query_params={"organization": self._organization, "project": self._project},
            )
            res = handle_response(
                res,
                expected=201,
                msg=f"There was an issue uploading the transformations on transformation {idx} with name {trans.__name__}: {res.text}",
            )
            responses.append(res)
        return responses

    def _load_transformations(self, training_run_pk: int):
        """
        Expects a list of code_encoded as set by upload_transformations.
        """
        res = self._transmission.get(
            url_path="/collection/dataset-transformations",
            query_params={"training_run": training_run_pk},
        )
        res = handle_response(
            res, expected=200, msg=f"There was an issue loading the transformations: {res.text}"
        )
        transformations = list(map(lambda x: x["code_encoded"], res.json()))
        return list(map(decode_func, transformations))

    def _aggregate_dataset(self, datasets: List[str]) -> Tuple[str, int]:
        """
        Aggregates a list of dataset paths into a single file for upload.
        NOTE the files must be split by row and have the same format otherwise this will fail or cause unexpected format
        issues later.
        :param datasets:
        :return:
        """
        loaded_datasets = [pd.read_csv(dset) for dset in datasets]
        aggregated = pd.concat(loaded_datasets, axis=0)
        if not os.path.exists(self._cache_dir):
            os.makedirs(self._cache_dir)
        # save aggregated and return path as string
        dset_hash = pd.util.hash_pandas_object(aggregated).sum()
        aggregated.to_csv(os.path.join(self._cache_dir, "temp_dataset.csv"), index=False)
        return os.path.join(self._cache_dir, "temp_dataset.csv"), dset_hash

    @staticmethod
    def _process_transformations(transformations: List) -> List[Tuple[Callable, List, Dict]]:
        for idx, trans_sig in enumerate(transformations):
            # if sig is iterable then first must be func, then one of: l | d | l,d   (list,dict)
            if hasattr(trans_sig, "__iter__"):
                # check too many args
                if len(trans_sig) > 3:
                    raise Exception(
                        f"Too many arguments for transformation exp: func,args,kwarg recieved: {trans_sig}"
                    )
                # check first arg is a function:
                if not isinstance(trans_sig[0], Callable):
                    raise Exception(
                        f"First argument in transformation must be the function received: {trans_sig}"
                    )

                if len(trans_sig) == 3:
                    if not (isinstance(trans_sig[1], list) and isinstance(trans_sig[2], dict)):
                        raise Exception(
                            f"transformation signature must be the function,list,dict received:"
                            f" {trans_sig} of type {[type(el) for el in trans_sig]}"
                        )
                    transformations[idx] = list(trans_sig)
                else:
                    if isinstance(trans_sig[1], list):
                        transformations[idx] = [*trans_sig, dict()]
                    elif isinstance(trans_sig[1], dict):
                        func, kwargs = trans_sig
                        transformations[idx] = [func, list(), kwargs]
                    else:
                        raise Exception(
                            f"transformation signature type error: {trans_sig[1]}  "
                            f"in {trans_sig} is not of type list or dict"
                        )
            elif isinstance(trans_sig, Callable):
                transformations[idx] = [trans_sig, list(), dict()]
            else:
                raise Exception(
                    f"transformation: {trans_sig} must be function or iterable, recieved:{type(trans_sig)} "
                )
        return transformations
