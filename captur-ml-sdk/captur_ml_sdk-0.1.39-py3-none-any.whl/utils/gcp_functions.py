import re
import json
import gcsfs

from google.cloud import aiplatform

from captur_ml_sdk.dtypes.exceptions import (
    ModelNotFoundError,
    ModelHasNoLiveVersionsError,
    VersionNotFoundError,
    VersionNotLiveError
)

def get_model_list_from_aiplatform():
    """Returns list of trained models with details"""
    api_endpoint = "us-central1-aiplatform.googleapis.com"
    client_options = {"api_endpoint": api_endpoint}
    client = aiplatform.gapic.ModelServiceClient(client_options=client_options)
    models = client.list_models(
        parent="projects/capturpwa/locations/us-central1")
    return models


def read_json_from_gcp_storage(file_path, project="capturpwa"):
    """
    Reads json from a file in GCP storage and returns as a dictionary.
    ----------------
    args:
        file_path (str) : location of the json file to be read
        project (str) : name of GCP project
            - default = "capturpwa"
    returns:
        data (dict) : data on model names and versions
            - format:
    {
        "<model1_name>": {
            "type": "classification",
            "model_versions": [
                {
                    "model_id": "<model_version_1_id>",
                    "dataset_id": "<dataset1_id>"
                },
                {
                    "model_id": "<model_version_2_id>",
                    "dataset_id": "<dataset2_id>"
                },
                {
                    "model_id": "<model_version_3_id>",
                    "dataset_id": "<dataset3_id>"
                },
            ]
        }
        "<model2_name>": {
            "type": "object_detection",
            "model_versions": [
                {
                    "model_id": "<model_version_1_id>",
                    "dataset_id": "<dataset1_id>"
                },
                {
                    "model_id": "<model_version_2_id>",
                    "dataset_id": "<dataset2_id>"
                }
            ]
        }
        "<model3_name>": {}
    }
    ----------------
    """
    gcs_file_system = gcsfs.GCSFileSystem(project)
    with gcs_file_system.open(file_path, "r") as f:
        data = json.loads(f.read())
    return data


def get_all_available_models(with_filter=None):
    """
    Returns a refined list of available models.
    ----------------
    args:
        with_filter : dict or None
            - example dict = {"model_display_name":"my_favourite_model"}
            default = None
    returns:
        all_model_dicts : list[dict]
            - each dict contains:
                "name",
                "display_name",
                "description",
                "create_time",
                "update_time"
    ----------------
    """
    models = get_model_list_from_aiplatform()

    all_model_dicts = []
    for model in models:
        attrs = ["name", "display_name", "description",
                 "create_time", "update_time"]
        m = {
            attr: model.__getattr__(attr) for attr in attrs
        }
        all_model_dicts += [m]

    if with_filter is not None:
        assert type(with_filter) is dict, "with_filter must be a dict"
        all_model_dicts = [
            item for item in all_model_dicts if all(item[k] == v for k, v in with_filter.items())
        ]

    return all_model_dicts


def check_specific_version_exists(model_name, model_version):
    """
    Checks whether a specific version of a model exists within GCP.
    ----------------
    args:
        model_name (str) : display name of the model
        model_version (str) : specific model version e.g. 4837405867162748509
    returns:
        specific_version_exists (bool)
    ----------------
    """
    filters = {
        "display_name": model_name,
        "name": f"projects/73629791501/locations/us-central1/models/{model_version}"
    }
    res = get_all_available_models(with_filter=filters)

    specific_version_exists = False

    if len(res) > 0:
        specific_version_exists = True

    return specific_version_exists


def get_list_of_versions_from_gcp(model_name):
    """
    Gets a list of model versions associated with a specific model display name.
    ----------------
    args:
        model_name (str) : display name of the model
    returns:
        model_versions_list (list) : list of existing model versions
    ----------------
    """
    model_data = read_json_from_gcp_storage(
        file_path="captur-ml/models/model_bank.json")
    if model_data.get(model_name):
        model_version_list = model_data.get(model_name).get("model_versions", [])
    else:
        model_version_list = []
    return model_version_list


def check_specific_version_is_live(live_versions, model_version):
    """
    Checks whether a specific version of a model is live.
    ----------------
    args:
        live_versions (list) : list of live versions from model_bank.json
        model_version (str) : specific model version e.g. 4837405867162748509
    returns:
        version_is_live (bool)
    ----------------
    """
    version_is_live = False
    for version in live_versions:
        if version.get("model_id") == model_version:
            version_is_live = True
    return version_is_live


def get_model_type_from_gcp(model_name):
    """
    Returns the type of a model.
    ----------------
    args:
        model_name (str) : display name of the model
    returns:
        model_type (str) : type of model, (currently only {"classification", "object_detection"})
    ----------------
    """
    model_data = read_json_from_gcp_storage(
        file_path="captur-ml/models/model_bank.json")
    try:
        return model_data.get(model_name).get("type")
    except AttributeError:
        raise ModelNotFoundError(f"{model_name} not found.")


def get_model_from_latest(model_version, list_of_model_versions):
    """
    Gets a model based on the model version including the term 'HEAD'.
    ----------------
    args:
        model_version (str) :
            "HEAD" returns latest model
            "HEAD~1" returns second latest model
            "HEAD~n" returns n+1th latest bar model
        list_of_model_versions (list) : list of available model versions
    returns:
        model information dictionary e.g. {model information dictionary}
    ----------------
    """
    model_version = model_version.split("~")

    if len(model_version) == 1:
        return list_of_model_versions[-1].get("model_id")

    model_countback = model_version[1]
    try:
        model_countback = int(model_countback) + 1
    except ValueError:
        return None

    if model_countback > len(list_of_model_versions):
        return None

    return list_of_model_versions[-model_countback].get("model_id")


def get_model_from_absolute_version(model_version, list_of_model_versions):
    """
    Gets a model based on the absolute model version, i.e. including term 'vN',
    e.g. v1 or v2 etc.
    ----------------
    args:
        model_version (str) :
            "v1" returns earliest model
            "v2" returns second earliest model
            "vN" returns Nth earliest model
        list_of_model_versions (list) : list of available model versions
    returns:
        model information dictionary e.g. {model information dictionary}
    ----------------
    """
    model_version = model_version.replace("v", "")

    try:
        model_version = int(model_version) - 1
    except ValueError:
        return None

    if model_version >= len(list_of_model_versions):
        return None

    return list_of_model_versions[model_version].get("model_id")


def get_requested_model_id(model_name: str, model_version: str):
    """
    Returns a refined list of available models.
    ----------------
    args:
        model_name (str): The name of the model e.g. "pipeline_practice_model"
        model_version (str): Something like:
            "HEAD",
            "v1",
            "4617869671822000128",
            "HEAD~1"

    returns:
        model version with model_id and dataset_id (dict) or False

    raises:
        ModelNotFoundError: raised if this model_name is not found
        VersionNotFoundError: raised if the model_name is found but the specified model_version is not
        ModelHasNoLiveVersionsError: raised if model_name exists but no live versions are present in the model bank file
        VersionNotLiveError: raised if model_name exists but version is not live (in the model bank)
    ----------------
    """

    if not get_all_available_models(with_filter={"display_name": model_name}):
        raise ModelNotFoundError(f"Model: {model_name} not found.")

    model_version_data = get_list_of_versions_from_gcp(model_name)

    if len(model_version_data) == 0:
        raise ModelHasNoLiveVersionsError(
            f"Model {model_name} exists but has no live version. "
            f"Please specifiy the version directly or deploy a live version."
        )

    if re.match("[0-9]{19}", model_version):
        model_id = model_version
        if not check_specific_version_is_live(model_version_data, model_id):
            raise VersionNotLiveError(
                f"{model_id} not found under {model_name} in model bank."
            )

    if re.match("^HEAD(~[1-9][0-9]*)?$", model_version):
        model_id = get_model_from_latest(
            model_version, model_version_data)

    if re.match("^v[1-9][0-9]*$", model_version):
        model_id = get_model_from_absolute_version(
            model_version, model_version_data)

    if model_id is None:
        raise VersionNotFoundError(
            f"Model {model_name} cannot get version {model_version}"
            f"because there are only {len(model_version_data)} live versions."
        )

    if not check_specific_version_exists(model_name, model_id):
        raise VersionNotFoundError(
            f"Model {model_name} exists but {model_id} not found."
        )

    return model_id


def check_file_exists(filepath):
    """Returns True if the file at filepath exists, else returns False."""
    if "gs://" in filepath:
        filepath = filepath.replace("gs://", "")
    gcs_file_system = gcsfs.GCSFileSystem()
    return gcs_file_system.exists(filepath)


def get_dataset_id_from_model_id(model_name, model_id):
    """
    Returns the id of the dataset used to train the model with id 'model_id'.
    ----------------
    args:
        model_id (str) : id of the model
    returns:
        dataset_id (str) : id of the dataset used to train the model
    ----------------
    """
    model_data = read_json_from_gcp_storage(
        file_path="captur-ml/models/model_bank.json")
    model_name_data = model_data.get(model_name)
    try:
        model_versions = model_name_data.get("model_versions")
    except AttributeError:
        raise ModelNotFoundError(f"Model {model_name} not found.")
    dataset_id = None
    for version in model_versions:
        if version.get("model_id") == model_id:
            dataset_id = version.get("dataset_id")
    return dataset_id
