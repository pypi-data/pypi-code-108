import re
import requests

from biolib import biolib_errors
from biolib.typing_utils import Optional
from biolib.biolib_api_client.auth import BearerAuth
from biolib.biolib_api_client import BiolibApiClient, AppGetResponse
from biolib.biolib_errors import BioLibError
from biolib.biolib_logging import logger


class BiolibAppApi:

    @staticmethod
    def get_by_uri(uri: str) -> AppGetResponse:
        # Replace protocol with @ (if supplied)
        uri = re.sub(r'^http(s)?://', '@', uri)
        # Replace frontend version path with app_uri compatible version (if supplied)
        uri = re.sub(r'/version/(?P<version>(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*))(/)?$', r':\g<version>', uri)

        response = requests.get(
            f'{BiolibApiClient.get().base_url}/api/app/',
            auth=BearerAuth(BiolibApiClient.get().access_token),
            params={'uri': uri},
            timeout=5,
        )

        if response.status_code == 404:
            raise biolib_errors.NotFound(f'Application {uri} not found.')

        if response.status_code == 400:
            raise biolib_errors.BioLibError(response.content.decode())

        if not response.ok:
            raise Exception(response.content.decode())

        app_response: AppGetResponse = response.json()
        return app_response

    @staticmethod
    def push_app_version(
        app_id,
        zip_binary,
        author,
        app_name,
        set_as_active,
        app_version_id_to_copy_images_from: Optional[str],
    ):
        response = requests.post(
            f'{BiolibApiClient.get().base_url}/api/app_versions/',
            files={
                'source_files_zip': zip_binary,
            },
            data={
                'app': app_id,
                'set_as_active': 'true' if set_as_active else 'false',
                'state': 'published',
                'app_version_id_to_copy_images_from': app_version_id_to_copy_images_from
            },
            auth=BearerAuth(BiolibApiClient.get().access_token)
        )
        if not response.ok:
            logger.error(f'Push failed for {author}/{app_name}:')
            raise BioLibError(response.text)

        # TODO: When response includes the version number, print the URL for the new app version
        logger.info(f'Successfully pushed app version for {author}/{app_name}.')
        return response.json()

    @staticmethod
    def update_app_version(app_version_id, data):
        response = requests.patch(
            f'{BiolibApiClient.get().base_url}/api/app_versions/{app_version_id}/',
            json=data,
            auth=BearerAuth(BiolibApiClient.get().access_token)
        )
        if not response.ok:
            logger.error(f'Failed to update app version {app_version_id}')
            raise BioLibError(response.text)

        return response.json()
