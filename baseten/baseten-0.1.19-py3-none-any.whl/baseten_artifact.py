import logging
import tarfile
import tempfile
from typing import List

import requests
from colorama import Fore, Style
from tqdm import tqdm

from baseten.baseten_deployed_model import BasetenDeployedModel
from baseten.common import api
from baseten.common.core import raises_api_error

logger = logging.getLogger(__name__)


class BasetenArtifact:
    """An artifact stored on the BaseTen backend"""
    def __init__(
        self,
        artifact_id: str,
        name: str = None,
        description: str = None,
        deleted: bool = False,
    ):
        if not artifact_id:
            raise ValueError("Must provide the artifact's id")

        self._id = artifact_id
        self._name = name
        self._description = description
        self._deleted = deleted

    def __repr__(self):
        attr_info = [f'id={self._id}']
        if self._deleted:
            attr_info.append('DELETED ON SERVER')
        if self._name:
            attr_info.append(f'name={self._name}')
        if self._description:
            attr_info.append(f'description={self._description}')

        info_str = '\n  '.join(attr_info)

        return f'BasetenArtifact<\n  {info_str}\n>'

    @raises_api_error
    def create_link(self, model_id: str = None, model_version_id: str = None):
        if not model_id and not model_version_id:
            raise ValueError('Either model_id or model_version_id must be provided.')
        if model_id and model_version_id:
            raise ValueError('Must provide either model_id or model_version_id; not both.')
        resp = api.create_artifact_link(self._id, model_id=model_id, model_version_id=model_version_id)
        logger.info('⛓ Successfully linked artifact ⛓')
        return resp

    @raises_api_error
    def links(self):
        links = api.artifact_links(self._id)
        return [
            BasetenDeployedModel(model_version_id=model_version_id)
            for model_version_id in links['model_version_ids']
        ] + [
            BasetenDeployedModel(model_id=model_id)
            for model_id in links['model_ids']
        ]

    @raises_api_error
    def url(self) -> str:
        # todo(alex): worth it to introduce a library to cache a TTL here?
        return api.artifact_url(self._id)

    @raises_api_error
    def download(self, target_directory: str):
        artifact_response = requests.get(self.url(), stream=True)
        logger.info('📁 Downloading artifact archive from BaseTen 📁')
        block_size = 1024  # 1 Kibibyte
        total_size_in_bytes = int(artifact_response.headers.get('content-length', 0))
        progress_bar = tqdm(
            total=total_size_in_bytes,
            unit='iB',
            unit_scale=True,
            bar_format="Download Progress: "
                       "{percentage:3.0f}%% |%s{bar:100}%s| {n_fmt}/{total_fmt}" % (Fore.BLUE, Fore.RESET)
        )

        temp_tgz = tempfile.NamedTemporaryFile(mode='w+b')
        for content in artifact_response.iter_content(block_size):
            temp_tgz.write(content)
            progress_bar.update(len(content))
        temp_tgz.file.seek(0)
        progress_bar.close()

        logger.info('🔮 Download successful!🔮')

        with tarfile.open(temp_tgz.name, 'r') as tar:
            tar.extractall(target_directory)
        logger.info(f'📁 Successfully extracted artifact to {target_directory} 📁')

    @raises_api_error
    def update(
        self,
        name: str = None,
        description: str = None,
        list_of_files: List[str] = None,
    ):
        s3_key = None
        artifact_name = name or self._name
        artifact_description = description or self._description
        if list_of_files:
            s3_key = api.serialize_artifact_to_s3(artifact_name, list_of_files)
        update_resp = api.update_artifact(self._id, artifact_name, artifact_description, s3_key)
        self._id = update_resp['id']
        self._name = update_resp['name']
        self._description = update_resp['description']

    @raises_api_error
    def delete(
        self,
    ):
        api.delete_artifact(self._id)
        self._deleted = True


@raises_api_error
def create_artifact(
    name: str,
    list_of_files: List[str],
    description: str = None,
    model_id: str = None,
    model_version_id: str = None,
):
    """Create an artifact in the BaseTen backend to track

        Args:
            name (str): The name of the artifact to be created.
            list_of_files (List[str]): A list of files to be uploaded.
            description (str, optional): An optional description of the artifact
            model_id (str, optional): A model_id to associate with the artifact
            model_version_id (str, optional): A model_version_id to associate with the artifact
        Returns:
            BasetenArtifact

        Raises:
            ApiError: If there was an error communicating with the server.
        """
    s3_key = api.serialize_artifact_to_s3(name, list_of_files)
    artifact_resp = api.create_artifact(
        s3_key,
        name,
        description=description,
        model_id=model_id,
        model_version_id=model_version_id
    )
    logger.info(
        f'Successfully stored {Fore.BLUE}{name}{Style.RESET_ALL} artifact with id {artifact_resp["artifact_id"]}.'
    )
    return BasetenArtifact(**artifact_resp)
