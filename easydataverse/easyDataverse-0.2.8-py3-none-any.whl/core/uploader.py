import os
import shutil
import requests

from typing import List, Optional

from pyDataverse.api import NativeApi
from pyDataverse.models import Dataset, Datafile
from easyDataverse.core.exceptions import MissingURLException, MissingCredentialsException


def upload_to_dataverse(
    json_data: str,
    dataverse_name: str,
    filenames: List[str] = None,
    p_id: str = None,
    DATAVERSE_URL: Optional[str] = None,
    API_TOKEN: Optional[str] = None
) -> str:
    """Uploads a given Dataset to the dataverse installation found in the environment variables.

    Args:
        json_data (str): JSON representation of the Dataverse dataset.
        dataverse_name (str): Name of the Dataverse where the data will be uploaded to.
        filenames (List[str], optional): List of files that should be uploaded. Can also include durectory names. Defaults to None.

    Raises:
        MissingURLException: URL to the dataverse installation is missing. Please include in your environment variables.
        MissingCredentialsException: API-Token to the dataverse installation is missing. Please include in your environment variables

    Returns:
        str: The resulting DOI of the dataset, if successful.
    """

    api = _initialize_pydataverse(DATAVERSE_URL, API_TOKEN)
    ds = Dataset()
    ds.from_json(json_data)

    # Finally, validate the JSON
    if ds.validate_json():
        if p_id:
            # Update dataset if pid given
            response = api.create_dataset(
                dataverse_name, json_data, p_id
            )
        else:
            # Create new if no pid given
            response = api.create_dataset(
                dataverse_name, json_data
            )

        if response.json()["status"] != "OK":
            raise Exception(response.json()["message"])

        # Get response data
        p_id = response.json()["data"]["persistentId"]

        if filenames is not None:
            # Upload files if given
            for filename in filenames:
                __uploadFile(
                    filename=filename,
                    p_id=p_id,
                    api=api
                )

        return p_id

    else:
        raise Exception("Could not upload")


def _initialize_pydataverse(
    DATAVERSE_URL: Optional[str],
    API_TOKEN: Optional[str]
):
    """Sets up a pyDataverse API for upload."""

    # Get environment variables
    if DATAVERSE_URL is None:
        try:
            DATAVERSE_URL = os.environ["DATAVERSE_URL"]

        except KeyError:
            raise MissingURLException

    if API_TOKEN is None:
        try:
            API_TOKEN = os.environ["DATAVERSE_API_TOKEN"]
        except KeyError:
            raise MissingCredentialsException

    return NativeApi(DATAVERSE_URL, API_TOKEN)


def __uploadFile(filename: str, p_id: str, api: NativeApi) -> None:
    """Uploads any file to a dataverse dataset.
    Args:
        filename (String): Path to the file
        p_id (String): Dataset permanent ID to upload.
        api (API): API object which is used to upload the file
    """

    # Check if its a dir
    if os.path.isdir(filename):
        shutil.make_archive("contents", 'zip', filename)
        filename = "contents.zip"

    df = Datafile()
    df.set({"pid": p_id, "filename": filename})
    api.upload_datafile(p_id, filename, df.json())


def update_dataset(
    p_id: str,
    json_data: dict,
    filenames: List[str] = None,
    DATAVERSE_URL: Optional[str] = None,
    API_TOKEN: Optional[str] = None
) -> bool:
    """Uploads and updates the metadata of a draft dataset.

    Args:
        p_id (str): Persistent ID of the dataset.
        json_data (dict): Dataverse JSON representation of the dataset.
    """

    url = f"{os.environ['DATAVERSE_URL']}/api/datasets/:persistentId/versions/:draft?persistentId={p_id}"
    response = requests.put(
        url,
        json=json_data,
        headers={"X-Dataverse-key": os.environ["DATAVERSE_API_TOKEN"]}
    )

    if filenames is not None:

        # Initialize pyDataverse API
        api = _initialize_pydataverse(
            DATAVERSE_URL, API_TOKEN
        )

        # Upload files if given
        for filename in filenames:
            __uploadFile(
                filename=filename,
                p_id=p_id,
                api=api
            )

    if response.json()["status"] != "OK":
        raise Exception(response.json()["message"])

    return True
